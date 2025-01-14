from django.shortcuts import render
from django.http import JsonResponse
from VNEDC.database import mes_database, vnedc_database
from datetime import datetime, timedelta
import json
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from jobs.database import scada_database
from django.shortcuts import render

from collection.models import ParameterValue, Plant, Machine
from users.models import CustomUser
from .forms import DateRangeForm
from datetime import datetime
import calendar


def work_order_list(request):
    filters = []
    params = []

    # Get current date and 14 days ago
    today = datetime.today()
    fourteen_days_ago = today - timedelta(days=14)

    # Default filter for last 14 days
    filters.append("InspectionDate BETWEEN %s AND %s")
    params.extend([fourteen_days_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')])

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
    SELECT 
        InspectionDate, r.WorkOrderId, Period, r.Id, WorkCenterTypeName, MachineName, LineName, ProductItem, 
        CustomerCode, CustomerName, CustomerPartNo, AQL, w.PlanQty, u.NormalizedUserName, 
        FORMAT(r.CreationTime, 'yyyy/MM/dd HH:mm:ss') as CreationTime,
        FORMAT(w.StartDate, 'yyyy/MM/dd HH:mm:ss') as StartDate,FORMAT(w.EndDate, 'yyyy/MM/dd HH:mm:ss') as EndDate     
    FROM 
        [PMGMES].[dbo].[PMG_MES_RunCard] r
    LEFT JOIN 
        [PMGMES].[dbo].[PMG_MES_WorkOrder] w ON r.WorkOrderId = w.id
    LEFT JOIN 
        [PMGMES].[dbo].[AbpUsers] u ON r.CreatorUserId = u.Id
    """

    if filters:
        sql += " WHERE " + " AND ".join(filters)

    # Default ordering
    sql += " ORDER BY InspectionDate DESC, WorkOrderId"

    db = mes_database()
    work_orders = db.select_sql_dict_param(sql, params)

    return JsonResponse(work_orders, safe=False)


def runcard_detail(request):
    runcard = request.GET.get('runcard')

    sql = """
    SELECT 
        r.id, r.WorkOrderId, w.CustomerName, w.PartNo, w.ProductItem, q.OptionName, q.Upper_InspectionValue,
        q.InspectionValue, q.Lower_InspectionValue, q.InspectionStatus, q.InspectionUnit, q.DefectCode, 
        FORMAT(q.CreationTime, 'yyyy/MM/dd HH:mm:ss') as CreationTime, 
        FORMAT(w.StartDate, 'yyyy/MM/dd HH:mm:ss') as StartDate,FORMAT(w.EndDate, 'yyyy/MM/dd HH:mm:ss') as EndDate , u.Name -- Added StartDate and EndDate from PMG_MES_WorkOrder
    FROM 
        [PMGMES].[dbo].[PMG_MES_RunCard] r
    LEFT JOIN 
        [PMGMES].[dbo].[PMG_MES_WorkOrder] w ON r.WorkOrderId = w.id
    LEFT JOIN 
        [PMGMES].[dbo].[PMG_MES_IPQCInspectingRecord] q ON q.RunCardId = r.id
    LEFT JOIN 
        [PMGMES].[dbo].[AbpUsers] u ON q.CreatorUserId = u.Id
    WHERE 
        r.id = %s
    """

    db = mes_database()
    results = db.select_sql_dict_param(sql, [runcard])

    for result in results:
        if result['OptionName'] == "Roll":
            result['InspectionValue'] = str(result['InspectionValue'])
        elif result['OptionName'] == "Cuff":
            result['InspectionValue'] = str(result['InspectionValue'])
        elif result['OptionName'] == "Palm":
            result['InspectionValue'] = str(result['InspectionValue'])
        elif result['OptionName'] == "Finger":
            result['InspectionValue'] = str(result['InspectionValue'])
        elif result['OptionName'] == "FingerTip":
            result['InspectionValue'] = str(result['InspectionValue'])

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
            CONVERT(DATE, Cdt) AS Date,                   
            DATEPART(HOUR, Cdt) AS Hour,                  
            DATEPART(MINUTE, Cdt) AS Minutes     
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
    skq = []
    kq2 = []
    skq2 = []
    min = []
    # Extract unique device IDs from results


    for device in data:
        data_on_day = []
        sdata_on_day = []
        data_on_day2 = []
        sdata_on_day2 = []
        min_on_day = []
        for period in period_times:
            data_on_hour = []
            sdata_on_hour = []
            data_on_hour2 = []
            sdata_on_hour2 = []
            min_on_hour = []
            # Filter results for current device and hour
            matching_results = [result for result in results2 if
                                result['DeviceId'] == device and float(period) == float(result['Hour'])]

            if matching_results:
                # Append OKQty values if the period exists in results
                data_on_hour.extend(result['OKQty'] for result in matching_results)
                sdata_on_hour.extend(f" {result['Hour']}:0{result['Minutes']} - {result['OKQty']} " if len(str(result['Minutes'])) == 1 else
                                     f" {result['Hour']}:{result['Minutes']} - {result['OKQty']} " for result in matching_results)
                data_on_hour2.extend(result['NGQty'] for result in matching_results)
                sdata_on_hour2.extend(f" {result['Hour']}:0{result['Minutes']} - {result['NGQty']} " if len(str(result['Minutes'])) == 1 else
                                      f" {result['Hour']}:{result['Minutes']} - {result['NGQty']} " for result in matching_results)
                min_on_hour.extend(result['Minutes'] for result in matching_results)
            else:
                # Append a list with 12 zeros if the period is missing
                data_on_hour = [0]
                sdata_on_hour = [0]
                data_on_hour2 = [0]
                sdata_on_hour2 = [0]
                min_on_hour = [0]
            data_on_day.append(data_on_hour)
            sdata_on_day.append(sdata_on_hour)
            data_on_day2.append(data_on_hour2)
            sdata_on_day2.append(sdata_on_hour2)
            min_on_day.append(min_on_hour)
        kq.append(data_on_day)
        skq.append(sdata_on_day)
        kq2.append(data_on_day2)
        skq2.append(sdata_on_day2)
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

    table_data1 = [status_OKQty[i:i + 24] for i in range(0, len(status_OKQty), 24)]
    # table_data2 = kq
    table_data3 = []
    for i in range(24):
        table_data3.append(period_times)
    # table_data4 = min
    merged_status, merged_kq = [], []
    for i in range(0, (len(data)*24), 24):
        merged_status.extend(status_OKQty[i:i + 24])
        merged_status.extend(status_NGQty[i:i + 24])
    table_data11 = [merged_status[i:i + 24] for i in range(0, len(merged_status), 24)]
    table_data22 = [item for pair in zip(skq, skq2) for item in pair]
    table_data1 = table_data11
    table_data2 = table_data22
    table_data3 = table_data3*2
    table_data4 = min*2

    return render(request, 'mes/fast_check2.html', locals())


import time
def machine_status(request):

    return render(request, 'mes/machine_status.html', locals())


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

def machine_master_data_format(request):
    try:
        db = vnedc_database()
        update_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql1 = """
            select distinct(pd.mach_id), pd.plant_id
            from [VNEDC].[dbo].[collection_parameterdefine] pd
            order by pd.plant_id, pd.mach_id
        """
        machine_list = db.select_sql_dict(sql1)
        machines = []
        for item in machine_list:
            body = {
                'PLANT': item['plant_id'],
                'MACH_CODE': item['mach_id'],
                'MACH_NAME': item['mach_id'],
                'MOLD_TYPE': 'SINGLE',
                'UPDATE_DATE': update_date
            }
            machines.append(body)
        json_body = {"MachineMaster": {"Machine": machines}}
        return JsonResponse(json_body, safe=False)

    except Exception as e:
        print("Error:", e)
        pass
        # return JsonResponse({"error": "Failed to retrieve machine data"}, status=500)

def process_type_master_data_format(request):
    try:
        db = vnedc_database()
        update_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql1 = """
               SELECT process_code, process_name, process_tw, process_cn, process_vn, show_order
               FROM [VNEDC].[dbo].[collection_process_type]
               order by show_order
               """

        process_list = db.select_sql_dict(sql1)
        process = []
        for item in process_list:
            body = {
                'PROCESS_CODE': item['process_code'],
                'PROCESS_NAME': item['process_name'],
                'PROCESS_TW': item['process_tw'],
                'PROCESS_CN': item['process_cn'],
                'PROCESS_VN': item['process_vn'],
                'SHOW_ORDER': item['show_order'],
                'UPDATE_DATE': update_date
            }
            process.append(body)
        json_body = {"ProcessMaster": {"Process": process}}
        return JsonResponse(json_body, safe=False)

    except Exception as e:
        print("Error:", e)
        pass
        # return JsonResponse({"error": "Failed to retrieve machine data"}, status=500)

def parameter_define_master_data_format(request):
    try:
        db = vnedc_database()
        update_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql1 = """
                select plant_id, mach_id, process_type_id, parameter_name, parameter_tw, 
                parameter_cn, parameter_vn, show_order, base_line, control_range_high, 
                control_range_low, sampling_frequency, unit, side
                from [VNEDC].[dbo].[collection_parameterdefine]
                order by plant_id, mach_id, show_order
               """

        parameter_list = db.select_sql_dict(sql1)
        parameter = []
        for item in parameter_list:
            body = {
                'PLANT': item['plant_id'],
                'MACH_CODE': item['mach_id'],
                'PROCESS_TYPE': item['process_type_id'],
                'PARAMETER_CODE': item['parameter_name'],
                'PARAMETER_TW': item['parameter_tw'],
                'PARAMETER_CN': item['parameter_cn'],
                'PARAMETER_VN': item['parameter_vn'],
                'SHOW_ORDER': item['show_order'],
                'BASE_LINE': item['base_line'],
                'CONTROL_RANGE_HIGH': item['control_range_high'],
                'CONTROL_RANGE_LOW': item['control_range_low'],
                'FREQUENCY': item['sampling_frequency'],
                'UNIT': item['unit'],
                'SIDE': item['side'],
                'UPDATE_DATE': update_date
            }
            parameter.append(body)
        json_body = {"ParameterMaster": {"Parameter": parameter}}
        return JsonResponse(json_body, safe=False)

    except Exception as e:
        print("Error:", e)
        pass
        # return JsonResponse({"error": "Failed to retrieve machine data"}, status=500)

def excel_api(request):
    try:
        db = mes_database()
        sql = """
                WITH ProductItem AS (
                SELECT InspectionDate, MachineName, LineName, STRING_AGG(ProductItem, '/') AS ProductList from (
                SELECT distinct r.InspectionDate, MachineName, LineName, ProductItem
                from [PMGMES].[dbo].[PMG_MES_RunCard] r, [PMGMES].[dbo].[PMG_MES_IPQCInspectingRecord] ipqc, [PMGMES].[dbo].[PMG_MES_WorkOrder] w
                where r.Id = ipqc.RunCardId and r.WorkOrderId = w.Id and ipqc.OptionName = 'Weight' and r.InspectionDate between '2024-09-18' and GETDATE()
                ) A group by InspectionDate, MachineName, LineName
                )
              
                SELECT CAST(DATEDIFF(DAY, '1899-12-30', d.CreationTime) AS NVARCHAR(50))+LINE AS ExcelKey, FORMAT(d.CreationTime, 'yyyy-MM-dd') record_date, LINE, sum(Qty2) qty2_sum
                  FROM [PMG_DEVICE].[dbo].[COUNTING_DATA] d, [PMG_DEVICE].[dbo].[COUNTING_DATA_MACHINE] dm, ProductItem i
                  where d.MachineName = dm.COUNTING_MACHINE and i.MachineName = dm.MES_MACHINE and i.LineName = LINE and i.InspectionDate = FORMAT(d.CreationTime, 'yyyy-MM-dd')
                  and CreationTime between CONVERT(DATETIME, '20240918 00:00:00', 120) and GETDATE()
                  and MES_MACHINE = 'VN_GD_NBR1_L08'
                  group by DATEDIFF(DAY, '1899-12-30', d.CreationTime), FORMAT(d.CreationTime, 'yyyy-MM-dd'), LINE
                  order by record_date, LINE
                """
        rows = db.select_sql_dict(sql)
        table_data = []
        for row in rows:
            table_data.append([row['ExcelKey'], row['record_date'], row['LINE'], row['qty2_sum']])
        return render(request, 'mes/excel_update.html', locals())
    except:
        pass

@csrf_exempt
def account_check(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            account = data.get('account')
            password = data.get('password')
            valid = account_validation(account, password)
        except Exception as e:
            print("Exception:", e)
            valid = False
    else:
        valid = False
    return JsonResponse({'valid': valid})

import hashlib
import binascii
def account_validation(account, password):
    try:
        db = vnedc_database()
        sql = f"SELECT password FROM [VNEDC].[dbo].[users_customuser] where emp_no = '{account}'"
        rows = db.select_sql_dict(sql)
        user_password = rows[0]['password']
        algorithm, iterations, salt, hash_value = user_password.split('$')
        iterations = int(iterations)
        salt = salt.encode()
        stored_hash = binascii.a2b_base64(hash_value)
        new_hash = hashlib.pbkdf2_hmac('sha256', str(password).encode(), salt, iterations)
        is_valid = new_hash == stored_hash
    except Exception as e:
        print("Exception:", e)
        is_valid = False
    return is_valid

@csrf_exempt
def insert_parameter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            data_date = data.get('data_date')
            plant_id = data.get('plant_id')
            mach_id = data.get('mach_id')
            process_type = data.get('process_type')
            parameter_name = data.get('parameter_name')
            parameter_value = float(data.get('parameter_value'))
            create_at = data.get('create_date')
            emp_no = data.get('create_id')

            plant = Plant.objects.get(plant_code=plant_id)
            mach = Machine.objects.get(mach_code=mach_id)
            user = CustomUser.objects.get(emp_no=emp_no)

            if any(value is None for value in [data_date, plant, mach, process_type, parameter_name, parameter_value, create_at, user]):
                status = False
                pass
            else:
                data_time = (str(create_at).split(' '))[-1].split(':')[0]
                if 0 <= int(data_time) < 6:
                    data_time = '06'
                elif 6 <= int(data_time) < 12:
                    data_time = '12'
                elif 12 <= int(data_time) < 18:
                    data_time = '18'
                else:
                    data_time = '00'

                ParameterValue.objects.update_or_create(plant=plant, mach=mach,
                                                        data_date=data_date,
                                                        process_type=process_type,
                                                        data_time=data_time,
                                                        parameter_name=parameter_name,
                                                        defaults={'parameter_value': parameter_value,
                                                                  'create_by': user,
                                                                  'update_by': user})
                status = True
                print(f'insert_parameter status: {status}')
        except Exception as e:
            print("Exception:", e)
            status = False
    else:
        status = False
    return JsonResponse({'success': status})

def general_status(request):
    start_time = time.time()
    execution_time = 0
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_month = datetime.now().strftime('%Y-%m')
    current_time = datetime.now()
    time_10_minutes_ago = (current_time - timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
    time_10_minutes_next = (current_time + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
    selected_date = current_date
    selected_machine = 'NBR'

    if request.method == 'POST':
        selected_date = request.POST.get('date', '')
        selected_machine = request.POST.get('machine', 'PVC')
        sLimit_mode = request.session.get('limit_mode', '0')

    period_times = ['6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17',
                    '18', '19', '20', '21', '22', '23', '0', '1', '2', '3', '4', '5']
    db = mes_database()

    sql1 = f"""
                WITH LatestRecords AS (
                        SELECT 
                            MachineName,
                            CreationTime,
                            Speed,
                            ROW_NUMBER() OVER (PARTITION BY MachineName ORDER BY CreationTime DESC) AS RowNum
                        FROM 
                            [PMG_DEVICE].[dbo].[COUNTING_DATA]
                        WHERE 
                            CreationTime BETWEEN CONVERT(DATETIME, '{time_10_minutes_ago}', 120) 
                                            AND CONVERT(DATETIME, '{time_10_minutes_next}', 120) 
                    ),
                    FilteredRecords AS (
                        SELECT 
                            MachineName,
                            CreationTime,
                            Speed
                        FROM 
                            LatestRecords
                        WHERE 
                            RowNum <= 2  
                    ),
                    AggregatedRecords AS (
                        SELECT 
                            MachineName,
                            MAX(CASE WHEN RowNum = 1 THEN Speed END) AS LatestSpeed,
                            MAX(CASE WHEN RowNum = 2 THEN Speed END) AS SecondLatestSpeed
                        FROM 
                            LatestRecords
                        GROUP BY 
                            MachineName
                    )

                    SELECT 
                        cdm.COUNTING_MACHINE,
                        ar.SecondLatestSpeed,
                        ar.LatestSpeed,
                        CASE 
                            WHEN (ar.LatestSpeed IS NULL OR ar.LatestSpeed = 0) 
                                AND (ar.SecondLatestSpeed IS NULL OR ar.SecondLatestSpeed = 0) THEN 0
                            ELSE 1
                        END AS [Check]
                    FROM 
                        [PMG_DEVICE].[dbo].[COUNTING_DATA_MACHINE] cdm
                    LEFT JOIN 
                        AggregatedRecords ar ON cdm.COUNTING_MACHINE = ar.MachineName
                    WHERE 
                        cdm.COUNTING_MACHINE LIKE '%{selected_machine}_CountingMachine%'
                    ORDER BY
                        cdm.MES_MACHINE,
                        cdm.COUNTING_MACHINE;
            """

    machineline_lastedvalue_2lastedvalue_stopstatus_dict = db.select_sql_dict(sql1)
    machineline_stopstatus_list, machineline_list, lastedvalue_2lastedvalue_list = [], [], []
    for value in machineline_lastedvalue_2lastedvalue_stopstatus_dict:
        machineline_stopstatus_list.append([value['COUNTING_MACHINE'], value['Check']])
        machineline_list.append(value['COUNTING_MACHINE'])
        lastedvalue_2lastedvalue_list.append([value['SecondLatestSpeed'], value['LatestSpeed']])

    group_machinename_with_machineline = {}
    group_2lastedvalue_status_machineline = {}
    group_2lastedvalue_lastedvalue_machineline = {}
    for index, machine_line in enumerate(machineline_list):
        machine_name = f"{machine_line.split('_CountingMachine_')[0]} {machine_line.split('_CountingMachine_')[-1][:-1]}"
        if machine_name not in group_machinename_with_machineline:
            group_machinename_with_machineline[machine_name] = []
            group_2lastedvalue_status_machineline[machine_name] = []
            group_2lastedvalue_lastedvalue_machineline[machine_name] = []
        group_machinename_with_machineline[machine_name].append(
            f"{machine_line.split('_CountingMachine_')[0]} {machine_line.split('_CountingMachine_')[-1]}")
        group_2lastedvalue_status_machineline[machine_name].append(machineline_stopstatus_list[index][1])
        group_2lastedvalue_lastedvalue_machineline[machine_name].append(lastedvalue_2lastedvalue_list[index])
    # #Column 3 - part 2 - machine speed status
    # stopstatus = list(group_2lastedvalue_status_machineline.values())
    # #-----------------

    # #Column 3 - part 4 - machine speed values
    # speedvalue = list(group_2lastedvalue_lastedvalue_machineline.values())
    # #-----------------

    sql2 = f"""
            SELECT 
                    dml.Name AS MachineName,
                    CASE 
                        WHEN COUNT(wo.Id) > 0 THEN 1 
                        ELSE 0 
                    END AS WorkOrderMode
                FROM 
                    [PMGMES].[dbo].[PMG_DML_DataModelList] dml
                LEFT JOIN 
                    [PMGMES].[dbo].[PMG_MES_WorkOrder] wo 
                    ON dml.Id = wo.MachineId
                    AND wo.StartDate IS NOT NULL
                    AND wo.StartDate BETWEEN '{selected_date} 05:30:00' 
                                        AND DATEADD(SECOND, -1, DATEADD(DAY, 1, '{selected_date} 05:30:00'))
                WHERE 
                    dml.DataModelTypeId = 'DMT000003'
                    AND dml.Name LIKE '%{selected_machine}%'
                GROUP BY 
                    dml.Name
                ORDER BY 
                    dml.Name;"""

    machinename_workorder_dict = db.select_sql_dict(sql2)
    # #Column 3 - part 1 - work order status
    # workoder = [value['WorkOrderMode'] for value in machinename_workorder_dict]
    # #-----------------

    sql3 = f"""
                SELECT 
                    dml.Name AS MachineName,
                    wo.Id AS WorkOrderId
                FROM 
                    [PMGMES].[dbo].[PMG_DML_DataModelList] dml
                LEFT JOIN 
                    [PMGMES].[dbo].[PMG_MES_WorkOrder] wo 
                    ON dml.Id = wo.MachineId
                    AND wo.StartDate IS NOT NULL
                    AND wo.StartDate BETWEEN '{selected_date} 05:30:00' 
                                        AND DATEADD(SECOND, -1, DATEADD(DAY, 1, '{selected_date} 05:30:00'))
                WHERE 
                    dml.DataModelTypeId = 'DMT000003'
                    AND dml.Name LIKE '%{selected_machine}%'
                ORDER BY 
                    dml.Name, wo.Id;
                """

    machinename_workorderid_dict = db.select_sql_dict(sql3)
    group_workorderid = defaultdict(list)
    for entry in machinename_workorderid_dict:
        group_workorderid[entry['MachineName']].append(entry['WorkOrderId'])
    # #Column 3 - part 3 - work order id values
    # workorderid = list(group_workorderid.values())
    # #-----------------

    sql4 = f"""
                       select rc.MachineName, rc.LineName, rc.Period,rc.Id, ir.InspectionValue
            from [PMGMES].[dbo].[PMG_MES_RunCard]  rc
            left join [PMGMES].[dbo].[PMG_MES_IPQCInspectingRecord] ir
            on ir.RunCardId =  rc.Id and OptionName = 'Weight'
            where rc.MachineName like '%{selected_machine}%' 
            and ((rc.InspectionDate = '{selected_date}' and period between 6 and 23) 
            or ( rc.InspectionDate = DATEADD(DAY, 1, '{selected_date}') and period between 0 and 5))
            order by rc.machineName, rc.InspectionDate, Cast(rc.Period as Int)
                """

    runcard_and_weights = db.select_sql_dict(sql4)
    group_runcard_periods = defaultdict(list)
    group_runcard_machine = defaultdict(lambda: defaultdict(list))
    group_weights_machine = defaultdict(lambda: defaultdict(list))
    for entry in runcard_and_weights:
        group_runcard_periods[entry['MachineName']].append(entry['Period'])
        group_runcard_machine[entry['MachineName']][entry['Period']].append(entry['Id'])
        group_weights_machine[entry['MachineName']][entry['Period']].append(entry['InspectionValue'])
    runcard_periods_with_time = [
        [machine_name,
         [[period, periods.get(period, []) if periods.get(period) != [None] else []] for period in period_times]]
        for machine_name, periods in group_runcard_machine.items()]
    runcard_weights_with_time = [
        [machine_name,
         [[period, [float(value) for value in periods.get(period, []) if value is not None]] for period in
          period_times]]
        for machine_name, periods in group_weights_machine.items()]
    runcard_periods = [[period[-1] for period in machine[1]] for machine in runcard_periods_with_time]
    weights_periods = [[period[-1] for period in machine[1]] for machine in runcard_weights_with_time]

    # #Column 4 - part 1 - runcard lost periods
    # runcard_lost = [len([value for value in period_times if value not in period]) for period in list(group_runcard_periods.values())]
    # #-----------------

    sql5 = f"""
                SELECT 
                    cdm.MES_MACHINE as MachineName, 
                    cdm.LINE, 
                    cd.Speed,
                    DATEPART(MINUTE, cd.CreationTime) AS Minute
                FROM 
                    [PMG_DEVICE].[dbo].[COUNTING_DATA_MACHINE] cdm
                LEFT JOIN 
                    [PMG_DEVICE].[dbo].[COUNTING_DATA] cd 
                    ON cd.MachineName = cdm.COUNTING_MACHINE 
                    AND cd.CreationTime BETWEEN CONVERT(DATETIME, '{selected_date} 06:00:00', 120) 
                                        AND CONVERT(DATETIME, DATEADD(SECOND, -1, CONVERT(DATETIME, DATEADD(DAY, 1, '{selected_date}') + ' 06:00:00', 120)), 120)
                    AND (cd.Speed = 0 OR cd.Speed IS NULL)
                WHERE 
                    cdm.COUNTING_MACHINE LIKE '%{selected_machine}%'
                ORDER BY 
                    cdm.MES_MACHINE, 
                    cdm.LINE, 
                    cd.CreationTime;
                """

    stop_or_null_time = db.select_sql_dict(sql5)
    group_stop_base_machine = {}
    for entry in stop_or_null_time:
        machine = entry['MachineName']
        line = entry['LINE']
        minute = entry['Minute']
        if machine not in group_stop_base_machine:
            group_stop_base_machine[machine] = {}
        if line not in group_stop_base_machine[machine]:
            group_stop_base_machine[machine][line] = 0
        if minute is not None:
            group_stop_base_machine[machine][line] += 5
    # #Column 4 - part 2 - machine stopped minutes
    # stoped_time = [[count for count in line_counts.values()] for line_counts in group_stop_base_machine.values()]
    # #-----------------

    sql6 = f"""
            SELECT 
                cdm.MES_MACHINE as MachineName, 
                cdm.LINE, 
                cd.Qty2,
                DATEPART(HOUR, cd.CreationTime) AS Period
            FROM 
                [PMG_DEVICE].[dbo].[COUNTING_DATA_MACHINE] cdm
            LEFT JOIN 
                [PMG_DEVICE].[dbo].[COUNTING_DATA] cd 
                ON cd.MachineName = cdm.COUNTING_MACHINE 
                AND cd.CreationTime BETWEEN CONVERT(DATETIME, '{selected_date} 06:00:00', 120) 
                                    AND CONVERT(DATETIME, DATEADD(SECOND, -1, CONVERT(DATETIME, DATEADD(DAY, 1, '{selected_date}') + ' 06:00:00', 120)), 120)
                AND cd.Qty2 is not NULL
                AND (Speed is not NULL or cd.Speed >= 60)
            WHERE 
                cdm.COUNTING_MACHINE LIKE '%{selected_machine}%'
            ORDER BY 
                cdm.MES_MACHINE, 
                cdm.LINE, 
                cd.CreationTime;"""

    qty2_and_period = db.select_sql_dict(sql6)
    group_qty2_and_period = {}
    for entry in qty2_and_period:
        machine = entry['MachineName']
        line = entry['LINE']
        period = entry['Period']
        if machine not in group_qty2_and_period:
            group_qty2_and_period[machine] = {}
        if line not in group_qty2_and_period[machine]:
            group_qty2_and_period[machine][line] = {}
        if period not in group_qty2_and_period[machine][line]:
            group_qty2_and_period[machine][line][period] = []
        group_qty2_and_period[machine][line][period].append(entry['Qty2'])
    qty2_and_period_dict = {}
    for key, sub_dict in group_qty2_and_period.items():
        result = []
        for line, periods in sub_dict.items():
            line_values = []
            for period, values in periods.items():
                line_values.append(values)
            result.append(line_values)
        qty2_and_period_dict[key] = result
    qty2_and_period_list = list(qty2_and_period_dict.values())

    if selected_machine == 'PVC':
        sql7 = f"""
                                WITH FirstQuery AS (
                                    SELECT DISTINCT 
                                        DeviceId
                                    FROM 
                                        [PMG_DEVICE].[dbo].[OpticalDevice]
                                    WHERE 
                                        DeviceId LIKE '%PVC%'
                                        AND DeviceId LIKE '%PVC1_L%'
                                        AND DeviceId LIKE '%AOI%'
                                        AND CONVERT(DATE, Cdt) = '2024-09-21'
                                ),
                                HoursList AS (
                                    -- List of hours from 6 AM today to 5 AM tomorrow
                                    SELECT 6 AS [Hour]
                                    UNION ALL SELECT 7
                                    UNION ALL SELECT 8
                                    UNION ALL SELECT 9
                                    UNION ALL SELECT 10
                                    UNION ALL SELECT 11
                                    UNION ALL SELECT 12
                                    UNION ALL SELECT 13
                                    UNION ALL SELECT 14
                                    UNION ALL SELECT 15
                                    UNION ALL SELECT 16
                                    UNION ALL SELECT 17
                                    UNION ALL SELECT 18
                                    UNION ALL SELECT 19
                                    UNION ALL SELECT 20
                                    UNION ALL SELECT 21
                                    UNION ALL SELECT 22
                                    UNION ALL SELECT 23
                                    UNION ALL SELECT 0
                                    UNION ALL SELECT 1
                                    UNION ALL SELECT 2
                                    UNION ALL SELECT 3
                                    UNION ALL SELECT 4
                                    UNION ALL SELECT 5
                                ),
                                SecondQuery AS (
                                    SELECT 
                                        od.DeviceId, 
                                        od.OKQty, 
                                        od.NGQty, 
                                        DATEPART(HOUR, od.Cdt) AS [Hour],                  
                                        DATEPART(MINUTE, od.Cdt) AS [Minutes],
                                        Cdt
                                    FROM 
                                        [PMG_DEVICE].[dbo].[OpticalDevice] od
                                    WHERE 
                                        od.DeviceId LIKE '%PVC%'
                                        AND od.Cdt BETWEEN CONVERT(DATETIME, '{selected_date} 06:00:00', 120) 
                                                       AND CONVERT(DATETIME, DATEADD(SECOND, -1, CONVERT(DATETIME, DATEADD(DAY, 1, '{selected_date}') + ' 06:00:00', 120)), 120)
                                )
                                SELECT 
                                    fq.DeviceId, 
                                    h.[Hour], 
                                    sq.OKQty, 
                                    sq.NGQty, 
                                    sq.Minutes
                                FROM 
                                    FirstQuery fq
                                CROSS JOIN 
                                    HoursList h  -- Create all hour combinations with each DeviceId
                                LEFT JOIN 
                                    SecondQuery sq
                                    ON fq.DeviceId = sq.DeviceId 
                                    AND h.[Hour] = sq.[Hour]  -- Join actual data for each hour
                                ORDER BY 
                                    CAST(
                                        SUBSTRING(
                                            fq.DeviceId, 
                                            CHARINDEX('_L', fq.DeviceId) + 2, 
                                            CHARINDEX('_', fq.DeviceId, CHARINDEX('_L', fq.DeviceId) + 2) - CHARINDEX('_L', fq.DeviceId) - 2
                                        ) AS INT),
                                    fq.DeviceId
                    """

        aoi_dict = db.select_sql_dict(sql7)
    elif selected_machine == 'NBR':
        aoi_dict = [{'DeviceId': 'NBR1_L01_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L01_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L02_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L02_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L03_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L03_A2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L03_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L03_B2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L04_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L04_A2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L04_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L04_B2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L05_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L05_A2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L05_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L05_B2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L06_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L06_A2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L06_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L06_B2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L07_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L07_A2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L07_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L07_B2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L08_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L08_A2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L08_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L08_B2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L09_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L09_A2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L09_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L09_B2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L10_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L10_A2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L10_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L10_B2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L11_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L11_A2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L11_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L11_B2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L12_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L12_A2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L12_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L12_B2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L13_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L13_A2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L13_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L13_B2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L14_A1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L14_A2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L14_B1_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None},
                    {'DeviceId': 'NBR1_L14_B2_AOI', 'OKQty': None, 'NGQty': None, 'Hour': None, 'Minutes': None}]
    group_aoi_ok = {}
    group_aoi_ng = {}
    group_aoi_mi = {}
    group_aoi_ok_popup = {}
    group_aoi_ng_popup = {}
    for entry in aoi_dict:
        machine = '_'.join(entry['DeviceId'].split('_')[:2])
        machine_line = entry['DeviceId']
        hour = entry['Hour']
        group_aoi_ok.setdefault(machine, {}).setdefault(machine_line, {}).setdefault(hour, []).append(entry['OKQty'])
        group_aoi_ng.setdefault(machine, {}).setdefault(machine_line, {}).setdefault(hour, []).append(entry['NGQty'])
        group_aoi_mi.setdefault(machine, {}).setdefault(machine_line, {}).setdefault(hour, []).append(entry['Minutes'])
        group_aoi_ok_popup.setdefault(machine, {}).setdefault(machine_line, {}).setdefault(hour, []).append(
            f"{entry['Hour']}:{entry['Minutes']} - {entry['OKQty']}")
        group_aoi_ng_popup.setdefault(machine, {}).setdefault(machine_line, {}).setdefault(hour, []).append(
            f"{entry['Hour']}:{entry['Minutes']} - {entry['NGQty']}")

    aoi_ok = [[[sub_data[hour] for hour in sub_data] for sub_data in sub_dict.values()]
              for sub_dict in group_aoi_ok.values()]
    aoi_ng = [[[sub_data[hour] for hour in sub_data] for sub_data in sub_dict.values()]
              for sub_dict in group_aoi_ng.values()]
    aoi_mi = [[[sub_data[hour] for hour in sub_data] for sub_data in sub_dict.values()]
              for sub_dict in group_aoi_mi.values()]
    aoi_ok_popup = [[[sub_data[hour] for hour in sub_data] for sub_data in sub_dict.values()]
                    for sub_dict in group_aoi_ok_popup.values()]
    aoi_ng_popup = [[[sub_data[hour] for hour in sub_data] for sub_data in sub_dict.values()]
                    for sub_dict in group_aoi_ng_popup.values()]
    # print(len(aoi_ok[0][1]))
    # print(len(aoi_ok_popup[0][1]))



    aoi_ok_mode = []
    aoi_ng_mode = []
    for machine in aoi_ok:
        machine_mode = []
        for line in machine:
            line_mode = []
            for index, period in enumerate(period_times):
                try:
                    if all(value == 0 for value in line[index]):
                        line_mode.append(0)  # RED
                    elif all(value >= 200 for value in line[index]):
                        line_mode.append(1)  # GREEN
                    else:  # all((value > 0 and value < 200) for value in line[index]):
                        line_mode.append(2)  # YELLOW
                except:
                    line_mode.append(3)
            machine_mode.append(line_mode)
        aoi_ok_mode.append(machine_mode)
    for machine in aoi_ng:
        machine_mode = []
        for line in machine:
            line_mode = []
            for index, period in enumerate(period_times):
                try:
                    if all(value == 0 for value in line[index]):
                        line_mode.append(0)  # RED
                    elif all(value >= 20 for value in line[index]):
                        line_mode.append(2)  # GREEN
                    else:  # all((value > 0 and value < 200) for value in line[index]):
                        line_mode.append(1)  # YELLOW
                except:
                    line_mode.append(3)
            machine_mode.append(line_mode)
        aoi_ng_mode.append(machine_mode)

    aoi_ok_zip = []
    for index, value in enumerate(aoi_ok):
        aoi_ok_zip.append(list(zip(aoi_ok_mode[index], aoi_ok_popup[index])))

    aoi_ng_zip = []
    for index, value in enumerate(aoi_ok):
        aoi_ng_zip.append(list(zip(aoi_ng_mode[index], aoi_ng_popup[index])))
    # Column 1and2 - machine name and machine lines
    # List1
    machine_name_with_line = [[key, value] for key, value in group_machinename_with_machineline.items()]
    # -----------------
    # Column 3 - part 1 - work order status
    # List2
    workoder = [value['WorkOrderMode'] for value in machinename_workorder_dict]
    # -----------------
    # Column 3 - part 2 - machine speed status
    # List5
    stopstatus = list(group_2lastedvalue_status_machineline.values())
    # -----------------
    # Column 3 - part 3 - work order id values
    # List4
    workorderid = list(group_workorderid.values())
    fworkorderid = ['-'.join(sublist) if sublist[0] is not None else '' for sublist in workorderid]
    # -----------------
    # Column 3 - part 4 - machine speed values
    # List6
    speedvalue = list(group_2lastedvalue_lastedvalue_machineline.values())
    # -----------------
    # Column 4 - part 1 - runcard lost periods
    # List3
    runcard_lost = [len([value for value in period_times if value not in period]) for period in
                    list(group_runcard_periods.values())]
    # -----------------
    # Column 4 - part 2 - machine stopped minutes
    # List7
    stoped_time = [[count for count in line_counts.values()] for line_counts in group_stop_base_machine.values()]
    # -----------------
    # Column 5 - part 1 - machine count data
    qty2_on_period = []
    qty2_on_machineline = []
    for machine in qty2_and_period_list:
        sqty2 = []
        ssum_qty2 = 0
        for item in machine:
            ssqty2 = [sum(value for value in item2 if value is not None) for item2 in item]
            sqty2.append(ssqty2)
            ssum_qty2 += sum(ssqty2)
        qty2_on_period.append(sqty2)
        qty2_on_machineline.append(ssum_qty2)
    counting_machine_mode = [0 if any(0 in data for data in counting_data) else 1 for counting_data in qty2_on_period]
    counting_data_on_period = [[[item[period] for item in counting_data if len(item) > period]
                                if not all(
        value in (None, 0) for value in [item[period] for item in counting_data if len(item) > period]) else []
                                for period in range(24)] for counting_data in qty2_on_period]

    # -----------------

    list1 = machine_name_with_line
    list2 = workoder
    list3 = runcard_lost
    list4 = fworkorderid
    list5 = stopstatus
    list6 = stoped_time
    list7 = speedvalue
    list8 = qty2_on_machineline
    list9 = counting_machine_mode
    left_table_data = []
    for i in range(len(list1)):
        machine_name = list1[i][0]
        summary_row = [' ', list2[i], list3[i], list9[i], list8[i], list4[i]]
        detailed_rows = []
        num_lines = min(len(list1[i][1]), len(list5[i]), len(list6[i]), len(list7[i]))
        for j in range(num_lines):
            detailed_row = [list1[i][1][j], list5[i][j], list6[i][j], list7[i][j]]
            detailed_rows.append(detailed_row)
        left_table_data.append([machine_name, [summary_row] + detailed_rows])
    right_table_data = [
        [runcard_periods[i], weights_periods[i], counting_data_on_period[i], aoi_ok_zip[i][0], aoi_ok_zip[i][0],
         aoi_ng_zip[i][1], aoi_ng_zip[i][1]]
        if len(aoi_ok_mode[i]) == 2 and len(aoi_ng_mode[i]) == 2
        else [runcard_periods[i], weights_periods[i], counting_data_on_period[i], aoi_ok_zip[i][0], aoi_ng_zip[i][0],
              aoi_ok_zip[i][1], aoi_ng_zip[i][1], aoi_ok_zip[i][2], aoi_ng_zip[i][2], aoi_ok_zip[i][3],
              aoi_ng_zip[i][3]]
        for i in range(len(runcard_periods))
    ]
    end_time = time.time()
    execution_time = end_time - start_time
    return render(request, 'mes/status.html', locals())


def monthly_check(request):
    form = DateRangeForm(request.GET or None)

    if form.is_valid():
        selected_month = form.cleaned_data['month']
        year = int(str(selected_month).split('-')[0])
        month = int(str(selected_month).split('-')[-1])
        days_in_month = calendar.monthrange(year, month)[1]  # Số ngày trong tháng
        days = range(1, days_in_month + 1)  # Các ngày từ 1 đến ngày cuối trong tháng
        start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
        end_date = datetime(year, month, days_in_month).strftime('%Y-%m-%d')

        db = vnedc_database()
        sql1 = f"""
            SELECT DISTINCT(Name) FROM [MES_OLAP].[dbo].[mes_daily_report_raw]
            WHERE belong_to BETWEEN '{start_date}' AND '{end_date}' AND name LIKE '%NBR%' order by name
        """
        rows1 = db.select_sql_dict(sql1)
        sql2 = f"""
            SELECT Name, belong_to, SUM(sum_qty) AS counting, SUM(ticket_qty) AS sap_qty
            FROM [MES_OLAP].[dbo].[mes_daily_report_raw]
            WHERE belong_to BETWEEN '{start_date}' AND '{end_date}' AND belong_to IS NOT NULL AND ticket_qty IS NOT NULL
            AND name LIKE '%NBR%'
            GROUP BY belong_to, Name
            ORDER BY Name, belong_to
        """
        rows2 = db.select_sql_dict(sql2)

        data_table = []

        for sub_rows1 in rows1:
            line = []
            counter = 0
            name = sub_rows1['Name']
            split_name = f"{(sub_rows1['Name'].split('_'))[-1]}"
            line.append(split_name)

            #sub_data_counting = ["Counting"]
            # sub_data_counting = [name]
            # sub_data_sap_qty = [name]

            sub_data_counting = []
            sub_data_sap_qty = []
            # Khởi tạo giá trị mặc định bằng 0 cho mỗi ngày trong tháng
            daily_data = {day: {'counting': 0, 'sap_qty': 0} for day in range(1, days_in_month + 1)}

            # Lấy dữ liệu cho mỗi máy (Name)
            for sub_rows2 in rows2:
                if sub_rows2['Name'] == name:
                    day = sub_rows2['belong_to'].day
                    daily_data[day]['counting'] = sub_rows2['counting']
                    daily_data[day]['sap_qty'] = sub_rows2['sap_qty']

            # Thêm dữ liệu của từng ngày vào danh sách đếm và sap qty
            for day in days:
                sub_data_counting.append(daily_data[day]['counting'])
                sub_data_sap_qty.append(daily_data[day]['sap_qty'])

            gap = [b - a for a, b in zip(sub_data_counting, sub_data_sap_qty)]
            gap_rate = [((b - a)/a)*100 if a!=0 else 0 for a, b in zip(sub_data_counting, sub_data_sap_qty)]

            # Format
            sub_data_counting = [f"{a // 1000:,} K" for a in sub_data_counting]
            sub_data_sap_qty = [f"{a // 1000:,} K" for a in sub_data_sap_qty]
            gap = [f"{a // 1000:,} K" for a in gap]
            gap_rate = [f"{a:.1f}%" if a != 0 else "0%" for a in gap_rate]

            data_table.append({"mach": f"{split_name}C", "data_type": "COUNTING", "data": sub_data_counting})
            data_table.append({"mach": f"{split_name}S", "data_type": "SAP", "data": sub_data_sap_qty})
            data_table.append({"mach": split_name, "data_type": "GAP", "data": gap})
            data_table.append({"mach": split_name, "data_type": "GAP_RATE", "data": gap_rate})

    return render(request, 'mes/monthly_check.html', locals())

def test(request):
    return render(request, 'mes/test.html', locals())