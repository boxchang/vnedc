import sys
import requests
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from jobs.database import mes_database
from datetime import datetime, timedelta
import time
startDate = datetime.today().date() - timedelta(days=1) #Yesterday %Y-%m-%d
endDate = datetime.today().date() #Today
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #Send message time

#Step 5: Send messages from python to Wecom group
def send_message(msg):
    path = os.path.dirname(os.path.abspath(__file__))
    wecom_file = os.path.join(path, "wecom_key.config")
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

def message():
    send_code = 0
    #Step 5: Send message to Wecom MES group
    machine = ['NBR', 'PVC']
    db = mes_database()
    NBR_details = []
    PVC_details = []
    machine = ['NBR', 'PVC']
    db = mes_database()
    machine_details = {'NBR': [], 'PVC': []}
    for selected_machine in machine:
        missingIPQCStandardValue = []
        missingSCADAStandardValue = []
        
        # Step 1: Find all distinct ProductItems from PMG_MES_WorkOrder
        sql_partNo = f"""
            SELECT DISTINCT PartNo, ProductItem
            FROM [PMGMES].[dbo].[PMG_MES_WorkOrder]
            WHERE CreationTime BETWEEN CONVERT(DATETIME, '{startDate} 06:00:00', 120)
            AND CONVERT(DATETIME, '{endDate} 05:59:59', 120)
            AND SAP_FactoryDescr LIKE '%{selected_machine}%'
        """
        partNoItems = db.select_sql_dict(sql_partNo)
        partNoItems_list = [value['PartNo'] for value in partNoItems]
        productItems = [value['ProductItem'] for value in partNoItems]
        
        # Step 2 & 3: Check for missing IPQC and SCADA standard values
        for index, partNo in enumerate(partNoItems_list):
            sql_ipqc = f"""
                SELECT PartNo FROM [PMGMES].[dbo].[PMG_MES_IPQC{selected_machine}Std] 
                WHERE PartNo = '{partNo}'
            """
            if not db.select_sql_dict(sql_ipqc):
                missingIPQCStandardValue.append([partNo, productItems[index]])

            sql_scada = f"""
                SELECT PartNo FROM [PMGMES].[dbo].[PMG_MES_{selected_machine}_SCADA_Std] 
                WHERE PartNo = '{partNo}'
            """
            if not db.select_sql_dict(sql_scada):
                missingSCADAStandardValue.append([partNo, productItems[index]])
        
        machine_details[selected_machine] = [missingIPQCStandardValue, missingSCADAStandardValue]
    NBR_details = machine_details['NBR']
    PVC_details = machine_details['PVC']

    #Step 4: Create message format before sending through WeCom
    wecomMessage = f'''{current_time}\n\nWarning of missing IPQC and SCADA standard values.\n\nChecking from {startDate} 06:00:00 to {endDate} 05:59:59.\n\n'''
    if any(NBR_details):
        wecomMessage += 'Machine line: NBR\n'
        if NBR_details[0]:
            wecomMessage += '- Need to set IPQC standard values on PartNo:\n' + ''.join(f'+ {item[0]} ( {item[1]} )\n' for item in NBR_details[0])
        if NBR_details[1]:
            wecomMessage += '- Need to set SCADA standard values on PartNo:\n' + ''.join(f'+ {item[0]} ( {item[1]} )\n' for item in NBR_details[1])
        send_code = 1        
    if any(PVC_details):
        wecomMessage += 'Machine line: PVC\n'
        if PVC_details[0]:
            wecomMessage += '- Need to set IPQC standard values on PartNo:\n' + ''.join(f'+ {item[0]} ( {item[1]} )\n' for item in PVC_details[0])
        if PVC_details[1]:
            wecomMessage += '- Need to set SCADA standard values on PartNo:\n' + ''.join(f'+ {item[0]} ( {item[1]} )\n' for item in PVC_details[1])
        send_code = 1        
    return send_code, wecomMessage

if __name__ == "__main__":
    start = time.time()
    code, msg = message()
    if code == 1: #If send code == 1, it means there's standard value missing and need to be sent alert, else it means nothing needs to be sent
        response = send_message(msg)
        print(response)
        print(msg)
    end = time.time()
    print(f'Execution time: {end - start:.3f} seconds')
