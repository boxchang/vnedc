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

    # 取得要作業的Runcard資料，批號、廠、Com port
    def get_runcard_list(self, data_date):
        start_date = data_date
        end_date = (datetime.strptime(data_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

        db = tgm_database()
        sql = """
        select  distinct RunCardId, WorkCenterTypeName,(case WorkCenterTypeName when 'NBR' then 9 when 'PVC' then 7 end) comport
        from PMGMES.[dbo].[PMG_MES_RunCard_IPQCInspectIOptionMapping] t, [PMGMES].[dbo].[PMG_MES_RunCard] r
		WITH(NOLOCK)
		where GroupType='HAND' and t.RunCardId = r.Id
		and  t.CreationTime between  '{start_date}' and '{end_date}'
        """.format(start_date=start_date, end_date=end_date)
        records = db.select_sql_dict(sql)
        return records

    # 先撈一版資料，用來比對資料是否存在
    def get_file_list(self, data_date):
        data_date = data_date.replace('-', '/')
        db = tgm_database()
        sql = """select * from MEASURE_FILE where FILE_BULID_DAY='{FILE_BULID_DAY}'""".format(FILE_BULID_DAY=data_date)
        records = db.select_sql_dict(sql)
        list = [record['FILE_NAME'] for record in records]
        return list

    # 執行主Function
    def execute(self):
        # 從MES取得Runcard批號
        runcards = self.get_runcard_list(self.data_date)

        # 撈取量測主檔
        files = self.get_file_list(self.data_date)
        for runcard in runcards:
            lot_number = runcard['RunCardId']
            plant = runcard['WorkCenterTypeName']
            comport = runcard['comport']
            if lot_number not in files:  # 沒有資料才塞
                # MEASURE_FILE
                self.insert_measure_file(lot_number)

                # 取得MEASURE FILE主檔的File ID
                file_id = self.get_file_id(lot_number)

                if file_id:
                    # MEASURE_ITEM
                    self.insert_measure_item(file_id, ' 1.Cuon bien 2.Co tay 3.Ban tay 4.Ngon tay', lot_number, comport, 1)  # 卷唇
                    self.insert_measure_item(file_id, '5.D Ngon tay', lot_number, comport, 2)  # 指尖

                    # FILE_INFO
                    self.insert_file_info(file_id, 'Lot Number', lot_number)
                    self.insert_file_info(file_id, 'Plant', plant)

    # 新增量測主檔
    def insert_measure_file(self, LOT_NUMBER):
        db = tgm_database()
        today = datetime.today().strftime('%Y/%m/%d')
        sql = """insert into MEASURE_FILE(FILE_NAME, MEMO, FILE_BULID_DAY, CONV_TYPE, CONV_AUTO, DEFAULT_LOT) 
                 Values ('{LOT_NUMBER}', '', '{FILE_BULID_DAY}', 0, 0, '{LOT_NUMBER}')""" \
            .format(LOT_NUMBER=LOT_NUMBER, FILE_BULID_DAY=today)
        print(sql)
        db.execute_sql(sql)

    # 取得量測主檔
    def get_file_id(self, LOT_NUMBER):
        file_id = ""
        db = tgm_database()
        sql = "select * from MEASURE_FILE where FILE_NAME='{LOT_NUMBER}'".format(LOT_NUMBER=LOT_NUMBER)
        record = db.select_sql_dict(sql)
        if record:
            file_id = record[0]["FILE_ID"]
        return file_id

    # 新增量測項目
    def insert_measure_item(self, FILE_ID, ITEM_NAME, LOT_NUMBER, COM_PORT, CHANNEL):
        db = tgm_database()
        today = datetime.today().strftime('%Y/%m/%d')
        decimal = 2 # 小數位數
        sql = """insert into MEASURE_ITEM(FILE_ID, ITEM_NAME, MEMO, DP, UNIT, COM, CH, ITEM_BULID_DAY, FILE_NAME) 
                 Values ('{FILE_ID}', '{ITEM_NAME}', '', {decimal}, 'mm', {COM_PORT}, {CHANNEL}, '{ITEM_BULID_DAY}', '{FILE_NAME}')""" \
            .format(FILE_ID=FILE_ID, ITEM_NAME=ITEM_NAME, COM_PORT=COM_PORT, CHANNEL=CHANNEL,
                    ITEM_BULID_DAY=today, FILE_NAME=LOT_NUMBER, decimal=decimal)
        db.execute_sql(sql)

    # 新增量測主檔資料
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