import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from jobs.database import mes_database, vnedc_database


class mes_production_info(object):
    today = ""

    def __init__(self, today):
        self.today = today

    def extract_substring(self, input_string):
        # 找到第一个 '-' 的位置
        first_dash_index = input_string.find('-')

        if first_dash_index == -1:
            # 如果没有找到 '-'，返回空字符串
            dash_substring = input_string
        else:
            # 找到第一个 '-' 后面的第二个 '-' 的位置
            second_dash_index = input_string.find('-', first_dash_index + 1)

            if second_dash_index == -1:
                # 如果没有第二个 '-'，取从第一个 '-' 后面的字符串到末尾
                dash_substring = input_string[first_dash_index + 1:]
            else:
                # 截取两个 '-' 之间的子字符串
                dash_substring = input_string[first_dash_index + 1:second_dash_index]

            substring = dash_substring.split(" ")[0]

        # 检查子字符串是否以 'XL' 结尾
        if substring.endswith('XXL') or substring.endswith('XXS'):
            result = substring[-3:]
        elif substring.endswith('XL') or substring.endswith('XS'):
            # 如果以 'XL' 结尾，取最后两个字符
            result = substring[-2:]
        else:
            # 否则取最后一个字符
            result = substring[-1]

        if result not in ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL']:
            if dash_substring.find('XXS') > -1:
                result = 'XXS'
            elif dash_substring.find('XXL') > -1:
                result = 'XXL'
            elif dash_substring.find('XS') > -1:
                result = 'XS'
            elif dash_substring.find('XL') > -1:
                result = 'XL'
            elif dash_substring.find('S') > -1:
                result = 'S'
            elif dash_substring.find('M') > -1:
                result = 'M'
            elif dash_substring.find('L') > -1:
                result = 'L'

            return result
        else:
            return result


    def main(self):
        today = self.today

        db = mes_database()
        vnedc_db = vnedc_database()

        sql = f"""
        SELECT distinct InspectionDate, Name, ProductItem, LineName
          FROM [PMGMES].[dbo].[PMG_MES_WorkOrder] w
          join [PMGMES].[dbo].[PMG_DML_DataModelList] dl on w.MachineId = dl.Id
          join [PMGMES].[dbo].[PMG_MES_RunCard] r on r.WorkOrderId = w.id
          join [PMGMES].[dbo].[PMG_MES_IPQCInspectingRecord] ipqc on ipqc.RunCardId = r.Id
          where InspectionDate = '{today}' and Period between 6 and 23
          and Name like '%NBR%'
          and OptionName = 'Weight'
		  and InspectionValue > 0
          order by Name, LineName
        """

        results = db.select_sql_dict(sql)

        for result in results:
            size = self.extract_substring(result["ProductItem"])
            machine = str(result["Name"]).replace('_', '')
            mach_id = machine[2:7] + machine[-2:]
            plant_id = machine[2:7]
            data_date = result["InspectionDate"]
            line = result["LineName"]
            product = result["ProductItem"]

            sql = f"""
            select * from [VNEDC].[dbo].[collection_daily_prod_info_head] where data_date = '{data_date}'
            and line = '{line}' and product = '{product}' and mach_id = '{mach_id}' and plant_id = '{plant_id}'
            """
            rows = vnedc_db.select_sql_dict(sql)

            if not rows:
                sql = f"""
                insert into [VNEDC].[dbo].[collection_daily_prod_info_head](data_date, plant_id, mach_id, line, product, size, create_at, create_by_id)
                values('{data_date}', '{plant_id}', '{mach_id}', '{line}', '{product}', '{size}', GETDATE(), 1)
                """
                vnedc_db.execute_sql(sql)

def insert_weight(selected_date):
    sql = f"""
        SELECT rc.WorkCenterTypeName, rc.MachineName, rc.Id, rc.InspectionDate, rc.Period,  rc.LineName, ir.InspectionValue
        FROM [PMGMES].[dbo].[PMG_MES_RunCard] rc
        JOIN [PMGMES].[dbo].[PMG_MES_IPQCInspectingRecord] ir
        ON rc.Id = ir.RunCardId
        AND ir.OptionName = 'Weight'
        WHERE rc.WorkCenterTypeName = 'NBR'
        AND (Period = 0 OR Period = 6 OR Period = 12 or Period = 18)
        AND rc.InspectionDate = '{selected_date}'
        ORDER BY Cast(Period as INT), MachineName, LineName
    """
    db = mes_database()
    vnedc_db = vnedc_database()
    rows = db.select_sql_dict(sql)
    for row in rows:
        count = 0
        sdata_date = row['InspectionDate']
        splant_id = "GDNBR" if 'NBR' == str(row['WorkCenterTypeName']) else 'LK'
        smach_id = "GDNBR"+ str(row['MachineName'])[-2:] if splant_id == "GDNBR" else "LKNBR" + str(row['MachineName'])[-2:]
        if str(row['Period']) == '0':
            sdata_time = '00'
        elif str(row['Period']) == '6':
            sdata_time = '06'
        elif str(row['Period']) == '12':
            sdata_time = '12'
        else:
            sdata_time = '18'
        sparameter_value = float(row['InspectionValue'])

        check_sql = f"""
                select * from [VNEDC].[dbo].[collection_parametervalue] 
                where data_date = '{sdata_date}' and plant_id = '{splant_id}' and mach_id = '{smach_id}' and process_type = 'OTHER' and data_time = {sdata_time} and parameter_name = 'WEIGHT'
        """
        check = vnedc_db.select_sql_dict(check_sql)
        if check:
            continue
        elif not check:
            insert_sql = f"""
                insert into [VNEDC].[dbo].[collection_parametervalue] (data_date, plant_id, mach_id, process_type, data_time, parameter_name, parameter_value, create_at, update_at, create_by_id, update_by_id)
                values ('{sdata_date}', '{splant_id}', '{smach_id}', 'OTHER', '{sdata_time}', 'WEIGHT', {sparameter_value}, GETDATE(), GETDATE(), 30, 30)
            """
            vnedc_db.execute_sql(insert_sql)


from datetime import datetime, timedelta

today = datetime.today()
today = today.strftime('%Y-%m-%d')
insert_weight(today)

prod_info = mes_production_info(today)
prod_info.main()