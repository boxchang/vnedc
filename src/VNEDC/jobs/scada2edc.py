import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from jobs.database import vnedc_database, scada_database, gd_mes_database, lk_mes_database
from datetime import datetime, timedelta


class SGADA2EDC(object):
    start_date = ""
    end_date = ""
    debug = False
    mes_db = None
    vnedc_db = None

    def __init__(self, start_date, end_date, debug, plant):
        if plant == "GD":
            self.mes_db = gd_mes_database()
        elif plant == "LK":
            self.mes_db = lk_mes_database()
        self.vnedc_db = vnedc_database()
        self.start_date = start_date
        self.end_date = end_date
        self.debug = debug

    def execute(self):

        sql = """SELECT * FROM [VNEDC].[dbo].[collection_parameterdefine] where auto_value = 1"""
        defines = self.vnedc_db.select_sql_dict(sql)

        tmp_start_date = datetime.strptime(start_date, '%Y-%m-%d')
        tmp_end_date = datetime.strptime(end_date, '%Y-%m-%d')
        while tmp_start_date <= tmp_end_date:
            data_date = tmp_start_date.strftime('%Y-%m-%d')
            self.convert_data(data_date, defines)
            tmp_start_date += timedelta(days=1)


    def convert_data(self, data_date, defines):

        if self.debug:
            times = ["00", "06", "12", "18"]
        else:
            now = datetime.now()
            current_hour = now.hour

            if 0 <= current_hour < 6:
                times = ["00"]
            elif 6 <= current_hour < 12:
                times = ["06"]
            elif 12 <= current_hour < 18:
                times = ["12"]
            else:
                times = ["18"]

        for define in defines:
            try:
                scada_table = define['scada_table']
                scada_column = define['scada_column']
                for time in times:
                    datetime_s = "{date} {time}:00".format(date=data_date, time=time)
                    datetime_e = "{date} {time}:10".format(date=data_date, time=time)
                    sql = f"""select {scada_column} from {scada_table} where datetime >= CONVERT(DATETIME, '{datetime_s}') and datetime <= CONVERT(DATETIME, '{datetime_e}')"""
                    records = self.mes_db.select_sql_dict(sql)

                    if records:
                        record = records[0]
                        plant = define["plant_id"]
                        mach = define["mach_id"]
                        process_type = define["process_type_id"]
                        parameter_name = define["parameter_name"]
                        parameter_value = float(format(record[define["scada_column"]], ".4f"))

                        if not self.isVNEDCExisted(data_date, plant, mach, process_type, time, parameter_name):
                            self.insert_vnedc(data_date, plant, mach, process_type, time, parameter_name, parameter_value)
            except Exception as e:
                print(e)


    def isVNEDCExisted(self, data_date, plant, mach, process_type, time, parameter_name):
        result = False

        sql = """select * from collection_parametervalue 
                 where plant_id='{plant}' and mach_id='{mach}' and data_date='{data_date}' and data_time='{data_time}' 
                 and process_type='{process_type}' and parameter_name='{parameter_name}' """ \
            .format(plant=plant, mach=mach, data_date=data_date, process_type=process_type,
                    parameter_name=parameter_name, data_time=time)
        # print(sql)
        records = self.vnedc_db.select_sql_dict(sql)
        if records:
            result = True
        return result

    def insert_vnedc(self, data_date, plant, mach, process_type, time, parameter_name, parameter_value):

        sql = """insert into collection_parametervalue(data_date, plant_id, mach_id, process_type, data_time, parameter_name, parameter_value, create_at, update_at, create_by_id, update_by_id) 
                                Values('{date_date}', '{plant}', '{mach}', '{process_type}', '{data_time}', '{parameter_name}', {parameter_value}, GETDATE(), GETDATE(), 1, 1)""" \
            .format(date_date=data_date, plant=plant, mach=mach, process_type=process_type, data_time=time, parameter_name=parameter_name, parameter_value=parameter_value)
        print(sql)
        self.vnedc_db.execute_sql(sql)


debug = False
start_date = datetime.today().strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')
# start_date = "2024-07-25"
# end_date = "2024-07-26"

plant_list = ['LK', 'GD']

for plant in plant_list:
    sgada = SGADA2EDC(start_date, end_date, debug, plant)
    sgada.execute()