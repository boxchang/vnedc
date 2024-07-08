import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import socket
from datetime import datetime, timedelta
from jobs.database import sgada_database, tgm_database


class TGM2MES(object):
    path = os.path.dirname(os.path.abspath(__file__))
    last_time_file = os.path.join(path, "last_time.config")

    def execute(self):
        self.last_time = self.get_last_time() - timedelta(minutes=2)  # 程式的最後的執行時間再往前兩分鐘
        records = self.get_measure_files()
        for record in records:
            print(record['FILE_NAME'])

            # if record['FILE_NAME'] == "GN247080L6":
            #     print("")

            data = self.get_measure_data(record['FILE_NAME'])
            if data:
                print("Insert Data {LOT_NUMBER}".format(LOT_NUMBER=record['FILE_NAME']))
                self.insert_mes(data)
        self.save_exec_time()
        self.clean_data()

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

        sql = """SELECT file_name, item_name, data_val
                 FROM [TGM].[dbo].[MEASURE_DATA] d, MEASURE_ITEM i 
                 where i.ITEM_ID = d.ITEM_ID and file_name = '{LOT_NUMBER}' {sql_condition}
                 order by data_datetime desc"""\
            .format(LOT_NUMBER=LOT_NUMBER, last_time=self.last_time, sql_condition=sql_condition)
        records = db.select_sql_dict(sql)

        # Cuff的量測位置有4個數值，Finger有1個數值，滿足才回傳
        for record in records:
            if record["item_name"] == " 1.Cuon bien 2.Co tay 3.Ban tay 4.Ngon tay":
                cuff_count += 1
            if record["item_name"] == "5.D Ngon tay":
                finger_count += 1
        if cuff_count >= 4 and finger_count >= 1:
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
        item1_count = 1
        item2_count = 1
        for record in records:
            if record["item_name"] == " 1.Cuon bien 2.Co tay 3.Ban tay 4.Ngon tay" and item1_count < 5:
                cuff_list.append(record["data_val"])
                item1_count += 1
            if record["item_name"] == "5.D Ngon tay"  and item2_count < 2:
                finger_tip = record["data_val"]
                item2_count += 1


        roll = cuff_list[3]
        cuff = cuff_list[2]
        palm = cuff_list[1]
        finger = cuff_list[0]

        # 指、指尖要除以2
        finger = round(float(finger)/2, 2)
        finger_tip = round(float(finger_tip)/2, 3)

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

    # Runcard主檔的資料超過一天就刪除，假定Runcard產生出來一天內會做完
    def clean_data(self):
        db = tgm_database()
        sql = """
            SELECT file_name, count(*) number
            FROM [TGM].[dbo].[MEASURE_FILE] a, [TGM].[dbo].[MEASURE_DATA] b 
            where a.FILE_NAME = b.LOT_NUMBER and data_datetime < getdate()-1
            group by FILE_NAME having count(*) > 4
        """
        records = db.select_sql_dict(sql)

        for record in records:
            lot_number = record["file_name"]

            self.delete_measure_item(db, lot_number)
            self.delete_file_info(db, lot_number)
            self.delete_measure_data(db, lot_number)
            self.delete_measure_file(db, lot_number)


    def delete_measure_file(self, db, file_name):
        sql = "delete from measure_file where file_name = '{file_name}'".format(file_name=file_name)
        db.execute_sql(sql)

    def delete_measure_item(self, db, file_name):
        sql = "delete from measure_item where file_name='{file_name}'".format(file_name=file_name)
        db.execute_sql(sql)

    def delete_file_info(self, db, file_name):
        sql = "delete from file_info where file_info_val = '{file_name}'".format(file_name=file_name)
        db.execute_sql(sql)

    def delete_measure_data(self, db, file_name):
        sql = """
            delete FROM [TGM].[dbo].[MEASURE_DATA] 
            where DATA_DATETIME < getdate()-90 and LOT_NUMBER = '{LOT_NUMBER}'
        """
        db.execute_sql(sql)

tgm2mes = TGM2MES()
tgm2mes.execute()