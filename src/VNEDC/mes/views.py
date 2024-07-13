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

    if 'RunCardId' in request.GET and request.GET['RunCardId']:
        filters.append("RunCardId LIKE %s")
        params.append(f"%{request.GET['RunCardId']}%")

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
    WITH IPQC AS (
SELECT InspectionDate,r.WorkOrderId, Period,RunCardId, WorkCenterTypeName, MachineName,LineName,
	MAX(CASE WHEN p.OptionName = 'Roll' THEN p.InspectionValue END) AS Roll,
    MAX(CASE WHEN p.OptionName = 'Cuff' THEN p.InspectionValue END) AS Cuff,
    MAX(CASE WHEN p.OptionName = 'Palm' THEN p.InspectionValue END) AS Palm,
	MAX(CASE WHEN p.OptionName = 'Finger' THEN p.InspectionValue END) AS Finger,
	MAX(CASE WHEN p.OptionName = 'FingerTip' THEN p.InspectionValue END) AS FingerTip,
	MAX(CASE WHEN p.OptionName = 'Tensile' THEN p.InspectionValue END) AS Tensile,
	MAX(CASE WHEN p.OptionName = 'Elongation' THEN p.InspectionValue END) AS Elongation
  FROM [PMGMES].[dbo].[PMG_MES_RunCard] r
  LEFT JOIN 
    [PMGMES].[dbo].[PMG_MES_IPQCInspectingRecord] p ON r.Id = p.RunCardId
  GROUP BY 
    InspectionDate,r.WorkOrderId, Period,RunCardId, WorkCenterTypeName, MachineName,LineName COLLATE Chinese_Taiwan_Stroke_CI_AS
),
MeasureData AS (
  SELECT 
        LOT_NUMBER,
        DATA_ID,
        DATA_VAL,
        ROW_NUMBER() OVER (PARTITION BY LOT_NUMBER COLLATE Chinese_Taiwan_Stroke_CI_AS ORDER BY DATA_ID DESC ) AS rn
    FROM 
        TGM.dbo.MEASURE_DATA
)
SELECT 
InspectionDate,WorkOrderId, Period,RunCardId, WorkCenterTypeName, MachineName,LineName,
    ipqc.RunCardId,
    ipqc.Roll,
	MAX(CASE WHEN md.rn = 5 THEN md.DATA_VAL END) AS measure_5,
    ipqc.Cuff,
	MAX(CASE WHEN md.rn = 4 THEN md.DATA_VAL END) AS measure_4,
	ipqc.Palm,
	MAX(CASE WHEN md.rn = 3 THEN md.DATA_VAL END) AS measure_3,
    ipqc.Finger,
	MAX(CASE WHEN md.rn = 2 THEN ROUND(TRY_CAST(md.DATA_VAL AS FLOAT) / 2, 2) END) AS measure_2,
	ipqc.FingerTip,
    MAX(CASE WHEN md.rn = 1 THEN ROUND(TRY_CAST(md.DATA_VAL AS FLOAT) / 2, 3) END) AS measure_1
FROM 
    IPQC ipqc
LEFT OUTER JOIN 
    MeasureData md ON ipqc.RunCardId COLLATE Chinese_Taiwan_Stroke_CI_AS = md.lot_number COLLATE Chinese_Taiwan_Stroke_CI_AS
GROUP BY 
InspectionDate,WorkOrderId, Period,RunCardId, WorkCenterTypeName, MachineName,LineName,
    ipqc.RunCardId,
    ipqc.Roll,
    ipqc.Cuff,
	ipqc.Palm,
    ipqc.Finger,
	ipqc.FingerTip 
    """
    if filters:
        sql += " HAVING " + " AND ".join(filters)

    # 添加默认排序条件
    sql += " ORDER BY ipqc.InspectionDate DESC, ipqc.WorkOrderId, TRY_CAST(ipqc.Period AS INT)"

    db = mes_database()
    work_orders = db.select_sql_dict_param(sql, params)

    return JsonResponse(work_orders, safe=False)


def index(request):
    return render(request, 'mes/index.html')

