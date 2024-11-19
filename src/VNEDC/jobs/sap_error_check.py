import requests
import os
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from jobs.database import mes_database


def send_message(msg):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    wecom_file = os.path.join(path, "static", "wecom", "dt_wecom_key.config")
    url = '' #Add Wecom GD_MES group key
    if os.path.exists(wecom_file):
        with open(wecom_file, 'r') as file:
            url = file.read().strip()

    headers =   {'Content-Type': 'application/json; charset=utf-8'}
    data = {
        "msgtype": "text",
        "text": {
            "content": '',
            # "mentioned_list": ["@all"],
        }
    }
    data["text"]["content"] = msg
    r = requests.post(url, headers=headers, json=data)
    return r.json()

sql = f"""
        SELECT  rc.WorkCenterTypeName, rc.MachineName, wip.WorkOrderId, wip.RunCardId, wipd.LotNo, wipd.ErpSTATUS
        FROM [PMGMES].[dbo].[PMG_MES_WorkInProcessDetail] wipd
        join [PMGMES].[dbo].[PMG_MES_WorkInProcess] wip
        on wip.LotNo = wipd.LotNo
        join [PMGMES].[dbo].[PMG_MES_RunCard] rc
        on rc.id = wip.RunCardId
        where (wipd.CreationTime >= DATEADD(hour, -2, GETDATE())  AND wipd.CreationTime <= DATEADD(hour, -1, GETDATE())  and  wipd.ErpSTATUS is NULL)
        and (wipd.CreationTime >= DATEADD(hour, -1, GETDATE()) AND wipd.CreationTime <= GETDATE()  and wipd.ErpSTATUS = 'E')
        """

db = mes_database()
results = db.select_sql_dict(sql)
if len(results) > 0:
    text1 = "MES to SAP error at LotNo: "
    text2 = [value['LotNo'] for value in results]
    response = send_message(text1+','.join(text2))
    print(text1+','.join(text2))

