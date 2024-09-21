from django.shortcuts import render
from django.http import JsonResponse
from VNEDC.database import mes_database
from datetime import datetime, timedelta
import json
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from jobs.database import scada_database


def work_order_list(request):
    filters = []
    params = []

    # 获取当前日期和30天前的日期
    today = datetime.today()
    thirty_days_ago = today - timedelta(days=14)

    # 默认过滤条件：30天内的数据
    filters.append("InspectionDate BETWEEN %s AND %s")
    params.extend([thirty_days_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')])

    if 'Id' in request.GET and request.GET['Id']:
        filters.append("r.Id LIKE %s")
        params.append(f"%{request.GET['Id']}%")

    if 'InspectionDate' in request.GET and request.GET['InspectionDate']:
        filters.append("InspectionDate LIKE %s")
        params.append(f"%{request.GET['InspectionDate']}%")

    if 'Period' in request.GET and request.GET['Period']:
        filters.append("Period LIKE %s")
        params.append(f"%{request.GET['Period']}%")

    if 'WorkOrderId' in request.GET and request.GET['WorkOrderId']:
        filters.append("WorkOrderId LIKE %s")
        params.append(f"%{request.GET['WorkOrderId']}%")

    if 'WorkCenterTypeName' in request.GET and request.GET['WorkCenterTypeName']:
        filters.append("WorkCenterTypeName LIKE %s")
        params.append(f"%{request.GET['WorkCenterTypeName']}%")

    if 'MachineName' in request.GET and request.GET['MachineName']:
        filters.append("MachineName LIKE %s")
        params.append(f"%{request.GET['MachineName']}%")

    if 'LineName' in request.GET and request.GET['LineName']:
        filters.append("LineName LIKE %s")
        params.append(f"%{request.GET['LineName']}%")

    sql = """
    select InspectionDate,r.WorkOrderId,Period,r.Id,WorkCenterTypeName,MachineName,LineName,ProductItem,CustomerCode,
    CustomerName,CustomerPartNo,AQL,w.PlanQty,u.NormalizedUserName,FORMAT(r.CreationTime, 'yyyy/MM/dd HH:mm:ss') as CreationTime
    from [PMGMES].[dbo].[PMG_MES_RunCard] r
    LEFT JOIN [PMGMES].[dbo].[PMG_MES_WorkOrder] w on r.WorkOrderId = w.id
	LEFT JOIN [PMGMES].[dbo].[AbpUsers] u on r.CreatorUserId = u.Id
    """
    if filters:
        sql += " Where " + " AND ".join(filters)

    # 添加默认排序条件
    sql += " ORDER BY InspectionDate DESC, WorkOrderId"

    db = mes_database()
    work_orders = db.select_sql_dict_param(sql, params)

    return JsonResponse(work_orders, safe=False)


def runcard_detail(request):
    runcard = request.GET.get('runcard')
    sql = f"""
    select r.id,r.WorkOrderId,w.CustomerName,w.PartNo,w.ProductItem,q.OptionName,q.Upper_InspectionValue,
    q.InspectionValue,q.Lower_InspectionValue,q.InspectionStatus, q.InspectionUnit,q.DefectCode, FORMAT(q.CreationTime, 'yyyy/MM/dd HH:mm:ss') as CreationTime, u.Name
    from [PMGMES].[dbo].[PMG_MES_RunCard] r
    LEFT JOIN [PMGMES].[dbo].[PMG_MES_WorkOrder] w on r.WorkOrderId = w.id
    LEFT JOIN [PMGMES].[dbo].[PMG_MES_IPQCInspectingRecord] q on q.RunCardId = r.id
    LEFT JOIN [PMGMES].[dbo].[AbpUsers] u on q.CreatorUserId = u.Id
    where r.id = '{runcard}'
    """
    db = mes_database()
    results = db.select_sql_dict(sql)

    sql2 = f"""
    SELECT 
        LOT_NUMBER,
        DATA_ID,
        DATA_VAL,
        ROW_NUMBER() OVER (PARTITION BY LOT_NUMBER ORDER BY DATA_ID DESC ) AS rn
    FROM 
        TGM.dbo.MEASURE_DATA where LOT_NUMBER = '{runcard}'
    """
    measures = db.select_sql_dict(sql2)

    if measures:
        for result in results:
            if result['OptionName'] == "Roll":
                result['InspectionValue'] = str(result['InspectionValue']) + " (" + str(round(float(measures[4]['DATA_VAL']), 2))+ ")"
            elif result['OptionName'] == "Cuff":
                result['InspectionValue'] = str(result['InspectionValue']) + " (" + str(round(float(measures[3]['DATA_VAL']), 2)) + ")"
            elif result['OptionName'] == "Palm":
                result['InspectionValue'] = str(result['InspectionValue']) + " (" + str(round(float(measures[2]['DATA_VAL']), 2)) + ")"
            elif result['OptionName'] == "Finger":
                result['InspectionValue'] = str(result['InspectionValue']) + " (" + str(round(float(measures[1]['DATA_VAL'])/2, 3)) + ")"
            elif result['OptionName'] == "FingerTip":
                result['InspectionValue'] = str(result['InspectionValue']) + " (" + str(round(float(measures[0]['DATA_VAL'])/2, 3)) + ")"

    return JsonResponse(results, safe=False)


def ipqc_log(request):
    runcard = request.GET.get('runcard')
    OptionName = request.GET.get('OptionName')

    sql = f"""
    SELECT RunCardId,OptionName,InspectionValue,DefectCode,InspectionStatus,
    LogAction,FORMAT(CreationTime, 'yyyy/MM/dd HH:mm:ss') as CreationTime
    FROM [PMGMES].[dbo].[PMG_MES_IPQCInspectingRecord_Log] 
    where RunCardId = '{runcard}' and OptionName = '{OptionName}'"""

    db = mes_database()
    results = db.select_sql_dict(sql)

    return JsonResponse(results, safe=False)


def runcard_info(request):
    return render(request, 'mes/runcard.html')

def index(request):
    return render(request, 'mes/index.html')

def fast_check(request):
    today = str(datetime.today().strftime('%Y-%m-%d'))
    selected_date = today
    selected_machine = 'NBR'

    if request.method == 'POST':
        selected_date = request.POST.get('date', '')
        selected_machine = request.POST.get('machine', 'NBR')  # Get the selected machine, default to 'PVC' if not set

    sql1 = f"""
        WITH Machine AS (
        SELECT *
        FROM [PMGMES].[dbo].[PMG_DML_DataModelList] dl
        WHERE dl.DataModelTypeId = 'DMT000003'
    ),

    WorkOrderCheck AS (
        SELECT 
            dml.Id AS MachineID,
            dml.Name AS MachineName,
            wo.Id AS WorkOrderId,
            woi.LineId AS LineId,
            CASE 
                WHEN COUNT(wo.Id) OVER (PARTITION BY dml.Name) > 0 THEN 1 
                ELSE 0 
            END AS WorkOrderMode
        FROM 
            Machine dml
        LEFT JOIN 
            [PMGMES].[dbo].[PMG_MES_WorkOrder] wo 
            ON dml.Id = wo.MachineId
            AND wo.StartDate IS NOT NULL
            AND wo.StartDate BETWEEN CONVERT(DATETIME, '{selected_date} 05:30:00', 120) 
                            AND CONVERT(DATETIME, DATEADD(SECOND, -1, CONVERT(DATETIME, DATEADD(DAY, 1, '{selected_date}') + ' 05:30:00', 120)), 120)
        LEFT JOIN 
            [PMGMES].[dbo].[PMG_MES_WorkOrderInfo] woi 
            ON wo.Id = woi.WorkOrderId
        WHERE 
            dml.Name LIKE '%{selected_machine}%'
    )

    SELECT 
        MachineID,
        MachineName,
        WorkOrderId,
        LineId,
        WorkOrderMode
    FROM 
        WorkOrderCheck
    ORDER BY 
        MachineName;

    """
    sql2 = f"""
    select rc.MachineName, rc.LineName, rc.Period,rc.Id, ir.InspectionValue
    from [PMGMES].[dbo].[PMG_MES_RunCard]  rc
    left join [PMGMES].[dbo].[PMG_MES_IPQCInspectingRecord] ir
    on ir.RunCardId =  rc.Id and OptionName = 'Weight'
    where rc.MachineName like '%{selected_machine}%' 
    and ((rc.InspectionDate = '{selected_date}' and period between 6 and 23) 
    or ( rc.InspectionDate = DATEADD(DAY, 1, '{selected_date}') and period between 0 and 5))
    order by rc.machineName, rc.InspectionDate, Cast(rc.Period as Int)
    """
    sql3 = f"""
       WITH MachineWorkOrderRunCard AS (
        SELECT 
            dm.Name AS MES_MACHINE
        FROM 
            [PMGMES].[dbo].[PMG_DML_DataModelList] dm
        WHERE 
            dm.DataModelTypeId = 'DMT000003' 
            AND dm.Abbreviation LIKE '%{selected_machine}%'
    ),
    HourlyLineData AS (
        SELECT 
            cdm.MES_MACHINE,
            cdm.LINE,
            DATEPART(HOUR, cd.CreationTime) AS Hour,
            SUM(cd.qty2) AS HourlyQty
        FROM 
            [PMG_DEVICE].[dbo].[COUNTING_DATA_MACHINE] cdm
        JOIN 
            [PMG_DEVICE].[dbo].[COUNTING_DATA] cd
            ON cdm.COUNTING_MACHINE = cd.MachineName
        WHERE 
            cd.CreationTime BETWEEN CONVERT(DATETIME, '{selected_date} 06:00:00', 120) 
                              AND CONVERT(DATETIME, DATEADD(SECOND, -1, CONVERT(DATETIME, DATEADD(DAY, 1, '{selected_date}') + ' 06:00:00', 120)), 120)
            AND cd.MachineName LIKE '%{selected_machine}%'
            AND cd.MachineName LIKE '%CountingMachine%'
        GROUP BY 
            cdm.MES_MACHINE,
            cdm.LINE,
            DATEPART(HOUR, cd.CreationTime)
    ),
    AggregateData AS (
        SELECT 
            hld.MES_MACHINE,
            SUM(CASE WHEN hld.HourlyQty = 0 THEN 1 ELSE 0 END) AS ZeroCount,
            COUNT(*) AS TotalHours
        FROM 
            HourlyLineData hld
        GROUP BY 
            hld.MES_MACHINE
    )
    SELECT 
        mwr.MES_MACHINE,
        hld.Hour,
        MAX(CASE WHEN hld.LINE = 'A1' THEN hld.HourlyQty ELSE 0 END) AS A1_Qty,
        MAX(CASE WHEN hld.LINE = 'A2' THEN hld.HourlyQty ELSE 0 END) AS A2_Qty,
        MAX(CASE WHEN hld.LINE = 'B1' THEN hld.HourlyQty ELSE 0 END) AS B1_Qty,
        MAX(CASE WHEN hld.LINE = 'B2' THEN hld.HourlyQty ELSE 0 END) AS B2_Qty,
        CASE 
            WHEN ad.ZeroCount > 0 THEN 0
            WHEN ad.ZeroCount = 0 THEN 1
            ELSE NULL
        END AS QtyCheck,
        CASE 
            WHEN 
                (MAX(CASE WHEN hld.LINE = 'A1' THEN hld.HourlyQty ELSE 0 END) + 
                 MAX(CASE WHEN hld.LINE = 'A2' THEN hld.HourlyQty ELSE 0 END) + 
                 MAX(CASE WHEN hld.LINE = 'B1' THEN hld.HourlyQty ELSE 0 END) + 
                 MAX(CASE WHEN hld.LINE = 'B2' THEN hld.HourlyQty ELSE 0 END)) = 0 
            THEN 0
            ELSE 1
        END AS CellCheck
    FROM 
        MachineWorkOrderRunCard mwr
    LEFT JOIN 
        HourlyLineData hld
        ON mwr.MES_MACHINE = hld.MES_MACHINE
    LEFT JOIN 
        AggregateData ad
        ON mwr.MES_MACHINE = ad.MES_MACHINE
    GROUP BY 
        mwr.MES_MACHINE, 
        hld.Hour,
        ad.ZeroCount
    ORDER BY 
        mwr.MES_MACHINE,
        CASE 
            WHEN hld.Hour BETWEEN 6 AND 23 THEN hld.Hour - 5
            ELSE hld.Hour + 19
        END;
        """
    db = mes_database()
    results1 = db.select_sql_dict(sql1)
    results2 = db.select_sql_dict(sql2)
    results3 = db.select_sql_dict(sql3)

    machine_names = list(dict.fromkeys(list(results1_['MachineName'] for results1_ in results1)))
    work_orders, run_card_stop_hours, machines_data = [], [], []
    machine_data_totals, run_card_data, run_card_messages = [], [], []
    period_times = ['06', '07', '08', '09', '10', '11', '12', '13',
                    '14', '15', '16', '17', '18', '19', '20', '21',
                    '22', '23', '00', '01', '02', '03', '04', '05']
    for machine_name in machine_names:
        machine_name_count = 0
        for results1_ in results1:
            if machine_name == results1_['MachineName']:
                work_orders.append(results1_['WorkOrderMode'])
                break
        run_card_exist_hours = []
        for results2_ in results2:
            if machine_name == results2_['MachineName']:
                run_card_exist_hours.append(results2_['Period'])
        run_card_stop_hours.append(list(set(period_times) - set([f"{int(i):02}" for i in
                    list(dict.fromkeys(run_card_exist_hours)) if i is not None and f"{int(i):02}" in period_times])))
        machine_data_count = 0
        machine_data_total = 0
        for results3_ in results3:
            if machine_name == results3_['MES_MACHINE']:
                if machine_data_count == 0:
                    machines_data.append(results3_['QtyCheck'])
                    machine_data_count = 1
                machine_data_total += float(results3_['A1_Qty']) + float(results3_['A2_Qty']) + float(results3_['B1_Qty']) + float(results3_['B2_Qty'])
        machine_data_totals.append(machine_data_total)
    for index in range(len(run_card_stop_hours)):
        if len(run_card_stop_hours[index]) == 0:
            run_card_data.append(1)
            run_card_messages.append('Normal')
        elif len(run_card_stop_hours[index]) > 0:
            run_card_data.append(0)
            run_card_messages.append(f'Machine lost Runcard in: {len(run_card_stop_hours[index])} hour')
    for index in range(len(machines_data)):
        if machine_data_totals[index] == 0:
            machines_data[index] = 0

    run_card_messages_24 = [''] * (len(machine_names) * 24)
    run_card_mode_24 = [0] * (len(machine_names) * 24)
    run_card_messages_24_2 = [''] * (len(machine_names) * 24)
    run_card_mode_24_2 = [0] * (len(machine_names) * 24)
    run_card_messages_24_3 = [''] * (len(machine_names) * 24)
    run_card_mode_24_3 = [0] * (len(machine_names) * 24)
    for i, machine_name in enumerate(machine_names):
        for j, period_time in enumerate(period_times):
            found = False
            found2 = False
            found3 = False
            for results2_ in results2:
                if machine_name == results2_['MachineName']:
                    if results2_['Id'] is not None:
                        if float(results2_['Period']) == float(period_time):
                            run_card_mode_24[i * 24 + j] = 1
                            if run_card_messages_24[i * 24 + j] == '':
                                run_card_messages_24[i * 24 + j] = 'Runcard: at: '+ str(period_time) + ':00 ' + '<br>' + '&nbsp;&nbsp;&ndash;' + str(results2_['LineName'] + ': ' + results2_['Id'])
                            else:
                                run_card_messages_24[i * 24 + j] += '<br>' + '&nbsp;&nbsp;&ndash;' + f"{results2_['LineName']}: {results2_['Id']}"
                            found = True
                    if results2_['InspectionValue'] is not None:
                        if float(results2_['Period']) == float(period_time):
                            run_card_mode_24_2[i * 24 + j] = 1
                            if run_card_messages_24_2[i * 24 + j] == '':
                                run_card_messages_24_2[i * 24 + j] = 'Weight: at: '+ str(period_time) + ':00 ' + '<br>' + '&nbsp;&nbsp;&ndash;' + str(str(results2_['LineName']) + ': ' + str(results2_['InspectionValue']))
                            else:
                                run_card_messages_24_2[i * 24 + j] += '<br>' + '&nbsp;&nbsp;&ndash;' + f"{results2_['LineName']}: {results2_['InspectionValue']}"
                            found2 = True
            if not found:
                run_card_messages_24[i * 24 + j] = 'No Runcard'
            if not found2:
                run_card_messages_24_2[i * 24 + j] = 'No Weight Value'
            machines_data_total = 0
            machine_data_text = ''
            for results3_ in results3:
                machines_data_count = 0
                if machine_name == results3_['MES_MACHINE']:
                    if results3_['Hour'] is not None:
                        if float(results3_['Hour']) == float(period_time):
                            run_card_messages_24_3[i * 24 + j] = ('Machine: at: ' + str(results3_['Hour']) + ':00<br>'
                                                        + '&nbsp;&nbsp;&ndash; A1: ' + str(results3_['A1_Qty']) + '<br>'
                                                        + '&nbsp;&nbsp;&ndash; A2: ' + str(results3_['A2_Qty']) + '<br>'
                                                        + '&nbsp;&nbsp;&ndash; B1: ' + str(results3_['B1_Qty']) + '<br>'
                                                        + '&nbsp;&nbsp;&ndash; B2: ' + str(results3_['B2_Qty']))
                            if (float(results3_['A1_Qty']) + float(results3_['A2_Qty']) + \
                                float(results3_['B1_Qty']) + float(results3_['B2_Qty'])) > 0:
                                run_card_mode_24_3[i * 24 + j] = 1
                            found3 = True
            if not found3:
                run_card_messages_24_3[i * 24 + j] = 'No Machine Data'
    merged_messages, merged_data = [], []
    for i in range(0, (len(machine_names)*24), 24):
        merged_data.extend(run_card_mode_24[i:i + 24])
        merged_data.extend(run_card_mode_24_2[i:i + 24])
        merged_data.extend(run_card_mode_24_3[i:i + 24])
        merged_messages.extend(run_card_messages_24[i:i + 24])
        merged_messages.extend(run_card_messages_24_2[i:i + 24])
        merged_messages.extend(run_card_messages_24_3[i:i + 24])
    table_data1 = [merged_data[i:i + 24] for i in range(0, len(merged_data), 24)]
    table_data2 = [merged_messages[i:i + 24] for i in range(0, len(merged_messages), 24)]
    return render(request, 'mes/fast_check.html', locals())

def fast_check2(request):
    today = str(datetime.today().strftime('%Y-%m-%d'))
    selected_date = today
    selected_machine = 'PVC'

    if request.method == 'POST':
        selected_date = request.POST.get('date', '')
        selected_machine = request.POST.get('machine', 'PVC')  # Get the selected machine, default to 'PVC' if not set
    sql1 = f"""
        SELECT DISTINCT DeviceId
        FROM [PMG_DEVICE].[dbo].[OpticalDevice]
        WHERE DeviceId like '%{selected_machine}%'
        AND DeviceId like '%PVC1_L%'
        AND DeviceId like '%AOI%'
        Order by DeviceId
    """
    db = mes_database()
    results1 = db.select_sql_dict(sql1)
    device_id = []
    for result1 in results1:
        device_id.append(result1['DeviceId'])

    # Sort device IDs based on the numeric value after the underscore in the second position
    data = sorted(device_id, key=lambda x: int(x.split('_')[1][1:]))

    # Group the device IDs by their prefix (e.g., 'PVC1_L1')
    grouped_data = {}
    for item in data:
        prefix = "_".join(item.split('_')[:2])  # Extract the prefix 'PVC1_L1'
        if prefix not in grouped_data:
            grouped_data[prefix] = []
        grouped_data[prefix].append(item)

    # Modify the structure of device_id to include 'OKQty' and 'NGQty' for each device
    device_id = [
        [
            key,
            [[device, ['OKQty', 'NGQty']] for device in value]  # Add 'OKQty' and 'NGQty' to each device entry
        ]
        for key, value in grouped_data.items()
    ]

    period_times = ['06', '07', '08', '09', '10', '11', '12', '13',
                    '14', '15', '16', '17', '18', '19', '20', '21',
                    '22', '23', '00', '01', '02', '03', '04', '05']

    sql2 = f"""
        SELECT 
            DeviceId, 
            OKQty, 
            NGQty, 
            CONVERT(DATE, Cdt) AS [Date],                   
            DATEPART(HOUR, Cdt) AS [Hour],                  
            DATEPART(MINUTE, Cdt) AS [Minutes]     
        FROM 
            [PMG_DEVICE].[dbo].[OpticalDevice]
        WHERE 
            DeviceId LIKE '%_AOI%'
            AND DeviceId LIKE '%{selected_machine}%'
            AND Cdt BETWEEN CONVERT(DATETIME, '{selected_date} 06:00:00', 120) 
                        AND CONVERT(DATETIME, DATEADD(SECOND, -1, CONVERT(DATETIME, DATEADD(DAY, 1, '{selected_date}') + ' 06:00:00', 120)), 120)
        ORDER BY 
            DeviceId, Cdt;
    """
    results2 = db.select_sql_dict(sql2)

    kq = []
    kq2 = []
    min = []
    # Extract unique device IDs from results
    for device in data:
        data_on_day = []
        data_on_day2 = []
        min_on_day = []
        for period in period_times:
            data_on_hour = []
            data_on_hour2 = []
            min_on_hour = []
            # Filter results for current device and hour
            matching_results = [result for result in results2 if
                                result['DeviceId'] == device and float(period) == float(result['Hour'])]

            if matching_results:
                # Append OKQty values if the period exists in results
                data_on_hour.extend(result['OKQty'] for result in matching_results)
                data_on_hour2.extend(result['NGQty'] for result in matching_results)
                min_on_hour.extend(result['Minutes'] for result in matching_results)
            else:
                # Append a list with 12 zeros if the period is missing
                data_on_hour = [0]
                data_on_hour2 = [0]
                min_on_hour = [0]
            data_on_day.append(data_on_hour)
            data_on_day2.append(data_on_hour2)
            min_on_day.append(min_on_hour)
        kq.append(data_on_day)
        kq2.append(data_on_day2)
        min.append(min_on_day)
    status_OKQty = []
    status_NGQty = []
    for sub_kq in kq:
        for sub_sub_kq in sub_kq:
            mode = 1
            sum_value = sum(sub_sub_kq)
            for value in sub_sub_kq:
                if sum_value == 0:
                    mode = 0
                else:
                    if value == 0:
                        mode = 2
            status_OKQty.append(mode)

    status_OKQty = []
    for sub_kq in kq:
        for sub_sub_kq in sub_kq:
            mode = 1
            sum_value = sum(sub_sub_kq)
            len_value = len(sub_sub_kq)
            check_zero = 0
            if str(selected_date) == today:
                if len_value < 2:
                    mode = 7
                else:
                    if 0 in sub_sub_kq:
                        check_zero = 1
                    if sum_value == 0 and check_zero == 1:
                        mode = 1
                    elif sum_value > 0:
                        if check_zero == 0:
                            if sum_value < 200*len_value:
                                mode = 2
                            elif sum_value >= 200*len_value:
                                if any(sub_sub_sub_kq < 200 for sub_sub_sub_kq in sub_sub_kq):
                                    mode = 6
                                else:
                                    mode = 3
                        elif check_zero == 1:
                            if any(sub_sub_sub_kq > 200 for sub_sub_sub_kq in sub_sub_kq):
                                mode = 5
                            else:
                                mode = 4
            else:
                if 0 in sub_sub_kq:
                    check_zero = 1
                if sum_value == 0 and check_zero == 1:
                    mode = 1
                elif sum_value > 0:
                    if check_zero == 0:
                        if sum_value < 200 * len_value:
                            mode = 2
                        elif sum_value >= 200 * len_value:
                            if any(sub_sub_sub_kq < 200 for sub_sub_sub_kq in sub_sub_kq):
                                mode = 6
                            else:
                                mode = 3
                    elif check_zero == 1:
                        if any(sub_sub_sub_kq > 200 for sub_sub_sub_kq in sub_sub_kq):
                            mode = 5
                        else:
                            mode = 4

            status_OKQty.append(mode)

    for sub_kq2 in kq2:
        for sub_sub_kq2 in sub_kq2:
            mode2 = 1
            sum_value2 = sum(sub_sub_kq2)
            len_value2 = len(sub_sub_kq2)
            if str(selected_date) == today:
                if len_value2 < 2:
                    mode2 = 77
                elif len_value2 >= 2:
                    if sum_value2 == 0 or any(sub_sub_sub_kq2 > 200 for sub_sub_sub_kq2 in sub_sub_kq2):
                        mode2 = 11
                    else:
                        mode2 = 22
            else:
                if sum_value2 == 0 or any(sub_sub_sub_kq2 > 200 for sub_sub_sub_kq2 in sub_sub_kq2):
                    mode2 = 11
                else:
                    mode2 = 22
            status_NGQty.append(mode2)

    # print(status_OKQty)
    table_data1 = [status_OKQty[i:i + 24] for i in range(0, len(status_OKQty), 24)]
    table_data2 = kq
    table_data3 = []
    for i in range(24):
        table_data3.append(period_times)
    table_data4 = min
    merged_status, merged_kq = [], []
    for i in range(0, (len(data)*24), 24):
        merged_status.extend(status_OKQty[i:i + 24])
        merged_status.extend(status_NGQty[i:i + 24])
    table_data11 = [merged_status[i:i + 24] for i in range(0, len(merged_status), 24)]
    table_data22 = [item for pair in zip(kq, kq2) for item in pair]
    table_data1 = table_data11
    table_data2 = table_data22
    table_data3 = table_data3*2
    table_data4 = table_data4*2

    return render(request, 'mes/fast_check2.html', locals())

import os
def agent_storage(request):
    factoryList = ['GiangDien', 'LongKhanh', 'LongThanh']
    GiangDien = []
    LongKhanh = []
    LongThanh = []
    files = os.listdir('mes/storage')
    for file in files:
        data_temp = []
        with open(f'mes/storage/{file}', 'r') as data_file:
            data = data_file.read()
            data_temp.append(data)
        if "GiangDien" in (data.split(',')[0]):
            GiangDien.append(data_temp)
        elif "LongKhanh" in (data.split(',')[0]):
            LongKhanh.append(data_temp)
        elif "LongThanh" in (data.split(',')[0]):
            LongThanh.append(data_temp)
    sGiangDien = []
    sLongKhanh = []
    sLongThanh = []
    for item in GiangDien:
        disk = []
        disk_info = []
        info = str(item).split(',')
        for value in info:
            if 'Client:' in value:
                disk.append(value)
            if 'IP:' in value:
                disk.append(value)
            if 'Port:' in value:
                disk.append(value)
            if 'Disk' in value:
                disk.append(value)
            if '_Used' in value:
                disk.append(value)
        for value in info:
            if '_Code' in value:
                disk.append(value)
        for i in range(0, 3, 1):
            disk_info.append(disk[i])
        for i in range(3, len(disk), 2):
            sublist = disk[i:i + 2]
            disk_info.append(sublist)
        sublist = ['RAM']
        for value in info:
            if 'RAM_Total' in value:
                sublist.append(value)
        disk_info.append(sublist)
        sGiangDien.append(disk_info)
    for item in LongKhanh:
        disk = []
        disk_info = []
        info = str(item).split(',')
        for value in info:
            if 'Client:' in value:
                disk.append(value)
            if 'IP:' in value:
                disk.append(value)
            if 'Port:' in value:
                disk.append(value)
            if 'Disk' in value:
                disk.append(value)
            if '_Used' in value:
                disk.append(value)
        for value in info:
            if '_Code' in value:
                disk.append(value)
        for i in range(0, 3, 1):
            disk_info.append(disk[i])
        for i in range(3, len(disk), 2):
            sublist = disk[i:i + 2]
            disk_info.append(sublist)
        sublist = ['RAM']
        for value in info:
            if 'RAM_Total' in value:
                sublist.append(value)
        disk_info.append(sublist)
        sLongKhanh.append(disk_info)
    for item in LongThanh:
        disk = []
        disk_info = []
        info = str(item).split(',')
        for value in info:
            if 'Client:' in value:
                disk.append(value)
            if 'IP:' in value:
                disk.append(value)
            if 'Port:' in value:
                disk.append(value)
            if 'Disk' in value:
                disk.append(value)
            if '_Used' in value:
                disk.append(value)
        for value in info:
            if '_Code' in value:
                disk.append(value)
        for i in range(0, 3, 1):
            disk_info.append(disk[i])
        for i in range(3, len(disk), 2):
            sublist = disk[i:i + 2]
            disk_info.append(sublist)
        sublist = ['RAM']
        for value in info:
            if 'RAM_Total' in value:
                sublist.append(value)
        disk_info.append(sublist)
        sLongThanh.append(disk_info)
    ssGiangDien = []
    ssLongKhanh = []
    ssLongThanh = []
    for i in range(len(sGiangDien)):
        color = sGiangDien[i][5]
        sub_ssGiangDien = ['green']
        for index, color_mode in enumerate(color):
            color_code = color_mode.split(':')[-1]
            if 'red' in color_code:
                sub_ssGiangDien[0] = 'red'
        sub_ssGiangDien.append(((sGiangDien[i][2]).split(':')[-1]).replace(' ', ''))
        sub_ssGiangDien.append(((sGiangDien[i][0]).split(':')[-1]).replace(' ', ''))
        sub_ssGiangDien.append(((sGiangDien[i][1]).split(':')[-1]).replace(' ', ''))
        disk_size = sGiangDien[i][3:len(sGiangDien[i]) - 2]
        disk_info = []
        for disk in disk_size:
            for item in disk:
                disk_info.append(item.split(':')[1].replace(' ', ''))
        disk_info.extend(['RAM', (sGiangDien[i][-1])[-1].split(':')[-1].replace(' ', '')])
        sub_ssGiangDien.append(disk_info)
        ssGiangDien.append(sub_ssGiangDien)
    for i in range(len(sLongKhanh)):
        color = sLongKhanh[i][5]
        sub_ssGiangDien = ['green']
        for index, color_mode in enumerate(color):
            color_code = color_mode.split(':')[-1]
            if 'red' in color_code:
                sub_ssGiangDien[0] = 'red'
        sub_ssGiangDien.append(((sGiangDien[i][2]).split(':')[-1]).replace(' ', ''))
        sub_ssGiangDien.append(((sGiangDien[i][0]).split(':')[-1]).replace(' ', ''))
        sub_ssGiangDien.append(((sGiangDien[i][1]).split(':')[-1]).replace(' ', ''))
        disk_size = sGiangDien[i][3:len(sGiangDien[i]) - 2]
        disk_info = []
        for disk in disk_size:
            for item in disk:
                disk_info.append(item.split(':')[1].replace(' ', ''))
        disk_info.extend(['RAM', (sGiangDien[i][-1])[-1].split(':')[-1].replace(' ', '')])
        sub_ssGiangDien.append(disk_info)
        ssLongKhanh.append(sub_ssGiangDien)
    for i in range(len(sLongThanh)):
        color = sLongThanh[i][5]
        sub_ssGiangDien = ['green']
        for index, color_mode in enumerate(color):
            color_code = color_mode.split(':')[-1]
            if 'red' in color_code:
                sub_ssGiangDien[0] = 'red'
        sub_ssGiangDien.append(((sGiangDien[i][2]).split(':')[-1]).replace(' ', ''))
        sub_ssGiangDien.append(((sGiangDien[i][0]).split(':')[-1]).replace(' ', ''))
        sub_ssGiangDien.append(((sGiangDien[i][1]).split(':')[-1]).replace(' ', ''))
        disk_size = sGiangDien[i][3:len(sGiangDien[i]) - 2]
        disk_info = []
        for disk in disk_size:
            for item in disk:
                disk_info.append(item.split(':')[1].replace(' ', ''))
        disk_info.extend(['RAM', (sGiangDien[i][-1])[-1].split(':')[-1].replace(' ', '')])
        sub_ssGiangDien.append(disk_info)
        ssLongThanh.append(sub_ssGiangDien)
    return render(request, 'mes/agent_storage.html', locals())

import time
def machine_status(request):
    start_time = time.time()
    execution_time = 0

    current_date = datetime.today().strftime('%Y-%m-%d')
    current_month = datetime.today().strftime('%Y-%m')
    current_hour = datetime.today().strftime('%H')
    selected_date = current_date
    selected_machine = 'NBR'

    if request.method == 'POST':
        selected_date = request.POST.get('date', '')
        selected_machine = request.POST.get('machine', 'PVC')
    sql1 = f"""
            WITH LatestRecords AS (
                SELECT 
                    DISTINCT(MachineName),
                    Speed,
                    CreationTime,
                    ROW_NUMBER() OVER (PARTITION BY MachineName ORDER BY CreationTime DESC) AS RowNum
                FROM 
                    [PMG_DEVICE].[dbo].[COUNTING_DATA]
                WHERE 
                    CreationTime BETWEEN CONVERT(DATETIME, '{current_month}-01 00:00:00', 120) 
                                      AND CONVERT(DATETIME, '{current_date} 23:59:59', 120) 
                    AND MachineName like '%{selected_machine}%'
            )
            SELECT 
                MachineName,
                Speed,
                CAST(CreationTime AS DATE) AS Date,
                DATEPART(HOUR, CreationTime) AS Hour,
                DATEPART(MINUTE, CreationTime) AS Minute
            FROM 
                LatestRecords
            ORDER BY
                MachineName,
                CreationTime
                """

    if str(selected_date) == str(current_date):
        db = mes_database()
        results = db.select_sql_dict(sql1)  # results1
        machine_line_names = {}  # result = {}
        day_none_speed_minutes_counts = {}  # none_speed_counts = {}
        day_none_speed_minutes_hours = {}  # none_speed_times = {}
        month_none_speed_minutes = {}  # none_speed_month = {}
        for entry in results:
            machine_name = entry['MachineName']
            speed = entry['Speed']
            if machine_name not in machine_line_names:
                machine_line_names[machine_name] = []
                month_none_speed_minutes[machine_name] = 0
            machine_line_names[machine_name].append(speed)
            if entry['Speed'] is None:
                month_none_speed_minutes[machine_name] += 5
            if str(entry['Date']) == str(current_date):
                machine_name = entry['MachineName']
                today_stop_times = []  # time_stop = []
                if machine_name not in day_none_speed_minutes_counts:
                    day_none_speed_minutes_counts[machine_name] = 0
                    day_none_speed_minutes_hours[machine_name] = []
                if entry['Speed'] is None:
                    day_none_speed_minutes_counts[machine_name] += 5
                    day_none_speed_minutes_hours[machine_name].append(f"{entry['Hour']}:{entry['Minute']}")
        formatted_machine_line_names = [[machine, speeds] for machine, speeds in
                                        machine_line_names.items()]  # formatted_result
        month_2speed_none_keys = []  # speed_key_list   #machine_lists
        month_2speed_none_counts = []  # speed_key_count
        month_2speed_none_values = []  # speed_index
        for index, speed_list in enumerate(formatted_machine_line_names):
            month_2speed_none_keys.append(speed_list[0])
            my_list = speed_list[-1]
            count = 0
            i = 0
            ranges = []
            while i < len(my_list) - 1:
                if my_list[i] is None and my_list[i + 1] is None:
                    start = i
                    count += 1
                    while i < len(my_list) - 1 and my_list[i] is None:
                        i += 1
                    end = i - 1
                    if end > start:
                        ranges.append((start, end))
                else:
                    i += 1
            month_2speed_none_counts.append(count)
            if ranges:
                month_2speed_none_values.append(ranges)
        month_2speed_none_counts_dict = dict(zip(month_2speed_none_keys, month_2speed_none_counts))  # stop_2_times_dict
        month_2speed_none_values_dict = dict(
            zip(month_2speed_none_keys, month_2speed_none_values))  # stop_2_times_index
        line_stop_or_running_mode = []  # stopping_lines
        for index, elements in enumerate(formatted_machine_line_names):
            if all(value is None for value in elements[1]):
                line_stop_or_running_mode.append(elements[0])
        machine_line_names_sorted = sorted(month_2speed_none_keys, key=lambda x: (
        int(x.split('_')[2][:-1]), x.split('_')[2][-1]))  # machine_lines
        table_data_left_dict = {}  # grouped_data
        for item in machine_line_names_sorted:
            prefix = (item[:-1])
            if prefix not in table_data_left_dict:
                table_data_left_dict[prefix] = []
            table_data_left_dict[prefix].append(item)
        table_data_left_list = [[key, [device for device in value]] for key, value in
                                table_data_left_dict.items()]  # device_id
        table_data_left_list_rename = table_data_left_list  # new_device_id
        for index_data, device in enumerate(table_data_left_list_rename):
            for index, device1 in enumerate(device):
                if index == 0:
                    device[0] = device1.split('_')[0] + ' ' + device1.split('_')[-1]
                new_line_name = []
                if index == 1:
                    for device2 in device1:
                        new_line_name.append(device2.split('_')[0] + ' ' + device2.split('_')[-1])
                    device[1] = new_line_name
            table_data_left_list_rename[index_data] = device
        machine_line_names_sorted = sorted(
            machine_line_names.keys(),
            key=lambda k: (int(''.join(filter(str.isdigit, k.split('_')[-1]))),
                           ''.join(filter(str.isalpha, k.split('_')[-1])))
        )  # sorted_keys
        machine_line_speed_value_dict = {key: machine_line_names[key] for key in
                                         machine_line_names_sorted}  # sorted_data
        machine_line_speed_lasted_value = [value[-2:] for value in
                                           machine_line_speed_value_dict.values()]  # lasted_values
        machine_line_speed_lasted_mode = [0 if value[-1] is None else 1 for value in
                                          machine_line_speed_value_dict.values()]  # lasted_value_mode
        day_none_speed_minutes_counts_sorted_dict = {key: day_none_speed_minutes_counts[key] for key in
                                                     machine_line_names_sorted}  # sorted_stop
        day_none_speed_minutes_counts_sorted_list = [value for value in
                                                     day_none_speed_minutes_counts_sorted_dict.values()]  # lasted_stop
        day_none_speed_times_dict = {key: day_none_speed_minutes_hours[key] for key in
                                     machine_line_names_sorted}  # time_stop_key
        day_none_speed_times_list_str = [', '.join(value) for value in day_none_speed_times_dict.values()]  # time_stop
        month_none_speed_times_dict = {key: month_none_speed_minutes[key] for key in
                                       machine_line_names_sorted}  # msorted_stop
        month_none_speed_times_list_str = [value for value in month_none_speed_times_dict.values()]  # mlasted_stop
        month_2none_speed_times_dict = {key: month_2speed_none_counts_dict[key] for key in
                                        machine_line_names_sorted}  # stop_2_times
        month_2none_speed_times_list_str = [value for value in month_2none_speed_times_dict.values()]  # stop_2_time
        month_2none_speed_hour_dict = {key: month_2speed_none_values_dict[key] for key in
                                       machine_line_names_sorted}  # stop_2_indexs
        month_2none_speed_hour_list_str = [value for value in month_2none_speed_hour_dict.values()]  # stop_2_index
        info = []
        # Iterate through each list within the main list
        for index, value in enumerate(month_2none_speed_hour_list_str):
            sinfo = []
            # Iterate through each tuple within the sublist
            for sindex, svalue in enumerate(value):
                ssinfo = ''
                # Iterate through each number within the tuple
                for ssindex, ssvalue in enumerate(svalue):
                    # Calculate the date, hour, and minute
                    date = int(ssvalue / 288) + 1
                    hour = int((ssvalue % 288) / 12)
                    # Format the output string
                    if ssindex == 0:
                        mins = int((ssvalue % 288) % 12) * 5
                        ssinfo = f'{current_month}-{date} {hour:02}:{mins:02}'
                    else:
                        mins = int((ssvalue % 288) % 12 + 1) * 5 - 1
                        ssinfo += f' to {current_month}-{date} {hour:02}:{mins:02}\n'
                # Append the formatted string to the info list
                sinfo.append(ssinfo)
            # Output the formatted results for each sublist
            info.append(sinfo)
        info_str = []
        for values in info:
            formatted_output = '\n'.join(values)
            info_str.append(formatted_output)
        table_data_right_list_rename = [
            [mode, values[-1], fstop, tstop, mstop, rstop, time_info]
            for mode, values, fstop, tstop, mstop, rstop, time_info in
            zip(machine_line_speed_lasted_mode, machine_line_speed_lasted_value,
                day_none_speed_minutes_counts_sorted_list, day_none_speed_times_list_str,
                month_none_speed_times_list_str, month_2none_speed_times_list_str, info_str)
        ]

    end_time = time.time()
    execution_time = end_time - start_time
    return render(request, 'mes/machine_status.html', locals())

def general_status(request):

    return render(request, 'mes/status.html', locals())


def runcard_api(request, runcard):
    try:
        table_name = ""
        db = mes_database()
        sql = f"""
        select * from [PMGMES].[dbo].[PMG_MES_RunCard] rc where rc.Id = '{runcard}'
        """
        result = db.select_sql_dict(sql)

        if result:
            plant = result[0]["WorkCenterTypeName"]

            if plant == "NBR":
                table_name = "[PMGMES].[dbo].[PMG_MES_IPQCNBRStd]"
            else:
                table_name = "[PMGMES].[dbo].[PMG_MES_IPQCPVCStd]"


            sql_query = f"""
                select 
                rc.Id,
                rc.WorkOrderID,
                wo.CustomerPartNo,
                wo.PartNo,
                qc.LowerRoll,
                qc.UpperRoll,
                qc.LowerCuff,
                qc.UpperCuff,
                qc.LowerPalm,
                qc.UpperPalm,
                qc.LowerFinger,
                qc.UpperFinger,
                qc.LowerFingerTip,
                qc.UpperFingerTip
            from
                [PMGMES].[dbo].[PMG_MES_RunCard] rc
            left join
                [PMGMES].[dbo].[PMG_MES_WorkOrder] wo
                on rc.WorkOrderId = wo.Id
            left join
                {table_name} qc
                on wo.CustomerPartNo = qc.CustomerPartNo
                and wo.PartNo = qc.PartNo
            where 
                rc.Id = '{runcard}'
            """

            results = db.select_sql_dict(sql_query)
            if results:
                result = results[0]
                result_id = result['Id']
                result_LowerRoll = result['LowerRoll']
                result_UpperRoll = result['UpperRoll']
                result_LowerCuff = result['LowerCuff']
                result_UpperCuff = result['UpperCuff']
                result_LowerPalm = result['LowerPalm']
                result_UpperPalm = result['UpperPalm']
                result_LowerFinger = result['LowerFinger']
                result_UpperFinger = result['UpperFinger']
                result_LowerFingerTip = result['LowerFingerTip']
                result_UpperFingerTip = result['UpperFingerTip']
                status = 'OK'
                message = f'{runcard} được nhập thông tin thành công. Got {runcard} information successfully'
        else:
            result_id = result_LowerRoll = result_UpperRoll = result_LowerCuff = \
                result_UpperCuff = result_LowerPalm = result_UpperPalm = result_LowerFinger =\
                result_UpperFinger = result_LowerFingerTip = result_UpperFingerTip = None
            status = 'Fall'
            message = f'Runcard {runcard} không tồn tại. Runcard {runcard} not existed'
    except:
        result_id = result_LowerRoll = result_UpperRoll = result_LowerCuff = \
            result_UpperCuff = result_LowerPalm = result_UpperPalm = result_LowerFinger = \
            result_UpperFinger = result_LowerFingerTip = result_UpperFingerTip = None
        status = 'Fall'
        message = f'Không thể kết nối url http://192.168.11.31/mes/runcard/{runcard}'

    response_data = {
        'runcard': result_id,
        'ipqc_std': {
            'LowerRoll': result_LowerRoll,
            'UpperRoll': result_UpperRoll,
            'LowerCuff': result_LowerCuff,
            'UpperCuff': result_UpperCuff,
            'LowerPalm': result_LowerPalm,
            'UpperPalm': result_UpperPalm,
            'LowerFinger': result_LowerFinger,
            'UpperFinger': result_UpperFinger,
            'LowerFingerTip': result_LowerFingerTip,
            'UpperFingerTip': result_UpperFingerTip,
        },
        'status': status,
        'message': message,
    }
    return JsonResponse(response_data)

def insert_mes(data):
    db = scada_database()  # Assuming this is a function that sets up your database connection
    conn = db.create_sgada_connection()
    cursor = conn.cursor()
    procedure_name = '[dbo].[SP_AddTnicknessData]'

    runcard = data.get('runcard')
    local_ip = data.get('local_ip')
    roll = data.get('roll')
    cuff = data.get('cuff')
    palm = data.get('palm')
    finger = data.get('finger')
    finger_tip = data.get('finger_tip')

    # Adjust the finger and finger_tip values as required
    roll = float(roll)
    cuff = float(cuff)
    palm = float(palm)
    finger = float(finger)
    finger_tip = float(finger_tip)

    # Call the stored procedure
    cursor.execute(f"EXEC {procedure_name} ?, ?, ?, ?, ?, ?, ?", runcard, local_ip, roll, cuff, palm, finger, finger_tip)
    conn.commit()

    # 關閉連接
    cursor.close()
    conn.close()

@csrf_exempt
def thickness_data_api(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            insert_mes(data)

            runcard = data.get('runcard')
            response_data = {
                'status': 'OK',
                'message': f'{runcard} được thêm thành công. {runcard} insert successfully'
            }

            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Only PUT method is allowed'}, status=405)