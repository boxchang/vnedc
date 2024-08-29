from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from openpyxl.utils import get_column_letter
from VNEDC.database import vnedc_database
from collection.forms import DailyInfoForm
from collection.models import ParameterDefine, Process_Type, Plant, Machine, Daily_Prod_Info, ParameterValue, \
    Daily_Prod_Info_Head, Lab_Parameter_Control
from jobs.database import mes_database
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Border, Side, Font, Alignment, PatternFill
from django.shortcuts import render
import re


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
          FROM [collection_parameterdefine] 
          where plant_id='{tmp_mach.plant}' and mach_id='{tmp_mach.mach_code}' and auto_value=0) d
          join 
          (select * from [collection_parametervalue] 
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
        FROM [PMG_MES_WorkOrder] where SAP_FactoryDescr like '%NBR%' and WorkOrderDate between '{start_date}' and '{end_date}'
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


def rd_select(request):
    if request.method == 'POST':
        request.session['plant'] = request.POST.get('plant', '')
        request.session['mach'] = request.POST.get('mach', '')
        request.session['data_date'] = request.POST.get('data_date', '')

    return (request.session.get('plant', ''), request.session.get('mach', ''),
            request.session.get('data_date', ''), get_language())

def rd_report(request):
    sPlant, sMach, sData_date, lang = rd_select(request)

    process_type = Process_Type.objects.filter().first()
    plants = Plant.objects.all()
    machs = Machine.objects.filter(plant=sPlant) if sPlant else None

    defines = ParameterDefine.objects.filter(
        plant=sPlant,
        mach=sMach,
        process_type__in=['ACID', 'ALKALINE', 'LATEX', 'COAGULANT', 'CHLORINE'],
        parameter_name__in=['T1_CONCENTRATION', 'T2_CONCENTRATION', 'A_T1_TSC',
                            'A_T1_PH',  'A_T2_TSC', 'A_T2_PH', 'B_T1_TSC',
                            'B_T1_PH', 'B_T2_TSC', 'B_T2_PH', 'A_CPF',
                            'A_PH', 'A_CONCENTRATION', 'B_CPF',
                            'B_PH', 'B_CONCENTRATION', 'CONCENTRATION']
    )

    for define in defines:
        values = ParameterValue.objects.filter(
                                    plant=sPlant,
                                    mach=sMach,
                                    data_date=sData_date,
                                    process_type=define.process_type.process_code,
                                    parameter_name=define.parameter_name
                                )
        define.values = values

    try:
        control_limit = Lab_Parameter_Control.objects.filter(
            plant=sPlant,
            mach=sMach,
            item_no=re.search(r'-(\d+)', Daily_Prod_Info.objects.filter(
                                        plant=sPlant,
                                        mach=sMach,
                                        data_date=sData_date).first().prod_name_a1).group(1))
        low_value, high_value = [], []
        for i in range(len(control_limit)):
            high_value.append(control_limit[i].control_range_high)
            low_value.append(control_limit[i].control_range_low)

        low_limit, high_limit = [0]*19, [0]*19
        for i in ([5, 6, 8, 9] + list(range(10, 18))):
            if i in [5, 6, 8, 9]:
                if i == 5 or i == 8:
                    low_limit[i], high_limit[i] = low_value[3], high_value[3]
                elif i == 6 or i == 9:
                    low_limit[i], high_limit[i] = low_value[4], high_value[4]
            else:
                if i % 2 == 0:
                    low_limit[i], high_limit[i] = low_value[0], high_value[0]
                else:
                    low_limit[i], high_limit[i] = low_value[1], high_value[1]

    except:
        pass

    return render(request, 'collection/rd_report.html', locals())

def generate_excel_file_big(request):
    sPlant, sMach, sData_date, sTo_date, sEnable_mode, sLimit_mode, lang = rd_select(request)
    if sEnable_mode == 'off':
        sTo_date == ''

    workbook = Workbook()
    worksheet = workbook.active

    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    download_code = 0
    if sPlant != '' and sMach != '' and sData_date != '':
        if sTo_date != '':
            start_date = datetime.strptime(sData_date, "%Y-%m-%d")
            end_date = datetime.strptime(sTo_date, "%Y-%m-%d")
            if start_date == end_date:
                filename = f"DATA-{sPlant}-{sMach}-{sData_date}.xlsx"
                plant_rp, mach_rp, date_rp, to_rp = sPlant, sMach, sData_date, sTo_date
                download_code = 1
            elif start_date < end_date and (end_date - start_date).days < 31:
                filename = f"DATA-{sPlant}-{sMach}-{sData_date}-to-{sTo_date}.xlsx"
                plant_rp, mach_rp, date_rp, to_rp = sPlant, sMach, sData_date, sTo_date
                download_code = 1
        elif sTo_date == '':
            start_date = datetime.strptime(sData_date, "%Y-%m-%d")
            end_date = start_date
            filename = f"DATA-{sPlant}-{sMach}-{sData_date}.xlsx"
            plant_rp, mach_rp, date_rp, to_rp = sPlant, sMach, sData_date, sTo_date
            download_code = 1

    if download_code == 1:
        for row in range(5, 27):
            worksheet.row_dimensions[row].height = 25
        worksheet.column_dimensions['A'].width = 30
        worksheet.column_dimensions['B'].width = 20
        worksheet.column_dimensions['C'].width = 20
        worksheet.row_dimensions[1].height = 45
        worksheet.row_dimensions[2].height = 30
        worksheet.row_dimensions[3].height = 30
        worksheet.row_dimensions[4].height = 30

        def set_merged_cell(range_str, value, alignment="center", fill_color="F1FF18"):
            worksheet.merge_cells(range_str)
            cell = worksheet[range_str.split(':')[0]]
            cell.value = value
            cell.alignment = Alignment(horizontal=alignment, vertical="center")
            cell.font = Font(bold=True, color="333333")
            cell.fill = PatternFill("solid", fgColor=fill_color)
        def set_merged_cell2(range_str, value, alignment="center", fill_color="FDE9D9"):
            worksheet.merge_cells(range_str)
            cell = worksheet[range_str.split(':')[0]]
            cell.value = value
            cell.alignment = Alignment(horizontal=alignment, vertical="center")
            cell.font = Font(bold=True, color="333333")
            cell.fill = PatternFill("solid", fgColor=fill_color)
        set_merged_cell('A5:A7', "ITEM")
        set_merged_cell('B5:B7', "Parameters")
        set_merged_cell('C5:C7', "Specs.")
        set_merged_cell('D5:G5', "Sample Time")

        names = ["Acid tank 1", "Acid tank 2", "Alkaline tank 1", "Alkaline tank 2", "Coagulant A", "Coagulant B",
                 "Latex SIDE A-1", "Latex SIDE A-2", "Latex SIDE B-1", "Latex SIDE B-2", "Chlorination"]
        merge_sizes = [1, 1, 1, 1, 3, 3, 2, 2, 2, 2, 1]
        start_row = 8
        for name, size in zip(names, merge_sizes):
            end_row = start_row + size - 1
            worksheet.merge_cells(f"A{start_row}:A{end_row}")
            cell = worksheet[f"A{start_row}"]
            cell.value = name
            cell.alignment = Alignment(horizontal="left", vertical="center", indent=3)
            start_row = end_row + 1

        parameters = ["%", "%", "%", "%", "CN (%)", "CPF (%)", "pH Value",
                      "CN (%)", "CPF (%)", "pH Value", "TSC %", "pH Value",
                      "TSC %", "pH Value", "TSC %", "pH Value", "TSC %", "pH Value", "ppm"]
        for row_num, param in enumerate(parameters, start=8):
            worksheet[f'B{row_num}'] = param
            worksheet[f'B{row_num}'].alignment = Alignment(horizontal="center", vertical="center")

        days_diff = (end_date - start_date).days + 1
        col_end = 7

        for day_offset in range(days_diff):
            current_date = start_date + timedelta(days=day_offset)
            col_start = 4 + (day_offset * 4)
            col_end = col_start + 3
            set_merged_cell2(f'{get_column_letter(col_start)}2:{get_column_letter(col_end)}2',  f"{plant_rp}")
            set_merged_cell2(f'{get_column_letter(col_start)}3:{get_column_letter(col_end)}3',  f"{mach_rp}")
            set_merged_cell2(f'{get_column_letter(col_start)}4:{get_column_letter(col_end)}4',  f"{current_date.strftime('%Y-%m-%d')}")
            set_merged_cell(f'{get_column_letter(col_start)}5:{get_column_letter(col_end)}5', "Sample Time")
            sample_times = ["1", "2", "3", "4"]
            sample_hours = ["0h", "6h", "12h", "18h"]

            for i, col in enumerate([get_column_letter(col_start),get_column_letter(col_start+1), get_column_letter(col_end-1), get_column_letter(col_end)]):
                worksheet[f'{col}6'] = sample_times[i]
                worksheet[f'{col}7'] = sample_hours[i]
                worksheet[f'{col}6'].alignment = worksheet[f'{col}7'].alignment = Alignment(horizontal="center")
                worksheet[f'{col}6'].fill = worksheet[f'{col}7'].fill = PatternFill("solid", fgColor="F1FF18")
            defines = ParameterDefine.objects.filter(
                plant=sPlant,
                mach=sMach,
                process_type__in=['ACID', 'ALKALINE', 'LATEX', 'COAGULANT', 'CHLORINE'],
                parameter_name__in=[
                    'T1_CONCENTRATION', 'T2_CONCENTRATION', 'A_T1_TSC', 'A_T1_PH',
                    'A_T2_TSC', 'A_T2_PH', 'B_T1_TSC', 'B_T1_PH', 'B_T2_TSC', 'B_T2_PH',
                    'A_CPF', 'A_PH', 'A_CONCENTRATION', 'B_CPF', 'B_PH', 'B_CONCENTRATION', 'CONCENTRATION'
                ]
            )
            start_row = 8
            for define in defines:
                values = ParameterValue.objects.filter(
                    plant=sPlant,
                    mach=sMach,
                    data_date=current_date.strftime('%Y-%m-%d'),
                    process_type=define.process_type.process_code,
                    parameter_name=define.parameter_name
                )

                for value in values:
                    # Determine the column based on data_time
                    if value.data_time == '00':
                        worksheet[f'{get_column_letter(col_start)}{start_row}'] = value.parameter_value
                    elif value.data_time == '06':
                        worksheet[f'{get_column_letter(col_start + 1)}{start_row}'] = value.parameter_value
                    elif value.data_time == '12':
                        worksheet[f'{get_column_letter(col_start + 2)}{start_row}'] = value.parameter_value
                    elif value.data_time == '18':
                        worksheet[f'{get_column_letter(col_start + 3)}{start_row}'] = value.parameter_value
                start_row += 1

        if int(sLimit_mode) == 1:
            try:
                control_limit = Lab_Parameter_Control.objects.filter(
                    plant=sPlant,
                    mach=sMach,
                    item_no=re.search(r'-(\d+)', Daily_Prod_Info.objects.filter(
                        plant=sPlant,
                        mach=sMach,
                        data_date=sData_date).first().prod_name_a1).group(1))
                low_value, high_value = [], []
                for i in range(len(control_limit)):
                    high_value.append(control_limit[i].control_range_high)
                    low_value.append(control_limit[i].control_range_low)

                low_limit, high_limit = [0] * 19, [0] * 19
                for i in ([5, 6, 8, 9] + list(range(10, 18))):
                    if i in [5, 6, 8, 9]:
                        if i == 5 or i == 8:
                            low_limit[i], high_limit[i] = low_value[3], high_value[3]
                        elif i == 6 or i == 9:
                            low_limit[i], high_limit[i] = low_value[4], high_value[4]
                    else:
                        if i % 2 == 0:
                            low_limit[i], high_limit[i] = low_value[0], high_value[0]
                        else:
                            low_limit[i], high_limit[i] = low_value[1], high_value[1]

                range_limit = []
                for i in range(len(high_limit)):
                    range_limit.append(f'{low_limit[i]} ~ {high_limit[i]}')

                start_row = 8

                for i in range(len(high_limit)):
                    if high_limit[i] != 0:
                        worksheet[f'C{start_row}'] = range_limit[i]
                        worksheet[f'C{start_row}'].alignment = Alignment(vertical="center", horizontal="right")
                    start_row += 1

                for i in range(len(high_limit)):
                    start_row = i + 8
                    if high_limit[i] != 0:
                        for day_offset in range(days_diff):
                            current_start_col = 4 + (day_offset * 4)
                            for col in range(current_start_col, current_start_col + 4):
                                cell = worksheet[f'{get_column_letter(col)}{start_row}']
                                if cell.value and float(cell.value):
                                    if float(cell.value) > float(high_limit[i]):
                                        cell.fill = PatternFill("solid", fgColor='FF0000')
                                    elif float(cell.value) < float(low_limit[i]):
                                        cell.fill = PatternFill("solid", fgColor='FF0000')
                    start_row += 1
            except Exception as e:
                print(f"An error occurred: {e}")

        def set_header_row(row, col, value, merged_cells=None, fill_color="FDE9D9"):
            if merged_cells:
                worksheet.merge_cells(merged_cells)
            worksheet.row_dimensions[row].height = 30
            cell = worksheet[f'{col}{row}']
            cell.value = value
            cell.alignment = Alignment(horizontal="left", vertical="center")
            cell.font = Font(size=14, bold=False)
            cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        header_data = [('A2', 'Plant :', plant_rp), ('A3', 'Machine :', mach_rp), ('A4', 'Date :', date_rp)]
        for col, label, value in header_data:
            row = int(col[1:])
            set_header_row(row, col[0], label)
        worksheet.merge_cells('B2:C4')
        fill = PatternFill(start_color='FDE9D9', end_color='FDE9D9', fill_type='solid')
        for row in worksheet.iter_rows(min_row=2, max_row=4, min_col=2, max_col=3):
            for cell in row:
                cell.fill = fill
        worksheet.merge_cells(f'A1:{get_column_letter(col_end)}1')
        worksheet.row_dimensions[1].height = 45
        merged_cell = worksheet['A1']
        merged_cell.value = 'Daily Report'
        merged_cell.alignment = Alignment(horizontal="center", vertical="center")
        merged_cell.font = Font(size=18, bold=True)
        merged_cell.fill = PatternFill(start_color="EBF1DE", end_color="EBF1DE", fill_type="solid")

        left_top_thick = Border(left=Side(style='thick'), right=Side(style='thin'),
                                top=Side(style='thick'), bottom=Side(style='thin'))
        right_top_thick = Border(left=Side(style='thin'), right=Side(style='thick'),
                                top=Side(style='thick'), bottom=Side(style='thin'))
        left_bot_thick = Border(left=Side(style='thick'), right=Side(style='thin'),
                                top=Side(style='thin'), bottom=Side(style='thick'))
        right_bot_thick = Border(left=Side(style='thin'), right=Side(style='thick'),
                                top=Side(style='thin'), bottom=Side(style='thick'))
        right_thick = Border(left=Side(style='thin'), right=Side(style='thick'),
                                 top=Side(style='thin'), bottom=Side(style='thin'))
        left_thick = Border(left=Side(style='thick'), right=Side(style='thin'),
                                 top=Side(style='thin'), bottom=Side(style='thin'))
        top_thick = Border(left=Side(style='thin'), right=Side(style='thin'),
                                 top=Side(style='thick'), bottom=Side(style='thin'))
        bot_thick = Border(left=Side(style='thin'), right=Side(style='thin'),
                                 top=Side(style='thin'), bottom=Side(style='thick'))
        middle = Border(left=Side(style='thin'), right=Side(style='thin'),
                                 top=Side(style='thin'), bottom=Side(style='thin'))
        for row in worksheet.iter_rows(min_row=5, max_row=26, min_col=4, max_col=7):
            for cell in row:
                if cell.row == 5 and cell.column == 4:
                    cell.border = left_top_thick
                elif cell.row == 5 and cell.column == 7:
                    cell.border = right_top_thick
                elif cell.row == 26 and cell.column == 4:
                    cell.border = left_bot_thick
                elif cell.row == 26 and cell.column == 7:
                    cell.border = right_bot_thick
                elif cell.column == 4:
                    cell.border = left_thick
                elif cell.column == 7:
                    cell.border = right_thick
                elif cell.row == 5:
                    cell.border = top_thick
                elif cell.row == 26:
                    cell.border = bot_thick
                else:
                    cell.border = middle

        for row in worksheet.iter_rows(min_row=5, max_row=7, min_col=1, max_col=col_end):
            for cell in row:
                cell.border = thin_border
                cell.font = Font(size=14)

        for row in worksheet.iter_rows(min_row=8, max_row=26, min_col=1, max_col=col_end):
            for cell in row:
                cell.border = thin_border
                cell.font = Font(size=13)
        for row in worksheet.iter_rows(min_row=2, max_row=4, min_col=1, max_col=col_end):
            for cell in row:
                cell.font = Font(size=14)
        for row in worksheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.isdigit():
                    cell.value = int(cell.value)

        def thick_boder_table(ws, min_row, max_row, min_col, max_col):
            thick = Side(border_style="medium", color="000000")
            for col in range(min_col, max_col + 1):
                ws.cell(row=min_row, column=col).border = Border(top=thick)
            for col in range(min_col, max_col + 1):
                ws.cell(row=max_row, column=col).border = Border(bottom=thick)
            for row in range(min_row, max_row + 1):
                ws.cell(row=row, column=min_col).border = Border(left=thick)
            for row in range(min_row, max_row + 1):
                ws.cell(row=row, column=max_col).border = Border(right=thick)
            ws.cell(row=min_row, column=min_col).border = Border(top=thick, left=thick)
            ws.cell(row=min_row, column=max_col).border = Border(top=thick, right=thick)
            ws.cell(row=max_row, column=min_col).border = Border(bottom=thick, left=thick)
            ws.cell(row=max_row, column=max_col).border = Border(bottom=thick, right=thick)

        def thick_boder_table2(ws, min_row, max_row, min_col, max_col):
            thick = Side(border_style="medium", color="000000")
            thin = Side(border_style="thin", color="000000")

            for col in range(min_col, max_col + 1):
                ws.cell(row=min_row, column=col).border = Border(top=thick, bottom=thin, left=thin, right=thin)
            for col in range(min_col, max_col + 1):
                ws.cell(row=max_row, column=col).border = Border(bottom=thick, top=thin, left=thin, right=thin)
            for row in range(min_row, max_row + 1):
                ws.cell(row=row, column=min_col).border = Border(left=thick, right=thin, top=thin, bottom=thin)
            for row in range(min_row, max_row + 1):
                ws.cell(row=row, column=max_col).border = Border(right=thick, top=thin, left=thin, bottom=thin)

            ws.cell(row=min_row, column=min_col).border = Border(top=thick, left=thick, right=thin, bottom=thin)
            ws.cell(row=min_row, column=max_col).border = Border(top=thick, right=thick, bottom=thin, left=thin)
            ws.cell(row=max_row, column=min_col).border = Border(bottom=thick, left=thick, top=thin, right=thin)
            ws.cell(row=max_row, column=max_col).border = Border(bottom=thick, right=thick, left=thin, top=thin)

        thick_boder_table(worksheet, min_row=1, max_row=1, min_col=1, max_col=col_end)
        for col in range(4, col_end, 4):
            thick_boder_table(worksheet, min_row=2, max_row=4, min_col=col, max_col=col_end)
        for col in range(4, col_end, 4):
            thick_boder_table2(worksheet, min_row=5, max_row=26, min_col=col, max_col=col_end)

        worksheet.freeze_panes = 'D8'
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        workbook.save(response)

        return response
    else:
        return HttpResponse(status=204)

