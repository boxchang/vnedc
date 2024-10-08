import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import socket
from datetime import datetime, timedelta
from jobs.database import scada_database, tgm_database, tgm_gdnbr_database, tgm_gdpvc_database


class TGM2MES(object):
    path = os.path.dirname(os.path.abspath(__file__))
    last_time_file = os.path.join(path, "last_time.config")
    tgmdb = None

    def __init__(self, plant):
        self.plant = plant
        if plant == 'VN_GD_NBR':
            self.tgmdb = tgm_gdnbr_database()
        if plant == 'VN_GD_PVC':
            self.tgmdb = tgm_gdpvc_database()

    def execute(self):
        self.last_time = self.get_last_time() - timedelta(minutes=2)  # 程式的最後的執行時間再往前兩分鐘
        self.save_exec_time()

        records = self.get_measure_files()
        for record in records:
            print(record['FILE_NAME'])

            # if record['FILE_NAME'] == "GN247080L6":
            #     print("")

            data = self.get_measure_data(record['FILE_NAME'])
            if data:
                print("Insert Data {LOT_NUMBER}".format(LOT_NUMBER=record['FILE_NAME']))
                self.insert_mes(data)



    def get_measure_files(self):
        sql = """select * from MEASURE_FILE"""
        records = self.tgmdb.select_sql_dict(sql)
        return records

    def get_measure_data(self, LOT_NUMBER):
        cuff_count = 0
        finger_count = 0

        if self.last_time != "":
            sql_condition = "and data_datetime > '{last_time}'".format(last_time=self.last_time)
        else:
            sql_condition = ""

        sql = """SELECT file_name, item_name, data_val
                 FROM [MEASURE_DATA] d, [MEASURE_ITEM] i
                 where i.ITEM_ID = d.ITEM_ID and file_name = '{LOT_NUMBER}' {sql_condition}
                 order by data_datetime desc, DATA_ID desc """\
            .format(LOT_NUMBER=LOT_NUMBER, last_time=self.last_time, sql_condition=sql_condition)
        records = self.tgmdb.select_sql_dict(sql)

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


        db = scada_database()
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



def main():
    LIST = ['VN_GD_NBR', 'VN_GD_PVC']

    # 检查参数数量
    if len(sys.argv) < 2:
        print("Usage: python prog.py <VN_GD_NBR/VN_GD_PVC>")
        sys.exit(1)

    # 获取参数
    param1 = sys.argv[1]

    if param1 not in LIST:
        print("Parameter1 should be VN_GD_NBR/VN_GD_PVC")
        sys.exit(1)

    tgm2mes = TGM2MES(param1)
    tgm2mes.execute()


if __name__ == "__main__":
    main()