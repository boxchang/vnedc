from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import get_language
from collection.forms import RecordForm, DailyInfoForm, InfoForm
from collection.models import ParameterDefine, Process_Type, Plant, Machine, Daily_Prod_Info, ParameterValue


def index(request):
    info_form = InfoForm()
    return render(request, 'collection/index.html', locals())


def prod_info_reset(request):
    if request.method == 'POST':
        if 'plant' in request.session:
            del request.session['plant']

        if 'mach' in request.session:
            del request.session['mach']

        if 'data_date' in request.session:
            del request.session['data_date']
    return redirect(reverse('daily_info_create'))


def page_init(request):
    plant = ""
    mach = ""
    data_date = ""
    if 'plant' in request.session:
        plant = Plant.objects.get(plant_code=request.session['plant'])
    if 'mach' in request.session:
        mach = Machine.objects.get(mach_code=request.session['mach'])
    if 'data_date' in request.session:
        data_date = request.session['data_date']
    lang = get_language()

    return plant, mach, data_date, lang


def prod_info_save(request):
    if request.method == 'POST':
        if 'plant' not in request.session:
            request.session['plant'] = request.POST.get('plant')

        if 'mach' not in request.session:
            request.session['mach'] = request.POST.get('mach')

        if 'data_date' not in request.session:
            request.session['data_date'] = request.POST.get('data_date')

    return redirect(reverse('daily_info_create'))


def record(request, process_code):
    plant, mach, data_date, lang = page_init(request)
    process_type = Process_Type.objects.filter(process_code=process_code).first()
    processes = Process_Type.objects.all().order_by('show_order')
    data_times = ['00', '06', '12', '18']

    if request.method == 'POST':
        if process_type:
            defines = ParameterDefine.objects.filter(plant=plant, mach=mach, process_type=process_type)
            for define in defines:
                for time in data_times:
                    value = request.POST.get(define.parameter_name+'_'+time)
                    try:
                        if value:
                            ParameterValue.objects.update_or_create(plant=plant, mach=mach,
                                                                    data_date=data_date,
                                                                    process_type=process_type,
                                                                    data_time=time, parameter_name=define.parameter_name,
                                                                    create_by=request.user,
                                                                    update_by=request.user,
                                                                    defaults={'parameter_value': value})
                    except Exception as e:
                        print(e)
        return redirect(reverse('record', kwargs={'process_code': process_code}))

    if process_type:
        defines = ParameterDefine.objects.filter(plant=plant, mach=mach, process_type=process_type)
        for define in defines:
            values = ParameterValue.objects.filter(plant=plant, mach=mach, data_date=data_date,
                                                   process_type=process_type, parameter_name=define.parameter_name)

            if values:
                for time in data_times:
                    item = values.filter(data_time=time).first()
                    if item:
                        value = item.parameter_value
                        setattr(define, "T"+time, value)

    info_form = InfoForm()
    return render(request, 'collection/record.html', locals())


@login_required
def daily_info_create(request):
    plant, mach, data_date, lang = page_init(request)
    form = DailyInfoForm()
    info_form = InfoForm()

    processes = Process_Type.objects.all().order_by('show_order')

    if not plant:
        return redirect(reverse('collection_index'))

    info = Daily_Prod_Info.objects.filter(plant=plant, mach=mach, data_date=data_date).first()

    if info:
        form = DailyInfoForm(instance=info)

    if request.method == 'POST':
        if not info:
            form = DailyInfoForm(request.POST)
            if form.is_valid():
                tmp_form = form.save(commit=False)
                tmp_form.plant = plant
                tmp_form.mach = mach
                tmp_form.data_date = data_date
                tmp_form.create_by = request.user
                tmp_form.update_by = request.user
                tmp_form.save()
        else:
            form = DailyInfoForm(request.POST, instance=info)
            if form.is_valid():
                tmp_form = form.save(commit=False)
                tmp_form.update_by = request.user
                tmp_form.save()

    return render(request, 'collection/daily_info_create.html', locals())


def raw_data_api(request, data_date_start, data_date_end, process_type):
    records = []
    data_date_start = datetime.strptime(data_date_start, '%Y%m%d')
    data_date_end = datetime.strptime(data_date_end, '%Y%m%d') + timedelta(days=1)
    date_list = [data_date_start + timedelta(days=x) for x in range(0, (data_date_end - data_date_start).days)]
    process_type = process_type
    TIMES = ["00", "06", "12", "18"]
    control = ParameterDefine.objects.filter(plant="GDNBR", mach="01", process_type="ACID", parameter_name__icontains="TEMPERATURE").first()
    defines = ParameterDefine.objects.filter(process_type="ACID", parameter_name__icontains="TEMPERATURE")

    for data_date in date_list:
        for time in TIMES:
            record = {}
            record["DATA_TIME"] = datetime.strftime(data_date, '%Y/%m/%d') + " " + time + ":00"
            record["PROCESS_TYPE"] = process_type
            for define in defines:
                record["PLANT"] = define.plant.plant_code
                data = ParameterValue.objects.filter(data_date=data_date, process_type=process_type, plant=define.plant, data_time=time, parameter_name=define.parameter_name, mach=define.mach).first()
                record[define.mach.mach_code+"_"+define.parameter_name] = data.parameter_value if data else 0
            record["RANGE_HIGH"] = control.control_range_high
            record["BASE"] = control.base_line
            record["RANGE_LOW"] = control.control_range_low
            records.append(record)

    return JsonResponse(records, safe=False)

