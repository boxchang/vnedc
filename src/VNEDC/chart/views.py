from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, date, timedelta
from VNEDC.database import mes_database, vnedc_database
from chart.forms import SearchForm, ProductionSearchForm
from collection.models import ParameterValue, ParameterDefine, Parameter_Type
import random
from collection.models import Process_Type, Plant, Machine
import matplotlib.pyplot as plt
import base64
import io
import time

def generate_pastel_color():
    # 设定颜色值的下限，以保证颜色偏淡
    lower_bound = 120  # 颜色的下限值
    upper_bound = 230  # 深色的上限值。通常设置在128以下，以确保颜色是深色

    # 生成淡色系的RGB颜色值
    r = random.randint(lower_bound, upper_bound)
    g = random.randint(lower_bound, upper_bound)
    b = random.randint(lower_bound, upper_bound)

    # 生成淡色系的 RGB 颜色值
    r = random.randint(lower_bound, upper_bound)
    g = random.randint(lower_bound, upper_bound)
    b = random.randint(lower_bound, upper_bound)

    # 将 RGB 颜色转换为十六进制格式
    pastel_color_hex = '#{:02x}{:02x}{:02x}'.format(r, g, b)

    return pastel_color_hex


def get_product_choices(start_date, end_date):
    sql = f"""
        SELECT distinct ProductItem
        FROM [PMGMES].[dbo].[PMG_MES_WorkOrder] where 
        workOrderDate between '{start_date}' and '{end_date}' 
        AND SAP_FactoryDescr like '%NBR%'
        order by ProductItem
        """
    mes_db = mes_database()
    rows = mes_db.select_sql_dict(sql)
    choices = [('', '---')] + [(row['ProductItem'], row['ProductItem']) for row in rows]
    return choices

def param_value(request):
    search_form = SearchForm()
    return render(request, 'chart/param_value.html', locals())

def param_value_product(request):
    month_ago = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    today = (date.today()).strftime("%Y-%m-%d")
    choices = get_product_choices(month_ago, today)

    search_form = ProductionSearchForm()
    search_form.fields['product'].choices = choices
    return render(request, 'chart/param_value_product.html', locals())

