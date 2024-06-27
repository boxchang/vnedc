import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(os.path.split(curPath)[0])[0]
sys.path.append(rootPath)

import socket
from datetime import datetime
from jobs.database import sgada_database, tgm_database


class TGM2MES(object):
    path = os.path.dirname(os.path.abspath(__file__))
    last_time_file = os.path.join(path, "last_time.config")

    def execute(self):
        self.last_time = self.get_last_time()
        records = self.get_measure_files()
        for record in records:
            data = self.get_measure_data(record['FILE_NAME'])
            if data:
                self.insert_mes(data)
        self.save_exec_time()

    def get_measure_files(self):
        db = tgm_database()
        sql = """select * from MEASURE_FILE"""
        records = db.select_sql_dict(sql)
        return records

    def get_measure_data(self, LOT_NUMBER):
        cuff_count = 0
        finger_count = 0
        db = tgm_database()

        if self.last_time != "":
            sql_condition = "and data_datetime > '{last_time}'".format(last_time=self.last_time)
        else:
            sql_condition = ""

        sql = """SELECT top(5) file_name, item_name, data_val
                 FROM [TGM].[dbo].[MEASURE_DATA] d, MEASURE_ITEM i 
                 where i.ITEM_ID = d.ITEM_ID and file_name = '{LOT_NUMBER}' {sql_condition}
                 order by data_datetime desc"""\
            .format(LOT_NUMBER=LOT_NUMBER, last_time=self.last_time, sql_condition=sql_condition)
        records = db.select_sql_dict(sql)

        # Cuff的量測位置有4個數值，Finger有1個數值，滿足才回傳
        for record in records:
            if record["item_name"] == "Cuff":
                cuff_count += 1
            if record["item_name"] == "Finger":
                finger_count += 1
        if cuff_count == 4 and finger_count == 1:
            return records
        else:
            return ""

    def insert_mes(self, records):
        # CH1厚度計(5mm) : 卷唇厚度Roll/袖口厚度Cuff/掌厚度Palm/指腹厚度Finger
        # CH2厚度計(10mm) : 指尖厚度FingerTip
        # [dbo].[SP_AddTnicknessData]
        #   @RunCardId varchar(64),
        # 	@DeviceId nvarchar(64),
        # 	@Roll  decimal (8, 3) ,
        # 	@Cuff  decimal (8, 3) ,
        # 	@Palm decimal (8, 3) ,
        # 	@Finger decimal (8, 3) ,
        # 	@FingerTip decimal (8, 3)

        # 獲取本機的主機名稱
        hostname = socket.gethostname()

        # 獲取本機的IP地址
        local_ip = socket.gethostbyname(hostname)


        db = sgada_database()
        conn = db.create_sgada_connection()
        cursor = conn.cursor()
        procedure_name = '[dbo].[SP_AddTnicknessData]'

        cuff_list = []
        finger_tip = ""
        for record in records:
            if record["item_name"] == "Cuff":
                cuff_list.append(record["data_val"])
            if record["item_name"] == "Finger":
                finger_tip = record["data_val"]

        roll = cuff_list[0]
        cuff = cuff_list[1]
        palm = cuff_list[2]
        finger = cuff_list[3]

        # 呼叫存儲過程並獲取查詢結果
        cursor.execute(f"EXEC {procedure_name} ?, ?, ?, ?, ?, ?, ?", records[0]['file_name'], local_ip, roll, cuff, palm, finger, finger_tip)
        conn.commit()

        # 關閉連接
        cursor.close()
        conn.close()


    def get_last_time(self):
        if os.path.exists(self.last_time_file):
            with open(self.last_time_file, 'r') as file:
                last_run_time = file.read().strip()
                if last_run_time:
                    last_run_time = datetime.strptime(last_run_time, '%Y-%m-%d %H:%M:%S')
        else:
            last_run_time = None
        return last_run_time


    def save_exec_time(self):
        current_time = datetime.now()
        with open(self.last_time_file, 'w') as file:
            file.write(current_time.strftime('%Y-%m-%d %H:%M:%S'))

tgm2mes = TGM2MES()
tgm2mes.execute()