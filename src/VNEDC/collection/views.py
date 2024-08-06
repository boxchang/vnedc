from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from VNEDC.database import vnedc_database
from collection.forms import DailyInfoForm
from collection.models import ParameterDefine, Process_Type, Plant, Machine, Daily_Prod_Info, ParameterValue, \
    Daily_Prod_Info_Head
from jobs.database import mes_database


def create_vnedc_connection():
    pass


@login_required
def index(request):
    plants = Plant.objects.all()
    machs = Machine.objects.none()
    if request.method == 'POST':
        sData_date = request.POST.get('data_date')
    else:
        sData_date = datetime.today()
        sData_date = sData_date.strftime("%Y-%m-%d")

    tmp_machs = Machine.objects.all()
    parameter_list = []
    for tmp_mach in tmp_machs:
        daily_prod_info_heads = Daily_Prod_Info_Head.objects.filter(data_date=sData_date, mach=tmp_mach.mach_code).order_by('mach_id', 'line')
        tmp_mach.daily_prod_info_heads = daily_prod_info_heads

        defines = ParameterDefine.objects.filter(mach=tmp_mach.mach_code, auto_value=0)

        goal_count = 0
        for define in defines:
            if define.sampling_frequency == "6H" or define.sampling_frequency == None:
                goal_count += 4
            elif define.sampling_frequency == "12H":
                goal_count += 2

            # Setup Define Parameter
            #tmp_param = define.process_type.process_code + "_" + define.parameter_name
            #if not tmp_param in parameter_list:
            #    parameter_list.append(define.process_type.process_code + "_" + define.parameter_name)

        reach_count = 0

        tmp_msg = ""

        sql = f"""            
        select d.plant_id,d.mach_id,d.parameter_name,v.parameter_value,d.process_type_id from (SELECT *
          FROM [VNEDC].[dbo].[collection_parameterdefine] 
          where plant_id='{tmp_mach.plant}' and mach_id='{tmp_mach.mach_code}' and auto_value=0) d
          join 
          (select * from [VNEDC].[dbo].[collection_parametervalue] 
          where data_date = '{sData_date}' and plant_id='{tmp_mach.plant}' and mach_id='{tmp_mach.mach_code}' and parameter_value>0) v 
          on d.plant_id = v.plant_id and d.mach_id = v.mach_id and d.parameter_name = v.parameter_name 
          and d.process_type_id = v.process_type
            order by process_type_id
        """
        db = vnedc_database()
        results = db.select_sql_dict(sql)
        for result in results:
            if result["parameter_value"] != None and result["parameter_value"] > 0:
                reach_count += 1

                # Remove Completed Parameter
                #tmp_param = result["process_type_id"] + "_" + result["parameter_name"]
                #if tmp_param in parameter_list:
                #    parameter_list.remove(tmp_param)

        hit_rate_msg = f"{reach_count}/{goal_count}"

        hit_rate = 0
        if reach_count > 0:
            hit_rate = int(round(reach_count/goal_count, 2) * 100)
        tmp_mach.hit_rate_msg = hit_rate_msg
        tmp_mach.hit_rate = hit_rate

        #tmp_msg = "\r\n".join(parameter_list)
        #tmp_mach.msg = tmp_msg

    return render(request, 'collection/index.html', locals())


@login_required
def prod_info_reset(request):
    if request.method == 'POST':
        if 'plant' in request.session:
            del request.session['plant']

        if 'mach' in request.session:
            del request.session['mach']

        if 'data_date' in request.session:
            del request.session['data_date']
    return redirect(reverse('daily_info_create'))


@login_required
def page_init(request):
    plant = ""
    mach = ""
    data_date = ""

    if 'plant' in request.session:
        plant = request.session['plant']
    else:
        plant = request.POST.get('plant')

    if 'mach' in request.session:
        mach = request.session['mach']
    else:
        mach = request.POST.get('mach')

    if 'data_date' in request.session:
        data_date = request.session['data_date']
    else:
        data_date = request.POST.get('data_date')

    lang = get_language()

    return plant, mach, data_date, lang