def param_value_api(request):
    chart_data = {}
    if request.method == 'POST':
        data_date_start = request.POST.get('data_date_start')
        data_date_end = request.POST.get('data_date_end')
        plant = request.POST.get('plant')
        mach = request.POST.get('mach')
        process_type = request.POST.get('process_type')
        param_type = request.POST.get('param_type')
        control_high = request.POST.get('control_high')
        control_low = request.POST.get('control_low')

        y_label = []
        datasets = []

        backgroundColor = {"01": "#4dc9f6", "02": "#f67019", "03": "#f53794", "04": "#537bc4", "05": "#acc236",
                           "06": "#166a8f", "07": "#00a950", "08": "#58595b", "09": "#4ff9f6", "10": "#fff019",
                           "11": "#fff794", "12": "#5ffbc4", "13": "#aff236", "14": "#1ffa8f", "15": "#0ff950",
                           "16": "#5ff95b", "17": "#bfff44", "18": "#efff44", "19": "#dffa44", "20": "#cffaaf"}
        borderColor = {"01": "#3db9e6", "02": "#e66009", "03": "#e52784", "04": "#436bc3", "05": "#9cb226",
                       "06": "#065a7f", "07": "#009940", "08": "#48494b", "09": "#4dd9f6", "10": "#fdd019",
                       "11": "#fdd794", "12": "#5ddbc4", "13": "#add236", "14": "#1dda8f", "15": "#0dd950",
                       "16": "#5dd95b", "17": "#beef44", "18": "#eeef44", "19": "#deea44", "20": "#ceeaaf"}

        try:

            defines = ParameterDefine.objects.filter(plant=plant, mach=mach, process_type=process_type, param_type=param_type)

            param_name = defines[0].parameter_name

            for define in defines:
                records = ParameterValue.objects.filter(plant=plant, mach=mach, process_type=process_type,
                                                        parameter_name=define.parameter_name, data_date__gte=data_date_start, data_date__lte=data_date_end)

                # Date Label
                for record in records:
                    tmp = "{data_date} {data_time}:00".format(data_date=record.data_date, data_time=record.data_time)
                    if tmp not in y_label:
                        y_label.append(tmp)
                y_label = list(set(y_label))
                y_label.sort()


                dataset = {}
                color = generate_pastel_color()
                dataset['label'] = define.parameter_name
                dataset['backgroundColor'] = color
                dataset['borderColor'] = color
                dataset["datalabels"] = {'align': 'end', 'anchor': 'end'}
                data = []
                for date_time in y_label:
                    date = date_time.split(' ')[0]
                    time = date_time.split(' ')[1].replace(":00", "")
                    tmp = records.filter(data_date=date, data_time=time, mach=mach).first()
                    if tmp:
                        data.append(tmp.parameter_value)
                if data:
                    dataset['data'] = data
                    datasets.append(dataset)

            # 取上下限值
            control_high_data = []
            base_line_data = []
            control_low_data = []
            define = None
            if control_high == "" and control_low == "":
                define = ParameterDefine.objects.filter(plant=plant, mach=mach, process_type=process_type,
                                                        parameter_name=param_name).first()
                if define:
                    for date_time in y_label:
                        control_high_data.append(define.control_range_high)
                        base_line_data.append(define.base_line)
                        control_low_data.append(define.control_range_low)
                    form_control_range_high = define.control_range_high if define.control_range_high else ''
                    form_control_range_low = define.control_range_low if define.control_range_low else ''

            if control_high != "":
                for date_time in y_label:
                    control_high_data.append(control_high)
                form_control_range_high = control_high

            if control_low != "":
                for date_time in y_label:
                    control_low_data.append(control_low)
                form_control_range_low = control_low

            datasets.append({'label': '控制上限', 'data': control_high_data, 'backgroundColor': '#aaaaaa',
                             'borderColor': '#cccccc', 'borderDash': [10, 2]})
            datasets.append(
                {'label': '控制線', 'data': base_line_data, 'backgroundColor': '#eeeeee', 'borderColor': '#cccccc',
                 'borderDash': [10, 2]})
            datasets.append({'label': '控制下限', 'data': control_low_data, 'backgroundColor': '#aaaaaa',
                             'borderColor': '#cccccc', 'borderDash': [10, 2]})

            if define.scada_column:
                title = process_type + "__" + param_type + "(" + define.scada_column + ")"
            else:
                title = process_type + "__" + param_type

            y_data = {"beginAtZero": "true", "min": control_low_data[0] * 0.1, "max": control_high_data[0] * 1.9}

            chart_data = {"labels": y_label, "datasets": datasets, "title": title, "control_high": form_control_range_high, "control_low": form_control_range_low, "y_data": y_data}
        except Exception as e:
            chart_data = {"labels": [], "datasets": [], "title": title, "control_high": form_control_range_high, "control_low": form_control_range_low, "y_data": []}
            print(e)

    return JsonResponse(chart_data, safe=False)


