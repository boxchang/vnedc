import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from datetime import datetime, timedelta
from jobs.database import sgada_database, tgm_database


class MES2TGM(object):
    data_date = ""

    def __init__(self, data_date):
        self.data_date = data_date

    def get_thickness_value(self, data_date):
        start_date = data_date
        end_date = (datetime.strptime(data_date, '%Y-%m-%d' ) +timedelta(days=1)).strftime('%Y-%m-%d')

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

    # 先撈一版資料，用來比對資料是否存在
    def get_file_list(self, data_date):
        data_date = data_date.replace('-', '/')
        db = tgm_database()
        sql = """select * from MEASURE_FILE where FILE_BULID_DAY='{FILE_BULID_DAY}'""".format(FILE_BULID_DAY=data_date)
        records = db.select_sql_dict(sql)
        list = [record['FILE_NAME'] for record in records]
        return list


    def execute(self):
        # 從MES取得Runcard批號
        runcards = self.get_thickness_value(self.data_date)

        # 撈取量測主檔
        files = self.get_file_list(self.data_date)
        for runcard in runcards:
            lot_number = runcard[0]
            if lot_number not in files:  # 沒有資料才塞
                # MEASURE_FILE
                self.insert_measure_file(lot_number)

                # 取得MEASURE FILE主檔的File ID
                file_id = self.get_file_id(lot_number)

                if file_id:
                    # MEASURE_ITEM
                    self.insert_measure_item(file_id, ' 1.Cuon bien 2.Co tay 3.Ban tay 4.Ngon tay', lot_number, 5, 1)  # 卷唇
                    #self.insert_measure_item(file_id, 'Cuff', lot_number, 4, 1)  # 袖
                    #self.insert_measure_item(file_id, 'Palm', lot_number, 4, 1)  # 掌
                    #self.insert_measure_item(file_id, 'Finger', lot_number, 4, 1)  # 指腹
                    self.insert_measure_item(file_id, '5.D Ngon tay', lot_number, 4, 2)  # 指尖

                    # FILE_INFO
                    self.insert_file_info(file_id, 'Lot Number', lot_number)

    def insert_measure_file(self, LOT_NUMBER):
        db = tgm_database()
        today = datetime.today().strftime('%Y/%m/%d')
        sql = """insert into MEASURE_FILE(FILE_NAME, MEMO, FILE_BULID_DAY, CONV_TYPE, CONV_AUTO, DEFAULT_LOT) 
                 Values ('{LOT_NUMBER}', '', '{FILE_BULID_DAY}', 0, 0, '{LOT_NUMBER}')""" \
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
                 Values ('{FILE_ID}', '{ITEM_NAME}', '', 2, 'mm', {COM_PORT}, {CHANNEL}, '{ITEM_BULID_DAY}', '{FILE_NAME}')""" \
            .format(FILE_ID=FILE_ID, ITEM_NAME=ITEM_NAME, COM_PORT=COM_PORT, CHANNEL=CHANNEL, ITEM_BULID_DAY=today, FILE_NAME=LOT_NUMBER)
        db.execute_sql(sql)

    def insert_file_info(self, FILE_ID, FILE_INFO_NAME, FILE_INFO_VALUE):
        db = tgm_database()
        sql = """insert into FILE_INFO(FILE_ID, FILE_INFO_NAME, FILE_INFO_VAL) 
                         Values ({FILE_ID}, '{FILE_INFO_NAME}', '{FILE_INFO_VALUE}')""" \
            .format(FILE_ID=FILE_ID, FILE_INFO_NAME=FILE_INFO_NAME, FILE_INFO_VALUE=FILE_INFO_VALUE)
        db.execute_sql(sql)


data_date = datetime.today().strftime('%Y-%m-%d')
#data_date = '2024-06-27'
thickness = MES2TGM(data_date)
thickness.execute()