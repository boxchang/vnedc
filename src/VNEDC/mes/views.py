from django.shortcuts import render
from django.http import JsonResponse
from VNEDC.database import mes_database
from datetime import datetime, timedelta
import json
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

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
    selected_date = ''
    selected_machine = ''

    if request.method == 'POST':
        selected_date = request.POST.get('date', '')
        selected_machine = request.POST.get('machine', 'PVC')  # Get the selected machine, default to 'PVC' if not set

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
 WITH Machine AS (
    SELECT * 
    FROM [PMGMES].[dbo].[PMG_DML_DataModelList] dl 
    WHERE dl.DataModelTypeId = 'DMT000003'
),

InspectionCheck AS (
    SELECT 
        dml.Id AS MachineID,
        dml.Name AS MachineName,
        wo.Id AS WorkOrderId,
        woi.LineId AS LineId,
        rc.Id AS RuncardId,
        rc.InspectionDate AS RuncardDate,
        rc.Period AS RuncardHour,
        qc.InspectionValue AS Weight,
        -- RunCardMode Calculation
        CASE 
            WHEN (
                SELECT COUNT(DISTINCT rc_sub.Period)
                FROM [PMGMES].[dbo].[PMG_MES_RunCard] rc_sub
                WHERE rc_sub.MachineId = dml.Id
                  AND rc_sub.WorkOrderId = wo.Id
                  AND rc_sub.InspectionDate BETWEEN '{selected_date}' AND DATEADD(DAY, 1, '{selected_date}') 
            ) = 24 THEN 1
            ELSE 0 
        END AS RunCardMode
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
    LEFT JOIN 
        [PMGMES].[dbo].[PMG_MES_RunCard] rc 
        ON rc.WorkOrderId = wo.Id
        AND rc.MachineId = wo.MachineId
        AND rc.LineName = woi.LineId
        AND (
            (rc.InspectionDate = '{selected_date}' AND rc.Period BETWEEN 6 AND 23) 
            OR 
            (rc.InspectionDate = DATEADD(DAY, 1, '{selected_date}')  AND rc.Period BETWEEN 0 AND 5)
        )
    LEFT JOIN 
        [PMGMES].[dbo].[PMG_MES_IPQCInspectingRecord] qc 
        ON qc.OptionName = 'Weight'
        AND qc.CreationTime BETWEEN CONVERT(DATETIME, '{selected_date} 05:30:00', 120) 
                          AND CONVERT(DATETIME, DATEADD(SECOND, -1, CONVERT(DATETIME, DATEADD(DAY, 1, '{selected_date}') + ' 05:30:00', 120)), 120)
        AND rc.Id = qc.RunCardId
        AND wo.Id = qc.WorkOrderId
    WHERE 
        dml.Name LIKE '%{selected_machine}%'
)

SELECT 
    MachineID,
    MachineName,
    WorkOrderId,
    LineId,
    RuncardId,
    RuncardDate,
    RuncardHour,
    Weight,
    RunCardMode
FROM 
    InspectionCheck
ORDER BY 
    MachineName,
    RuncardDate,
    RuncardHour;

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
                run_card_exist_hours.append(results2_['RuncardHour'])
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
                    if results2_['RuncardId'] is not None:
                        if float(results2_['RuncardHour']) == float(period_time):
                            run_card_mode_24[i * 24 + j] = 1
                            if run_card_messages_24[i * 24 + j] == '':
                                run_card_messages_24[i * 24 + j] = 'Runcard: at: '+ str(period_time) + ':00 ' + '<br>' + '&nbsp;&nbsp;&ndash;' + str(results2_['LineId'] + ': ' + results2_['RuncardId'])
                            else:
                                run_card_messages_24[i * 24 + j] += '<br>' + '&nbsp;&nbsp;&ndash;' + f"{results2_['LineId']}: {results2_['RuncardId']}"
                            found = True
                    if results2_['Weight'] is not None:
                        if float(results2_['RuncardHour']) == float(period_time):
                            run_card_mode_24_2[i * 24 + j] = 1
                            if run_card_messages_24_2[i * 24 + j] == '':
                                run_card_messages_24_2[i * 24 + j] = 'Weight: at: '+ str(period_time) + ':00 ' + '<br>' + '&nbsp;&nbsp;&ndash;' + str(str(results2_['LineId']) + ': ' + str(results2_['Weight']))
                            else:
                                run_card_messages_24_2[i * 24 + j] += '<br>' + '&nbsp;&nbsp;&ndash;' + f"{results2_['LineId']}: {results2_['Weight']}"
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
            elif not results:
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