def param_value_product_api(request):
    chart_data = {}
    if request.method == 'POST':
        data_date_start = request.POST.get('data_date_start')
        data_date_end = request.POST.get('data_date_end')
        process_type = request.POST.get('process_type')
        param_code = request.POST.get('param_code')
        product = request.POST.get('product')

        backgroundColor = {"01": "#4dc9f6", "02": "#f67019", "03": "#f53794", "04": "#537bc4", "05": "#acc236",
                           "06": "#166a8f", "07": "#00a950", "08": "#58595b", "09": "#4ff9f6", "10": "#fff019",
                           "11": "#fff794", "12": "#5ffbc4", "13": "#aff236", "14": "#1ffa8f", "15": "#0ff950",
                           "16": "#5ff95b", "17": "#bfff44", "18": "#efff44", "19": "#dffa44", "20": "#cffaaf"}
        borderColor = {"01": "#3db9e6", "02": "#e66009", "03": "#e52784", "04": "#436bc3", "05": "#9cb226",
                       "06": "#065a7f", "07": "#009940", "08": "#48494b", "09": "#4dd9f6", "10": "#fdd019",
                       "11": "#fdd794", "12": "#5ddbc4", "13": "#add236", "14": "#1dda8f", "15": "#0dd950",
                       "16": "#5dd95b", "17": "#beef44", "18": "#eeef44", "19": "#deea44", "20": "#ceeaaf"}

        try:
            # Generate Y
            times = ['00:00', '06:00', '12:00', '18:00']  # 定義每天的四個特定時間點
            y_label = []  # 初始化空列表來存儲結果

            # 迭代日期區間內的每一天
            start_date = datetime.strptime(data_date_start, '%Y-%m-%d')
            end_date = datetime.strptime(data_date_end, '%Y-%m-%d')
            current_date = start_date
            while current_date <= end_date:
                for time in times:
                    date_time_str = current_date.strftime('%Y-%m-%d') + ' ' + time  # 將日期和時間點結合並轉換為字符串格式
                    y_label.append(date_time_str)
                current_date += timedelta(days=1)  # 將日期增加一天

            # 找出有幾條線
            sql = f"""
            WITH ProdInfoHead AS (
                SELECT distinct head.data_date,head.mach_id,substring(line,1,1) side
                  FROM collection_daily_prod_info_head head, collection_daily_prod_info info
                  where head.data_date = info.data_date and product = '{product}' and head.data_date between '{data_date_start}' and '{data_date_end}'
                 )
                
            select * from collection_parametervalue v 
            join collection_parameterdefine d on d.plant_id = v.plant_id and d.mach_id = v.mach_id 
            and d.process_type_id = v.process_type and v.parameter_name = d.parameter_name 
            join ProdInfoHead i on v.data_date = i.data_date AND v.mach_id = i.mach_id
            where v.process_type = '{process_type}' and d.param_type = '{param_code}' and (i.side = d.side or d.side = '')
            """

            vnedc_db = vnedc_database()
            records = vnedc_db.select_sql_dict(sql)

            chart_records = set((record['mach_id'], record['parameter_name'], record['side']) for record in records)  # 使用集合去除重复的 (mach_id, side) 组合
            chart_records = list(chart_records)  # 将集合转换为列表
            chart_records = sorted(chart_records, key=lambda x: x[1])  # 按照第二个值排序

            # Chart Data
            datasets = []
            color_index = 1
            for chart_record in chart_records:
                mach_id = chart_record[0]
                param_name = chart_record[1]
                side = chart_record[2]
                dataset = {}
                dataset['label'] = mach_id + " " + side + " " + param_name
                dataset['backgroundColor'] = backgroundColor[str(color_index).zfill(2)]
                dataset['borderColor'] = borderColor[str(color_index).zfill(2)]
                dataset["datalabels"] = {'align': 'end', 'anchor': 'end'}
                dataset["spanGaps"] = True
                data = []

                for date_time in y_label:
                    date = date_time.split(' ')[0]
                    time = date_time.split(' ')[1].replace(":00", "")
                    time_filter = [record for record in records if
                                   record['mach_id'] == mach_id and record['side'] == side
                                   and record['data_date'].strftime("%Y-%m-%d") == date
                                   and record['data_time'] == time and record['parameter_name'] == param_name]
                    if time_filter:
                        data.append(time_filter[0]['parameter_value'])
                    else:
                        data.append('null')

                color_index += 1

                if data:
                    dataset['data'] = data
                    datasets.append(dataset)

            # 取上下限值
            control_high_data = []
            base_line_data = []
            control_low_data = []

            param_type = Parameter_Type.objects.filter(param_type_code=param_code, process_type=process_type).first()

            if param_type:
                control_table = param_type.control_table
                control_high_column = param_type.control_high_column
                control_low_column = param_type.control_low_column

            if control_table:
                if 'MES' in control_table:
                    sql = f"""
                            select {control_high_column}, {control_low_column} from {control_table} where ProductItem = '{product}'
                        """
                    mew_db = mes_database()
                    records = mew_db.select_sql_dict(sql)
                else:
                    dash_index = product.find('-')
                    if dash_index != -1 and dash_index + 2 < len(product):
                        product = product[dash_index + 1:dash_index + 3]
                    sql = f"""
                            select {control_high_column}, {control_low_column} from {control_table} where item_no = '{product}'
                            and process_type = '{process_type}' and parameter_name = '{param_code}'
                        """
                    records = vnedc_db.select_sql_dict(sql)

                if records:
                    for date_time in y_label:
                        control_high_data.append(float(records[0][control_high_column]))
                        control_low_data.append(float(records[0][control_low_column]))

                    datasets.append(
                        {'label': '控制上限', 'data': control_high_data, 'backgroundColor': '#cccccc', 'borderColor': '#999999',
                         'borderDash': [10, 2]})
                    datasets.append(
                        {'label': '控制下限', 'data': control_low_data, 'backgroundColor': '#cccccc', 'borderColor': '#999999',
                         'borderDash': [10, 2]})
                    y_data = {"beginAtZero": "true", "min": control_low_data[0] * 0.1, "max": control_high_data[0] * 1.7}
            else:
                y_data = {}

            chart_data = {"labels": y_label, "datasets": datasets,
                          "title": product + "  " + process_type + "  " + param_code, "subtitle": product, "y_data": y_data}

        except Exception as e:
            print(e)

    return JsonResponse(chart_data, safe=False)


