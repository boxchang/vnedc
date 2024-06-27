import os
import pyodbc
import socket
from datetime import datetime, timedelta

from jobs.database import sgada_database, tgm_database


class MES2TGM(object):
    data_date = ""

    def __init__(self, data_date):
        self.data_date = data_date

    def get_thickness_value(self, data_date):
        start_date = data_date
        end_date = (datetime.strptime(data_date, '%Y-%m-%d')+timedelta(days=1)).strftime('%Y-%m-%d')

        db = sgada_database()
        conn = db.create_sgada_connection()

        # 連接到SQL Server
        cursor = conn.cursor()

        # 設定存儲過程名稱和參數
        procedure_name = '[dbo].[SP_GetRunCard]'

        # 呼叫存儲過程並獲取查詢結果
        cursor.execute(f"{{CALL {procedure_name} (?, ?)}}", start_date, end_date)
        rows = cursor.fetchall()

        # 關閉連接
        cursor.close()
        conn.close()
        return rows


    def get_file_list(self, data_date):
        data_date = data_date.replace('-', '/')
        db = tgm_database()
        sql = """select * from MEASURE_FILE where FILE_BULID_DAY='{FILE_BULID_DAY}'""".format(FILE_BULID_DAY=data_date)
        records = db.select_sql_dict(sql)
        list = [record['FILE_NAME'] for record in records]
        return list


    def execute(self):

        runcards = self.get_thickness_value(self.data_date)
        files = self.get_file_list(self.data_date)
        for runcard in runcards:
            lot_number = runcard[0]
            if lot_number not in files:  # 沒有資料才塞
                # MEASURE_FILE
                self.insert_measure_file(lot_number)

                file_id = self.get_file_id(lot_number)

                if file_id:
                    # MEASURE_ITEM
                    self.insert_measure_item(file_id, 'Cuff', lot_number, 4, 1)  # 袖
                    self.insert_measure_item(file_id, 'Finger', lot_number, 4, 1)  # 指腹
                    self.insert_measure_item(file_id, 'Palm', lot_number, 4, 1)  # 掌
                    self.insert_measure_item(file_id, 'Roll', lot_number, 4, 1)  # 卷唇
                    self.insert_measure_item(file_id, 'FingerTip', lot_number, 4, 2)  # 指尖

                    # FILE_INFO
                    self.insert_file_info(file_id, 'Lot Number', lot_number)

    def insert_measure_file(self, LOT_NUMBER):
        db = tgm_database()
        today = datetime.today().strftime('%Y/%m/%d')
        sql = """insert into MEASURE_FILE(FILE_NAME, MEMO, FILE_BULID_DAY, CONV_TYPE, CONV_AUTO, DEFAULT_LOT) 
                 Values ('{LOT_NUMBER}', '', '{FILE_BULID_DAY}', 0, 0, '{LOT_NUMBER}')"""\
            .format(LOT_NUMBER=LOT_NUMBER, FILE_BULID_DAY=today)
        print(sql)
        db.execute_sql(sql)

    def get_file_id(self, LOT_NUMBER):
        file_id = ""
        db = tgm_database()
        sql = "select * from MEASURE_FILE where FILE_NAME='{LOT_NUMBER}'".format(LOT_NUMBER=LOT_NUMBER)
        record = db.select_sql_dict(sql)
        if record:
            file_id = record[0]["FILE_ID"]
        return file_id

    def insert_measure_item(self, FILE_ID, ITEM_NAME, LOT_NUMBER, COM_PORT, CHANNEL):
        db = tgm_database()
        today = datetime.today().strftime('%Y/%m/%d')
        sql = """insert into MEASURE_ITEM(FILE_ID, ITEM_NAME, MEMO, DP, UNIT, COM, CH, ITEM_BULID_DAY, FILE_NAME) 
                 Values ('{FILE_ID}', '{ITEM_NAME}', '', 2, 'mm', {COM_PORT}, {CHANNEL}, '{ITEM_BULID_DAY}', '{FILE_NAME}')"""\
            .format(FILE_ID=FILE_ID, ITEM_NAME=ITEM_NAME, COM_PORT=COM_PORT, CHANNEL=CHANNEL, ITEM_BULID_DAY=today, FILE_NAME=LOT_NUMBER)
        db.execute_sql(sql)

    def insert_file_info(self, FILE_ID, FILE_INFO_NAME, FILE_INFO_VALUE):
        db = tgm_database()
        sql = """insert into FILE_INFO(FILE_ID, FILE_INFO_NAME, FILE_INFO_VAL) 
                         Values ({FILE_ID}, '{FILE_INFO_NAME}', '{FILE_INFO_VALUE}')""" \
            .format(FILE_ID=FILE_ID, FILE_INFO_NAME=FILE_INFO_NAME, FILE_INFO_VALUE=FILE_INFO_VALUE)
        db.execute_sql(sql)



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


data_date = '2024-06-27'
# thickness = MES2TGM(data_date)
# thickness.execute()

tgm2mes = TGM2MES()
tgm2mes.execute()