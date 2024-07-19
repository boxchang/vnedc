from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, date, timedelta
from VNEDC.database import mes_database, vnedc_database
from chart.forms import SearchForm, ProductionSearchForm
from collection.models import ParameterValue, ParameterDefine, Parameter_Type


def get_product_choices(start_date, end_date):
    sql = f"""
        SELECT distinct ProductItem
        FROM [PMGMES].[dbo].[PMG_MES_WorkOrder] where workOrderDate between '{start_date}' and '{start_date}' order by ProductItem
        """
    mes_db = mes_database()
    rows = mes_db.select_sql_dict(sql)
    choices = [('', '---')] + [(row['ProductItem'], row['ProductItem']) for row in rows]
    return choices

def param_value(request):
    search_form = SearchForm()
    return render(request, 'chart/param_value.html', locals())

def param_value_product(request):
    day7_ago = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    today = (date.today()).strftime("%Y-%m-%d")
    choices = get_product_choices(day7_ago, today)

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
        param_define = request.POST.get('param_define')
        control_high = request.POST.get('control_high')
        control_low = request.POST.get('control_low')
        backgroundColor = {"01": "#4dc9f6", "02": "#f67019", "03": "#f53794", "04": "#537bc4", "05": "#acc236",
                           "06": "#166a8f", "07": "#00a950", "08": "#58595b", "09": "#4ff9f6", "10": "#fff019",
                           "11": "#fff794", "12": "#5ffbc4", "13": "#aff236", "14": "#1ffa8f", "15": "#0ff950",
                           "16": "#5ff95b", "17": "#bfff44", "18": "#efff44", "19": "#dffa44", "20": "#cffaaf"}
        borderColor = {"01": "#3db9e6", "02": "#e66009", "03": "#e52784", "04": "#436bc3", "05": "#9cb226",
                       "06": "#065a7f", "07": "#009940", "08": "#48494b", "09": "#4dd9f6", "10": "#fdd019",
                       "11": "#fdd794", "12": "#5ddbc4", "13": "#add236", "14": "#1dda8f", "15": "#0dd950",
                       "16": "#5dd95b", "17": "#beef44", "18": "#eeef44", "19": "#deea44", "20": "#ceeaaf"}

        try:
            records = ParameterValue.objects.filter(plant=plant, mach=mach, process_type=process_type,
                                                    parameter_name=param_define, data_date__gte=data_date_start, data_date__lte=data_date_end)
            y_label = []
            datasets = []
            for record in records:
                y_label.append("{data_date} {data_time}:00".format(data_date=record.data_date, data_time=record.data_time))
            y_label = list(set(y_label))
            y_label.sort()


            dataset = {}
            mach_index = mach[-2:]
            dataset['label'] = mach
            dataset['backgroundColor'] = backgroundColor[mach_index]
            dataset['borderColor'] = borderColor[mach_index]
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
            control_low_data = []
            define = None
            if control_high == "" and control_low == "":
                define = ParameterDefine.objects.filter(plant=plant, mach=mach, process_type=process_type, parameter_name=param_define).first()
                if define:
                    for date_time in y_label:
                        control_high_data.append(define.control_range_high)
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

            datasets.append({'label': '控制上限', 'data': control_high_data, 'backgroundColor': '#ffc4bd', 'borderColor': '#ffb7ad', 'borderDash': [10,2]})
            datasets.append({'label': '控制下限', 'data': control_low_data, 'backgroundColor': '#ffc4bd', 'borderColor': '#ffb7ad', 'borderDash': [10,2]})

            chart_data = {"labels": y_label, "datasets": datasets, "title": process_type, "control_high": form_control_range_high, "control_low": form_control_range_low}
        except Exception as e:
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
            sql = f"""
            WITH ProdInfo AS (
                SELECT i.data_date, v.data_time, i.mach_id, i.plant_id, d.parameter_name, d.parameter_tw, d.side, t.param_code, v.process_type, v.parameter_value, prod_name_a1 ,prod_name_a2, prod_name_b1, prod_name_b2
                FROM [VNEDC].[dbo].[collection_daily_prod_info] i
                JOIN [VNEDC].[dbo].[collection_parametervalue] v ON v.data_date = i.data_date AND v.mach_id = i.mach_id AND v.plant_id = i.plant_id
                JOIN [VNEDC].[dbo].[collection_parameterdefine] d ON v.process_type = d.process_type_id AND v.mach_id = d.mach_id AND v.parameter_name = d.parameter_name
                JOIN [VNEDC].[dbo].[collection_parameter_type] t ON d.param_type_id = t.id AND d.process_type_id = t.process_type_id
                WHERE v.process_type = '{process_type}'
                  AND t.param_code = '{param_code}'
                  AND i.data_date between '{data_date_start}' and '{data_date_end}'
            ),
            SelectedProdInfo AS (
                SELECT * FROM ProdInfo
                WHERE side = 'A' AND (prod_name_a1 = '{product}' OR prod_name_a2 = '{product}')
                UNION ALL
                SELECT * FROM ProdInfo
                WHERE side = 'B' AND (prod_name_b1 = '{product}' OR prod_name_b2 = '{product}')
                UNION ALL
                SELECT * FROM ProdInfo WHERE side = ''
            )
            SELECT data_date, data_time, mach_id, process_type, parameter_name, parameter_tw, side, param_code, parameter_name, parameter_value
            FROM SelectedProdInfo;
            """
            vnedc_db = vnedc_database()
            records = vnedc_db.select_sql_dict(sql)

            # 使用集合去除重复的 (mach_id, side) 组合
            chart_records = set((record['mach_id'], record['side']) for record in records)
            # 将集合转换为列表
            chart_records = list(chart_records)
            # 按照第一个值排序
            chart_records = sorted(chart_records, key=lambda x: x[0])

            y_label = []
            datasets = []
            for record in records:
                y_label.append("{data_date} {data_time}:00".format(data_date=record['data_date'], data_time=record['data_time']))
            y_label = list(set(y_label))
            y_label.sort()

            color_index = 1
            for chart_record in chart_records:
                mach_id = chart_record[0]
                side = chart_record[1]
                dataset = {}
                dataset['label'] = mach_id + " " + side
                dataset['backgroundColor'] = backgroundColor[str(color_index).zfill(2)]
                dataset['borderColor'] = borderColor[str(color_index).zfill(2)]
                dataset["datalabels"] = {'align': 'end', 'anchor': 'end'}
                data = []

                for date_time in y_label:
                    date = date_time.split(' ')[0]
                    time = date_time.split(' ')[1].replace(":00", "")
                    time_filter = [record for record in records if record['mach_id'] == mach_id and record['side'] == side and record['data_date'].strftime("%Y-%m-%d") == date and record['data_time'] == time]
                    if time_filter:
                        data.append(time_filter[0]['parameter_value'])

                color_index += 1

                if data:
                    dataset['data'] = data
                    datasets.append(dataset)

            # 取上下限值
            control_high_data = []
            base_line_data = []
            control_low_data = []

            param_type = Parameter_Type.objects.filter(param_code=param_code).first()
            define = ParameterDefine.objects.filter(process_type=process_type, param_type=param_type).first()
            if define:
                for date_time in y_label:
                    control_high_data.append(define.control_range_high)
                    base_line_data.append(define.base_line)
                    control_low_data.append(define.control_range_low)

            datasets.append({'label': '控制上限', 'data': control_high_data, 'backgroundColor': '#ffc4bd', 'borderColor': '#ffb7ad', 'borderDash': [10,2]})
            datasets.append({'label': '控制線', 'data': base_line_data, 'backgroundColor': '#ffddbd', 'borderColor': '#ffddad', 'borderDash': [10, 2]})
            datasets.append({'label': '控制下限', 'data': control_low_data, 'backgroundColor': '#ffc4bd', 'borderColor': '#ffb7ad', 'borderDash': [10,2]})

            chart_data = {"labels": y_label, "datasets": datasets, "title": process_type+" "+param_code}
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
                    name = record.parameter_vi
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
            html += """<option value="{value}">{name}</option>""".format(value=record.param_code, name=record.param_name)

    return JsonResponse(html, safe=False)