def get_param_define_api(request):
    html = ""
    if request.method == 'POST':
        plant = request.POST.get('plant')
        mach = request.POST.get('mach')
        process_type = request.POST.get('process_type')
        lang = request.POST.get('lang')
        records = ParameterDefine.objects.filter(plant=plant, mach=mach, process_type=process_type).distinct()
        html = """<option value="" selected>---------</option>"""
        distinct = []

        for record in records:
            if record.parameter_name not in distinct:
                if lang == 'zh-hans':
                    name = record.parameter_cn
                elif lang == 'zh-hant':
                    name = record.parameter_tw
                elif lang == 'vi':
                    name = record.parameter_vn
                else:
                    name = record.parameter_name
                html += """<option value="{value}">{name}</option>""".format(value=record.parameter_name, name=name)
                distinct.append(record.parameter_name)

    return JsonResponse(html, safe=False)

def get_param_code_api(request):
    html = ""
    if request.method == 'POST':
        process_type = request.POST.get('process_type')
        records = Parameter_Type.objects.filter(process_type=process_type)
        html = """<option value="" selected>---------</option>"""

        for record in records:
            html += """<option value="{value}">{name}</option>""".format(value=record.param_type_code, name=record.param_type_code)

    return JsonResponse(html, safe=False)

def test(request):

    return render(request, 'chart/test.html', locals())


def param_2(request):
    if request.method == 'POST':
        request.session['plant'] = request.POST.get('plant', '')
        request.session['mach'] = request.POST.get('mach', '')
        request.session['data_date'] = request.POST.get('data_date', '')

    return (request.session.get('plant', ''), request.session.get('mach', ''),
            request.session.get('data_date', ''))


import json
import os
import io
from .utils import chart_config
from collections import defaultdict

