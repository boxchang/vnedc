from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from chart.forms import SearchForm
from collection.models import ParameterValue, ParameterDefine


def param_value(request):
    search_form = SearchForm()
    return render(request, 'chart/param_value.html', locals())


def param_value_api(request):
    chart_data = {}
    if request.method == 'POST':
        data_date_start = request.POST.get('data_date_start')
        data_date_end = request.POST.get('data_date_end')
        plants = request.POST.getlist('plant[]')
        machs = request.POST.getlist('mach[]')
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
            records = ParameterValue.objects.filter(plant__in=plants, mach__in=machs, process_type=process_type,
                                                    parameter_name=param_define, data_date__gte=data_date_start, data_date__lte=data_date_end)
            y_label = []
            datasets = []
            for record in records:
                y_label.append("{data_date} {data_time}:00".format(data_date=record.data_date, data_time=record.data_time))
            y_label = list(set(y_label))
            y_label.sort()

            for mach in machs:
                dataset = {}
                dataset['label'] = mach
                dataset['backgroundColor'] = backgroundColor[mach]
                dataset['borderColor'] = borderColor[mach]
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
                define = ParameterDefine.objects.filter(plant__in=plants, mach__in=machs, process_type=process_type, parameter_name=param_define).first()
                if define:
                    for date_time in y_label:
                        control_high_data.append(define.control_range_high)
                        control_low_data.append(define.control_range_low)
                    form_control_range_high = define.control_range_high
                    form_control_range_low = define.control_range_low

            if control_high != "":
                for date_time in y_label:
                    control_high_data.append(control_high)
                form_control_range_high = control_high

            if control_low != "":
                for date_time in y_label:
                    control_low_data.append(control_low)
                form_control_range_low = control_low

            datasets.append({'label': 'CONTROL RANGE HIGH', 'data': control_high_data, 'backgroundColor': '#ffc4bd', 'borderColor': '#ffb7ad', 'borderDash': [10,2]})
            datasets.append({'label': 'CONTROL RANGE LOW', 'data': control_low_data, 'backgroundColor': '#ffc4bd', 'borderColor': '#ffb7ad', 'borderDash': [10,2]})

            chart_data = {"labels": y_label, "datasets": datasets, "title": process_type, "control_high": form_control_range_high, "control_low": form_control_range_low}
        except Exception as e:
            print(e)

    return JsonResponse(chart_data, safe=False)


def get_param_define_api(request):
    html = ""
    if request.method == 'POST':
        plant = request.POST.getlist('plant[]')
        mach = request.POST.getlist('mach[]')
        process_type = request.POST.get('process_type')
        records = ParameterDefine.objects.filter(plant__in=plant, mach__in=mach, process_type=process_type).distinct()
        html = """<option value="" selected>---------</option>"""
        distinct = []

        for record in records:
            if record.parameter_name not in distinct:
                html += """<option value="{value}">{name}</option>""".format(value=record.parameter_name, name=record.parameter_name)
                distinct.append(record.parameter_name)

    return JsonResponse(html, safe=False)
