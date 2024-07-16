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
    CustomerName,CustomerPartNo,AQL,w.PlanQty,u.NormalizedUserName,FORMAT(u.CreationTime, 'yyyy/MM/dd HH:mm:ss') as CreationTime
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
    q.InspectionValue,q.Lower_InspectionValue,q.InspectionStatus, q.InspectionUnit,q.DefectCode, FORMAT(q.CreationTime, 'yyyy/MM/dd HH:mm:ss') as CreationTime
    from [PMGMES].[dbo].[PMG_MES_RunCard] r
    LEFT JOIN [PMGMES].[dbo].[PMG_MES_WorkOrder] w on r.WorkOrderId = w.id
    LEFT JOIN [PMGMES].[dbo].[PMG_MES_IPQCInspectingRecord] q on q.RunCardId = r.id
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

def index(request):
    return render(request, 'mes/index.html')