@login_required
def prod_info_save(request):
    if request.method == 'POST':
        request.session['plant'] = request.POST.get('plant')
        request.session['mach'] = request.POST.get('mach')
        request.session['data_date'] = request.POST.get('data_date')
    return redirect(reverse('daily_info_create'))


@login_required
def record(request, process_code):
    sPlant, sMach, sData_date, lang = page_init(request)
    process_type = Process_Type.objects.filter(process_code=process_code).first()
    processes = Process_Type.objects.all().order_by('show_order')
    data_times = ['00', '06', '12', '18']
    plants = Plant.objects.all()

    if sPlant:
        machs = Machine.objects.filter(plant=sPlant)
    else:
        machs = None

    info = Daily_Prod_Info.objects.filter(plant=sPlant, mach=sMach, data_date=sData_date).first()

    plant = Plant.objects.get(plant_code=sPlant)
    mach = Machine.objects.get(mach_code=sMach)

    if request.method == 'POST':
        if process_type:
            defines = ParameterDefine.objects.filter(plant=sPlant, mach=sMach, process_type=process_type)
            for define in defines:
                for time in data_times:
                    value = request.POST.get(define.parameter_name+'_'+time)
                    try:
                        if value:
                            if float(value) == 0:
                                ParameterValue.objects.update_or_create(plant=plant, mach=mach,
                                                                        data_date=sData_date,
                                                                        process_type=process_type.process_code,
                                                                        data_time=time, parameter_name=define.parameter_name,
                                                                        defaults={'parameter_value': value, 'create_by': request.user, 'update_by': request.user})
                            msg = _("Update Done")
                    except Exception as e:
                        print(e)
        return redirect(reverse('record', kwargs={'process_code': process_code}))

    if process_type:
        defines = ParameterDefine.objects.filter(plant=sPlant, mach=sMach, process_type=process_type)
        for define in defines:
            values = ParameterValue.objects.filter(plant=sPlant, mach=sMach, data_date=sData_date,
                                                   process_type=process_type.process_code, parameter_name=define.parameter_name).order_by('-create_at')

            if values:
                for time in data_times:
                    item = values.filter(data_time=time).first()
                    if item:
                        value = item.parameter_value
                        setattr(define, "T"+time, value)

    daily_prod_info_heads = Daily_Prod_Info_Head.objects.filter(data_date=sData_date).order_by('line')

    return render(request, 'collection/record.html', locals())


def get_production_choices(end_date):
    date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    date_obj_minus_one = date_obj - timedelta(days=365)
    start_date = date_obj_minus_one.strftime("%Y-%m-%d")

    sql = f"""
        SELECT distinct ProductItem
        FROM [PMGMES].[dbo].[PMG_MES_WorkOrder] where SAP_FactoryDescr like '%NBR%' and WorkOrderDate between '{start_date}' and '{end_date}'
		order by ProductItem"""
    mes_db = mes_database()
    rows = mes_db.select_sql_dict(sql)
    choices = [('', '---')] + [(row['ProductItem'], row['ProductItem']) for row in rows]
    return choices


