from jobs.database import vnedc_database, sgada_database
import datetime

class SgadaInterface:
    def __init__(self, classname=None, start_date=None, end_date=None):
        self.process = classname
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        self.process().run(self.start_date, self.end_date)



class GDNBR:
    config = {"plant": "GDNBR",
              "lines": [
                 {"line": "GDNBR01", "table": "NBR_IntouchData_Machine1",
                  "process": {"type": "Oven",
                  "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20", "A08B08_TEMPERATURE": "T19",
                              "A09B09_TEMPERATURE": "T21",
                              "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26", "A12B12_TEMPERATURE": "T25",
                              "A13B13_TEMPERATURE": "T24",
                              "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR02", "table": "NBR_IntouchData_Machine2",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR03", "table": "NBR_IntouchData_Machine3",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR04", "table": "NBR_IntouchData_Machine4",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR05", "table": "NBR_IntouchData_Machine5",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR06", "table": "NBR_IntouchData_Machine6",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR07", "table": "NBR_IntouchData_Machine7",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR08", "table": "NBR_IntouchData_Machine8",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR09", "table": "NBR_IntouchData_Machine9",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR10", "table": "NBR_IntouchData_Machine10",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR11", "table": "NBR_IntouchData_Machine11",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR12", "table": "NBR_IntouchData_Machine12",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR13", "table": "NBR_IntouchData_Machine13",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                  {"line": "GDNBR14", "table": "NBR_IntouchData_Machine14",
                   "process": {"type": "Oven",
                               "params": {"A06B06_TEMPERATURE": "T18", "A07B07_TEMPERATURE": "T20",
                                          "A08B08_TEMPERATURE": "T19",
                                          "A09B09_TEMPERATURE": "T21",
                                          "A10B10_TEMPERATURE": "T22", "A11B11_TEMPERATURE": "T26",
                                          "A12B12_TEMPERATURE": "T25",
                                          "A13B13_TEMPERATURE": "T24",
                                          "A14B14_TEMPERATURE": "T23"}}},
                 ],
                }

    def __init__(self):
        print("init")


    def run(self, start_date, end_date):
        plant = self.config["plant"]
        print("開始執行{plant}".format(plant=plant))
        for line_info in self.config["lines"]:
            print("目前執行機台{mach}".format(mach=line_info["line"]))
            param_define = self.get_param_define(plant, line_info)
            tmp_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            tmp_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            while tmp_start_date <= tmp_end_date:
                data_date = tmp_start_date.strftime('%Y-%m-%d')
                self.convert_data(data_date, plant, line_info, param_define)
                tmp_start_date += datetime.timedelta(days=1)


    def isParamExist(self, param_define, param):
        result = False
        for define in param_define:
            if define["parameter_name"] == param:
                result = True
                break
        return result



    def convert_data(self, data_date, plant, line, param_define):
        db = sgada_database()
        times = ["00", "06", "12", "18"]
        table = line["table"]
        columns = []
        mapping = {}

        # 檢查轉檔程式的CONFIG的資料是否跟VNEDC的CONFIG一樣
        for config_param in line["process"]["params"]:
            if self.isParamExist(param_define, config_param):
                columns.append(line["process"]["params"][config_param])
                mapping[line["process"]["params"][config_param]] = config_param

        if columns:
            columns = ','.join(columns)

            for time in times:
                datetime_s = "{date} {time}:00".format(date=data_date, time=time)
                datetime_e = "{date} {time}:10".format(date=data_date, time=time)
                sql = """select {columns} from {table} where datetime >= CONVERT(DATETIME, '{datetime_s}') and datetime <= CONVERT(DATETIME, '{datetime_e}')"""\
                    .format(columns=columns, table=table, datetime_s=datetime_s, datetime_e=datetime_e)
                records = db.select_sql_dict(sql)

                if records:
                    record = records[0]
                    for key in record.keys():
                        parameter_name = mapping[key]
                        parameter_value = record[key]
                        mach = line["line"]
                        process_type = line["process"]["type"]
                        if not self.isVNEDCExisted(data_date, plant, mach, process_type, time, parameter_name):
                            self.insert_vnedc(data_date, plant, mach, process_type, time, parameter_name, parameter_value)

    def isVNEDCExisted(self, data_date, plant, mach, process_type, time, parameter_name):
        result = False
        db = vnedc_database()
        sql = """select * from collection_parametervalue 
                 where plant_id='{plant}' and mach_id='{mach}' and data_date='{data_date}' and data_time='{data_time}' 
                 and process_type='{process_type}' and parameter_name='{parameter_name}' """\
            .format(plant=plant, mach=mach, data_date=data_date, process_type=process_type, parameter_name=parameter_name, data_time=time)
        #print(sql)
        records = db.select_sql_dict(sql)
        if records:
            result = True
        return result

    def insert_vnedc(self, data_date, plant, mach, process_type, time, parameter_name, parameter_value):
        db = vnedc_database()

        sql = """insert into collection_parametervalue(data_date, plant_id, mach_id, process_type, data_time, parameter_name, parameter_value, create_at, update_at, create_by_id, update_by_id) 
                                Values('{date_date}', '{plant}', '{mach}', '{process_type}', '{data_time}', '{parameter_name}', {parameter_value}, GETDATE(), GETDATE(), 1, 1)""" \
            .format(date_date=data_date, plant=plant, mach=mach, process_type=process_type, data_time=time, parameter_name=parameter_name, parameter_value=parameter_value)
        print(sql)
        db.execute_sql(sql)

    def get_param_define(self, plant, line_info):
        db = vnedc_database()
        line = line_info["line"]
        process_type = line_info["process"]["type"]
        sql = """select * from collection_parameterdefine where plant_id='{plant}' 
                    and mach_id='{line}' and process_type_id='{process_type}'"""\
            .format(plant=plant, line=line, process_type=process_type)
        result = db.select_sql_dict(sql)
        return result