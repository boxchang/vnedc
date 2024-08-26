from django.shortcuts import render
from django.http import JsonResponse
from VNEDC.database import mes_database
from datetime import datetime, timedelta


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
    if request.method == 'POST':
        selected_date = request.POST.get('date', '')
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
        dml.Name LIKE '%NBR%'
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
        dml.Name LIKE '%NBR%'
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
            AND dm.Abbreviation LIKE '%NBR%'
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
            cd.CreationTime BETWEEN CONVERT(DATETIME, '{selected_date} 05:30:00', 120) 
                              AND CONVERT(DATETIME, DATEADD(SECOND, -1, CONVERT(DATETIME, DATEADD(DAY, 1, '{selected_date}') + ' 05:30:00', 120)), 120)
            AND cd.MachineName LIKE '%NBR%'
            AND cd.MachineName LIKE '%NBR_CountingMachine%'
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

    machine_names, work_orders, run_cards, machine_data = [], [], [], []
    runcard_stop_hours, runcard_messages = [], []
    machine_data_totals = []
    machine_data_hours, machine_data_messages = [], []
    runcard_modes = []
    iqpc_modes = []
    times = []
    for result1 in results1:
        machine_names.append(result1['MachineName'])
        machine_names = list(dict.fromkeys(machine_names))

    for machine_name in machine_names:
        machine_count = 0
        data_count = 0
        machine_data_total = 0
        rc_exist_hours = []
        for result1 in results1:
            if machine_name == result1['MachineName']:
                if machine_count == 0:
                    work_orders.append(result1['WorkOrderMode'])
                    machine_count = 1

        for result2 in results2:
            if machine_name == result2['MachineName']:
                rc_exist_hours.append(result2['RuncardHour'])
        rc_exist_hours = list(dict.fromkeys(rc_exist_hours))
        expected_time = {f"{i:02}" for i in range(24)}
        run_hour = [f"{int(i):02}" for i in rc_exist_hours if i is not None]
        exist_hours = set(run_hour)

        runcard_missed_hours = expected_time - exist_hours
        runcard_missed_hours = list(runcard_missed_hours)
        runcard_stop_hours.append(runcard_missed_hours)
        for result3 in results3:
            if machine_name == result3['MES_MACHINE']:
                if data_count == 0:
                    machine_data.append(result3['QtyCheck'])
                    data_count = 1
                machine_data_total += float(result3['A1_Qty']) + float(result3['A2_Qty']) + float(result3['B1_Qty']) + float(result3['B2_Qty'])
                machine_data_hours.append(result3['CellCheck'])
                times.append(str(result3['Hour']))
                machine_data_messages.append('Machine: at: ' + str(result3['Hour']) + ':00 -'
                               + '\nA1: ' + str(result3['A1_Qty'])
                               + '\nA2: ' + str(result3['A2_Qty'])
                               + '\nB1: ' + str(result3['B1_Qty'])
                               + '\nB2: ' + str(result3['B2_Qty']))
        machine_data_totals.append(machine_data_total)


    for i in range(len(runcard_stop_hours)):
        if len(runcard_stop_hours[i]) == 0:
            run_cards.append(1)
            runcard_messages.append('Normal')
        else:
            run_cards.append(0)
            runcard_messages.append(f'Runcard lost in : {len(runcard_stop_hours[i])} hours')

    period_times = ['06', '07', '08', '09', '10', '11', '12', '13',
                    '14', '15', '16', '17', '18', '19', '20', '21',
                    '22', '23', '00', '01', '02', '03', '04', '05']

    runcard_data_hours = []
    # print(len(runcard_stop_hours))

    for index in runcard_stop_hours:
        if len(index) == 0:
            runcard_data_hours.extend([1] * 24)
        else:
            for period in period_times:
                count = 0
                for time in index:
                    if float(period) == float(time):
                        count += 1
                if count == 0:
                    runcard_data_hours.append(1)
                elif count == 1:
                    runcard_data_hours.append(0)


    ipqc_data_hours = [[[] for _ in range(24)] for _ in range(14)]
    ipqc_messages = []
    machine_line_index = {f"L{i+1:02}": i for i in range(len(machine_name))}
    period_time_index = {time: i for i, time in enumerate(period_times)}

    for result2 in results2:
        machine = result2['MachineName'].split("_")[-1]
        period = result2['RuncardHour']
        weight = result2['Weight']
        if period is None:
            continue

        period = str(period).zfill(2)
        if period not in period_time_index:
            continue
        if weight is not None:
            weight = float(weight)

        machine_idx = machine_line_index[machine]
        period_idx = period_time_index[period]
        ipqc_data_hours[machine_idx][period_idx].append(weight)


    for index, ipqc_data in enumerate(ipqc_data_hours):
        for hour in ipqc_data:
            if len(hour) == 0:
                iqpc_modes.append(0)
                ipqc_messages.append('NO Runcard !')
            else:
                if None in hour:
                    iqpc_modes.append(0)
                    ipqc_messages.append(str(hour))
                else:
                    iqpc_modes.append(1)
                    ipqc_messages.append(str(hour))

    runcard_hour_messages = []
    for runcard_data_hour in runcard_data_hours:
        if runcard_data_hour == 1:
            runcard_hour_messages.append("Runcard printed")
        else:
            runcard_hour_messages.append("Runcard NOT printed !")

    try:
        new_value_messages = []
        new_runcard_messages = []
        for i in range(336):
            new_value_messages.append('IPQC weight: at: ' + str(times[i]) + ':00 - ' + str(ipqc_messages[i]))
            new_runcard_messages.append('Runcard: at: ' + str(times[i]) + ':00 - ' + str(runcard_hour_messages[i]))
    except:
        pass

    merged_messages,merged_data = [], []
    for i in range(0, 336, 24):
        merged_data.extend(runcard_data_hours[i:i + 24])
        merged_data.extend(iqpc_modes[i:i + 24])
        merged_data.extend(machine_data_hours[i:i + 24])
        merged_messages.extend(new_runcard_messages[i:i + 24])
        merged_messages.extend(new_value_messages[i:i + 24])
        merged_messages.extend(machine_data_messages[i:i + 24])


    print(len(times))
    table_data1 = [merged_data[i:i + 24] for i in range(0, len(merged_data), 24)]
    table_data2 = [merged_messages[i:i + 24] for i in range(0, len(merged_messages), 24)]
    return render(request, 'mes/fast_check.html', locals())