@login_required
def daily_info_create(request):
    sPlant, sMach, sData_date, lang = page_init(request)
    form = DailyInfoForm()
    plants = Plant.objects.all()

    processes = Process_Type.objects.all().order_by('show_order')

    if not sPlant or not sMach:
        return redirect(reverse('collection_index'))

    if sPlant:
        machs = Machine.objects.filter(plant=sPlant)

    plant = Plant.objects.get(plant_code=sPlant)
    mach = Machine.objects.get(mach_code=sMach)

    info = Daily_Prod_Info.objects.filter(plant=sPlant, mach=sMach, data_date=sData_date).first()

    if info:
        form = DailyInfoForm(instance=info, initial={'remark': info.remark.split(',')})

    if request.method == 'POST':
        if not info:  # 新增
            form = DailyInfoForm(request.POST)

            choices = get_production_choices(sData_date)
            form.fields['prod_name_a1'].choices = choices
            form.fields['prod_name_a2'].choices = choices
            form.fields['prod_name_b1'].choices = choices
            form.fields['prod_name_b2'].choices = choices

            if form.is_valid():
                tmp_form = form.save(commit=False)
                tmp_form.plant = plant
                tmp_form.mach = mach
                tmp_form.data_date = sData_date
                tmp_form.create_by = request.user
                tmp_form.update_by = request.user
                selected_options = form.cleaned_data['remark']
                tmp_form.remark = ','.join(selected_options)
                tmp_form.save()

                # 重新取得最新資料
                info = Daily_Prod_Info.objects.filter(plant=sPlant, mach=sMach, data_date=sData_date).first()
        else:  # 更新
            form = DailyInfoForm(request.POST, instance=info)

            choices = get_production_choices(sData_date)
            form.fields['prod_name_a1'].choices = choices
            form.fields['prod_name_a2'].choices = choices
            form.fields['prod_name_b1'].choices = choices
            form.fields['prod_name_b2'].choices = choices

            if form.is_valid():
                tmp_form = form.save(commit=False)
                tmp_form.update_by = request.user
                selected_options = form.cleaned_data['remark']
                tmp_form.remark = ','.join(selected_options)
                tmp_form.save()

        # =====================Start================================
        a1_product = tmp_form.prod_name_a1
        a1_size = tmp_form.prod_size_a1
        if a1_product and a1_size:
            if not Daily_Prod_Info_Head.objects.filter(data_date=sData_date, line="A1", product=a1_product,
                                                       size=a1_size, mach=mach, plant=plant):
                Daily_Prod_Info_Head.objects.create(data_date=sData_date, line="A1", product=a1_product,
                                                    size=a1_size, create_by=request.user, mach=mach, plant=plant)

        a2_product = tmp_form.prod_name_a2
        a2_size = tmp_form.prod_size_a2
        if a2_product and a2_size:
            if not Daily_Prod_Info_Head.objects.filter(data_date=sData_date, line="A2", product=a2_product,
                                                       size=a2_size, mach=mach, plant=plant):
                Daily_Prod_Info_Head.objects.create(data_date=sData_date, line="A2", product=a2_product,
                                                    size=a2_size, create_by=request.user, mach=mach, plant=plant)

        b1_product = tmp_form.prod_name_b1
        b1_size = tmp_form.prod_size_b1
        if b1_product and b1_size:
            if not Daily_Prod_Info_Head.objects.filter(data_date=sData_date, line="B1", product=b1_product,
                                                       size=b1_size, mach=mach, plant=plant):
                Daily_Prod_Info_Head.objects.create(data_date=sData_date, line="B1", product=b1_product,
                                                    size=b1_size, create_by=request.user, mach=mach, plant=plant)

        b2_product = tmp_form.prod_name_b2
        b2_size = tmp_form.prod_size_b2
        if b2_product and b2_size:
            if not Daily_Prod_Info_Head.objects.filter(data_date=sData_date, line="B2", product=b2_product,
                                                       size=b2_size, mach=mach, plant=plant):
                Daily_Prod_Info_Head.objects.create(data_date=sData_date, line="B2", product=b2_product,
                                                    size=b2_size, create_by=request.user, mach=mach, plant=plant)
        # =====================End================================

        msg = _("Update Done")

    choices = get_production_choices(sData_date)
    form.fields['prod_name_a1'].choices = choices
    form.fields['prod_name_a2'].choices = choices
    form.fields['prod_name_b1'].choices = choices
    form.fields['prod_name_b2'].choices = choices

    daily_prod_info_heads = Daily_Prod_Info_Head.objects.filter(data_date=sData_date, mach=mach, plant=plant).order_by('line')

    return render(request, 'collection/daily_info_create.html', locals())


def daily_info_head_delete(request, pk):
    if request.method == 'GET':
        head = Daily_Prod_Info_Head.objects.get(pk=pk)
        head.delete()
    return redirect(reverse('daily_info_create'))


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

def get_mach_api(request):
    if request.method == 'POST':
        plant = request.POST.get('plant')
        machs = Machine.objects.filter(plant=plant)
        html = """<option value="" selected>---------</option>"""

        for mach in machs:
            html += """<option value="{value}">{name}</option>""".format(value=mach.mach_code, name=mach.mach_name)
    return JsonResponse(html, safe=False)


def test(request):
    return render(request, 'collection/test.html', locals())