def param_value2(request):
    sPlant, sMach, sData_date = param_2(request)
    start_time = time.time()

    if not sData_date:
        sData_date = datetime.now().strftime('%Y-%m')

    plants = Plant.objects.all()
    machs = Machine.objects.filter(plant=sPlant) if sPlant else None

    # Use the provided chart configuration
    config = chart_config()
    db = vnedc_database()

    # Initialize a dictionary to hold all data from SQL results
    data_dict = defaultdict(list)

    # Optimize SQL queries by batching variables together
    for process_type, sub_dict in config.items():
        variables = [var for sub_key in sub_dict.values() for var in sub_key['variables']]
        variables_str = "', '".join(variables)

        # Construct a single SQL query for all variables in the process type
        sql = f"""
            SELECT data_date, mach_id, process_type, parameter_name, data_time, parameter_value
            FROM [VNEDC].[dbo].[collection_parametervalue]
            WHERE plant_id = '{sPlant}' 
            AND mach_id = '{sMach}' 
            AND process_type = '{process_type}' 
            AND parameter_name IN ('{variables_str}')
            AND data_date LIKE '%{sData_date}%'
            ORDER BY data_date, data_time;
        """
        # Execute the SQL query
        results = db.select_sql_dict(sql)

        # Group results by key and append data
        for result in results:
            key = f"{process_type}_{result['parameter_name']}"
            data_dict[key].append({
                'data_date': str(result['data_date']),
                'parameter_value': result['parameter_value']
            })

    # Plotting data directly from the SQL results
    if sMach and sPlant and results:
        start_time_img = time.time()
        image_data = []
        for main_key, sub_dict in config.items():
            for sub_key, attributes in sub_dict.items():
                start_time_img_1 = time.time()
                variables = attributes['variables']
                high_limit = attributes['high']
                low_limit = attributes['low']
                xlim = attributes['xlim']
                ylim = attributes['ylim']

                plt.figure(figsize=(16, 9))

                # Plot each variable in the sub-key if data is available
                for variable in variables:
                    key = f"{main_key}_{variable}"
                    data = data_dict.get(key, [])
                    if data:
                        # Extract data_date and parameter_value for plotting
                        data_dates = [entry['data_date'] for entry in data]
                        parameter_values = [entry['parameter_value'] for entry in data]
                        indices = list(range(len(parameter_values)))

                        # Plot the parameter values against indices
                        plt.plot(indices, parameter_values, marker='o', linestyle='-', label=key)

                        # Initialize unique_dates within this loop to ensure it's scoped correctly
                        unique_dates = {}
                        for i, date in enumerate(data_dates):
                            if date not in unique_dates:
                                plt.axvline(x=i, color='gray', linestyle='--', linewidth=0.5)
                                unique_dates[date] = i  # Mark the index of the first occurrence

                # X-axis label formatting: show each unique `data_date` once, rotated 45 degrees
                plt.xticks(
                    ticks=list(unique_dates.values()),
                    labels=list(unique_dates.keys()),
                    rotation=45,
                    ha='right'
                )

                # Add grid lines and other visual elements
                plt.fill_between(indices, parameter_values, color='white', alpha=0.3)
                plt.axhline(y=high_limit, color='red', linestyle='--', linewidth=1, label=f'Up limit = {high_limit}')
                plt.axhline(y=low_limit, color='red', linestyle='--', linewidth=1, label=f'Down limit = {low_limit}')
                plt.axhline(y=(high_limit + low_limit) / 2, color='black', linestyle='--', linewidth=1,
                            label='Middle value')

                # Set x-axis and y-axis limits
                plt.xlim(0, min(xlim[1], len(parameter_values)))
                plt.ylim(*ylim)
                plt.xlabel('Date')
                plt.ylabel('Value')
                plt.title(f'{sMach} - {main_key} - {sub_key}', fontsize=18)
                plt.legend()

                # Save the plot as a base64 encoded image with reduced border
                buf = io.BytesIO()
                plt.savefig(buf, format='jpg', dpi=100, bbox_inches='tight', pad_inches=0.2)
                buf.seek(0)
                image_base64 = base64.b64encode(buf.read()).decode('utf-8')
                plt.close()

                # Add the encoded image to the list
                image_data.append(image_base64)
                end_time_img_1 = time.time()
                end_time_img = time.time()

        # Output the generated images or further process as needed
        print("Generated plots and encoded them as base64 images.")
    else:
        print("Missing machine or plant information.")

    # Calculate execution time
    end_time = time.time()
    execution_time = end_time - start_time

# You would typically call param_value2(request) with the appropriate request object.

    # Pass the image data to the template
    return render(request, 'chart/param_value2.html', locals())
