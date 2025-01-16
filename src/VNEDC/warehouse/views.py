import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from VNEDC.database import sap_database
from warehouse.utils import Do_Transaction, transfer_stock
from .forms import WarehouseForm, AreaForm, BinForm, BinValueForm, BinSearchForm, StockInPForm, StockOutPForm, \
    BinTransferForm
from .models import Warehouse, Area, Bin, Bin_Value, Bin_Value_History, StockInForm, Series, StockInFormDetail, \
    MovementType, ItemType, StockOutForm
from django.db.models import Case, When, Value, BooleanField




# Warehouse
def create_warehouse(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST, request.FILES)  # Xử lý dữ liệu POST và FILES
        if form.is_valid():
            # Lưu đối tượng với user hiện tại
            warehouse = form.save(commit=False)  # Không lưu ngay lập tức

            # Gán người dùng vào các trường create_by và update_by
            warehouse.create_by = request.user
            warehouse.update_by = request.user

            # Lưu đối tượng với các trường đã được gán
            warehouse.save()  # Lưu đối tượng vào cơ sở dữ liệu
            return redirect('warehouse_list')  # Điều hướng đến trang thành công
    else:
        form = WarehouseForm()  # Tạo form trống

    return render(request, 'warehouse/create_warehouse.html', locals())


def warehouse_list(request):
    # Lấy toàn bộ danh sách warehouse từ cơ sở dữ liệu
    warehouses = Warehouse.objects.all()
    x = warehouses

    return render(request, 'warehouse/list_warehouse.html', locals())


def edit_warehouse(request, warehouse_code):
    warehouse = get_object_or_404(Warehouse, wh_code=warehouse_code)

    if request.method == 'POST':
        form = WarehouseForm(request.POST, request.FILES, instance=warehouse)

        if form.is_valid():
            form.save()  # Lưu các thay đổi vào cơ sở dữ liệu
            return redirect('warehouse_list')  # Điều hướng về danh sách kho
    else:
        form = WarehouseForm(instance=warehouse)

    return render(request, 'warehouse/edit_warehouse.html', locals())


def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)

    if request.method == 'POST':
        warehouse.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX
            return JsonResponse({'message': 'Warehouse deleted successfully.', 'success': True}, status=200)

        return redirect('warehouse_list')

    return JsonResponse({'message': 'Invalid request method.'}, status=400)


def test(request):

    return render(request, 'warehouse/test.html', locals())


def show_warehouse(request, pk):
    if request.method == 'POST':
        form = BinValueForm(request.POST)
        if form.is_valid():
            form.save()
            list_value = list(Bin_Value.objects.values())
            return JsonResponse(list_value, safe=False)

    warehouse = Warehouse.objects.get(wh_code=pk)
    bins = Bin.objects.filter(area__warehouse=warehouse)
    form = BinValueForm()

    bins_status = []

    for bin in bins:
        bin_value_exists = Bin_Value.objects.filter(bin=bin).exists()

        status = 'red' if bin_value_exists else 'green'

        bins_status.append({
            'bin_id': bin.bin_id,
            'status': status,  # Sử dụng biến status đã gán
        })
    return render(request, 'warehouse/test.html', locals())


# Area
def create_area(request, wh_code):
    if request.method == 'POST':
        form = AreaForm(request.POST)  # Xử lý dữ liệu POST và FILES
        if form.is_valid():

            area = form.save(commit=False)  # Không lưu ngay lập tức
            # Gán người dùng vào các trường create_by và update_by
            area.create_by = request.user
            area.update_by = request.user

            # Lưu đối tượng với các trường đã được gán
            area.save()  # Lưu đối tượng vào cơ sở dữ liệu
            return redirect('area_by_warehouse', wh_code=wh_code)  # Điều hướng đến trang thành công
    else:
        form = AreaForm(initial={'warehouse': wh_code})  # Tạo form trống

    return render(request, 'warehouse/area/create_area.html', locals())


def area_list(request):
    areas = Area.objects.all()
    return render(request, 'warehouse/area/list_area.html', locals())


def area_by_warehouse(request, wh_code):
    # Lấy đối tượng Warehouse tương ứng với wh_code
    warehouse = Warehouse.objects.get(wh_code=wh_code)

    if warehouse:
        # Lấy tất cả các Area có wh_code là mã kho của warehouse
        areas = Area.objects.filter(warehouse=warehouse)
    else:
        areas = []

    # Truyền dữ liệu vào context
    return render(request, 'warehouse/area/area_by_warehouse.html', locals())


def edit_area(request, area_code):
    area = get_object_or_404(Area, area_id=area_code)
    wh_code = area.warehouse_id

    if request.method == 'POST':
        # Khởi tạo form với dữ liệu từ request
        form = AreaForm(request.POST, request.FILES, instance=area)

        if form.is_valid():
            form.save()  # Lưu các thay đổi vào cơ sở dữ liệu
            return redirect('area_by_warehouse', wh_code=wh_code)
    else:
        form = AreaForm(instance=area)

    return render(request, 'warehouse/area/edit_area.html', locals())


def area_delete(request, pk):
    area = get_object_or_404(Area, pk=pk)
    wh = Area.objects.get(area_id=area).warehouse_id
    if request.method == 'POST':
        # Xóa đối tượng
        area.delete()

        # Trả về phản hồi AJAX nếu yêu cầu là AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX
            return JsonResponse({'message': 'Area deleted successfully.', 'redirect': 'warehouse/list/', 'success': True}, status=200)
        else:
            # Điều hướng thông thường nếu không phải là AJAX
            return redirect(area_by_warehouse, wh_code=wh)

    # Không cần render trang riêng cho việc xóa
    return JsonResponse({'message': 'Invalid request method.'}, status=400)


#Bin
def create_bin(request, area_code):
    # Lấy đối tượng Area từ area_code
    area = get_object_or_404(Area, area_id=area_code)

    if request.method == 'POST':
        form = BinForm(request.POST, request.FILES)
        if form.is_valid():
            # Gắn đối tượng area vào form trước khi lưu
            bin = form.save(commit=False)

            # Gán người dùng vào các trường create_by và update_by
            bin.create_by = request.user if request.user.is_authenticated else 'Unknown'
            bin.update_by = request.user if request.user.is_authenticated else 'Unknown'

            bin.area = area
            bin.save()
            return redirect('bin_by_area', area_code=area_code)  # Điều hướng đến trang bin_by_area
    else:
        # Truyền đối tượng area vào form, không phải chỉ area_code
        form = BinForm(initial={'area': area})

    return render(request, 'warehouse/bin/create_bin.html', locals())


def bin_list(request):
    bins = Bin.objects.all()
    return render(request, 'warehouse/bin/list_bin.html', {'bins': bins})


def edit_bin(request, bin_code):
    bin = get_object_or_404(Bin, bin_id=bin_code)
    area_code = bin.area_id

    if request.method == 'POST':
        # Khởi tạo form với dữ liệu từ request
        form = BinForm(request.POST, request.FILES, instance=bin)

        if form.is_valid():
            form.save()  # Lưu các thay đổi vào cơ sở dữ liệu
            return redirect('bin_by_area', area_code=area_code)
    else:
        form = BinForm(instance=bin)

    return render(request, 'warehouse/bin/edit_bin.html', locals())


def bin_delete(request, pk):

    bin = get_object_or_404(Bin, pk=pk)

    if request.method == 'POST':
        # Xóa đối tượng
        bin.delete()

        # Trả về phản hồi AJAX nếu yêu cầu là AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX
            return JsonResponse({'message': 'Bin deleted successfully.', 'success': True}, status=200)

        # Điều hướng thông thường nếu không phải là AJAX
        return redirect('bin_by_area', area_code=bin.area.area_id)

    # Không cần render trang riêng cho việc xóa
    return JsonResponse({'message': 'Invalid request method.'}, status=400)


def bin_by_area(request, area_code):
    # Lấy đối tượng Warehouse tương ứng với wh_code
    area = Area.objects.get(area_id=area_code)
    wh_code = area.warehouse_id

    if area:
        # Lấy tất cả các Area có wh_code là mã kho của warehouse
        bins = Bin.objects.filter(area=area)
    else:
        bins = []

    # Truyền dữ liệu vào context
    return render(request, 'warehouse/bin/bin_by_area.html', locals())


def bin_search(request):

    form = BinSearchForm(request.GET or None)

    if form.is_valid():
        query_bin = form.cleaned_data.get('bin')
        query_po_no = form.cleaned_data.get('po_no')
        query_size = form.cleaned_data.get('size')
        query_from = form.cleaned_data.get('from_date')
        query_to = form.cleaned_data.get('to_date')

    # message = ""
    # records = None
    # bin_values = None

        if query_bin or query_po_no or query_size:
            bin_hists = Bin_Value_History.objects.all()
            bin_values = Bin_Value.objects.all()

            if query_bin:
                bin_hists = bin_hists.filter(bin__bin_id=query_bin)  # Lọc chính xác mã `bin`
                bin_values = bin_values.filter(bin__bin_id=query_bin)
            if query_po_no:
                bin_hists = bin_hists.filter(po_no=query_po_no)
                bin_values = bin_values.filter(po_no=query_po_no)
            if query_size:
                bin_hists = bin_hists.filter(size=query_size)
                bin_values = bin_values.filter(size=query_size)
            if query_from:
                start_datetime = datetime.combine(query_from, datetime.min.time())  # Đầu ngày (00:00:00)
                bin_hists = bin_hists.filter(create_at__gte=start_datetime)
            if query_to:
                end_datetime = datetime.combine(query_to, datetime.max.time())
                bin_hists = bin_hists.filter(create_at__lte=end_datetime)
            if not bin_hists.exists():
                message = "No matching records found."

            # Lọc kết quả cuối cùng
            result_history = bin_hists
            result_value = bin_values

            page_obj = None
            range_pages = []

            if result_history or result_value:
                result_history = result_history.order_by('-create_at')
                paginator = Paginator(result_history, 15)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)

                total_pages = paginator.num_pages
                current_page = page_obj.number

        else:
            result_history = None
            result_value = None


    return render(request, 'warehouse/search_bin_history.html', locals()
    #               {
    #     'bin_values': bin_values,
    #     'page_obj': page_obj,  # Truyền page_obj thay vì records
    #     'range_pages': range_pages,
    #     'message': message if message else '',  # Truyền message nếu có
    # }
 )


def check_po_exists(request):
    po_no = request.POST.get('po_no')
    bin_id = request.POST.get('bin_id')

    # Kiểm tra xem PO có tồn tại trong cơ sở dữ liệu không
    if Bin_Value.objects.filter(bin=bin_id, po_no=po_no).exists():
        return JsonResponse({'exists': True})
    else:
        return JsonResponse({'exists': False})


def bin_action(request):

    if request.method == 'POST':
        bin_id = request.POST.get('bin')  # Lấy giá trị `bin` từ yêu cầu AJAX
        status = request.POST.get('status')  # Lấy giá trị `status` (nếu có)
        action = request.POST.get('action')

        form = BinSearchForm(request.POST or None, bin_value=bin_id)

        act_type = 'STOCKOUT'

        if status == 'edit':
            # Lấy các giá trị cần thiết từ request
            po = request.POST.get('po')
            size = request.POST.get('size')
            qty = int(request.POST.get('qty'))
            old = int(request.POST.get('qty'))
            old_qty = 0

            try:
                # Lấy bin_object từ bin_id
                bin_object = Bin.objects.get(bin_id=bin_id)
                bin_value = Bin_Value.objects.filter(bin=bin_object, po_no=po).first()

                if bin_value:
                    # So sánh giá trị `po` từ form với `po_no` trong DB
                    if po != bin_value.po_no:
                        act_type = 'STOCKIN'  # Nếu không khớp, gán giá trị act_type = 'STOCK IN'
                    else:
                        old_qty = bin_value.qty
                        qty = old_qty - qty  # Trừ số lượng cũ với số lượng mới được nhập từ form
                else:
                    act_type = 'STOCKIN'  # Nếu không tìm thấy bin_value, coi như nhập mới

                if qty == 0:
                    bin_value.delete()
                elif qty > 0:
                    Bin_Value.objects.update_or_create(
                        bin=bin_object,
                        po_no=po,
                        defaults={
                            'size': size,
                            'qty': qty,
                            'status': 'edit',
                            'update_by': request.user
                        }
                    )
                # new = old - qty
                # Lưu lịch sử
                Bin_Value_History.objects.create(
                    bin=bin_object,
                    po_no=po,
                    size=size,
                    act_type=act_type,
                    old_qty=int(old_qty),
                    act_qty=-int(old),
                    new_qty=int(qty),
                    create_by=request.user
                )

            except Bin.DoesNotExist:
                return JsonResponse({'error': f'Bin {bin_id} does not exist.'}, status=404)

        elif status == 'STOCK':
            po = request.POST.get('po')
            size = request.POST.get('size')
            qty = int(request.POST.get('qty'))

            try:
                # Lấy bin_object từ bin_id
                bin_object = Bin.objects.get(bin_id=bin_id)

                # Cập nhật hoặc tạo mới Bin_Value với số lượng mới
                Bin_Value.objects.update_or_create(
                    bin=bin_object,
                    po_no=po,
                    defaults={
                        'size': size,
                        'qty': qty,
                        'status': 'STOCK',
                        'update_by': request.user
                    }
                )

                # Lưu lịch sử
                Bin_Value_History.objects.create(
                    bin=bin_object,
                    po_no=po,
                    size=size,
                    act_type='STOCKIN',
                    old_qty=0,
                    act_qty=int(qty),
                    new_qty=int(qty),
                    create_by=request.user
                )

            except Bin.DoesNotExist:
                return JsonResponse({'error': f'Bin {bin_id} does not exist.'}, status=404)

        # Lọc dữ liệu theo bin_id và trả về danh sách
        list_bin_value = Bin_Value.objects.filter(bin__bin_id=bin_id).values('bin', 'po_no', 'size', 'qty')
        form = BinSearchForm()
        data = {
            'list_bin_value': list(list_bin_value),
            'message': 'Data successfully updated!',
            'bin_code': bin_id,
            'from': form.fields['from_date'].initial,
            'to': form.fields['to_date'].initial,
        }

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def index(request):
    warehouses = Warehouse.objects.all()
    return render(request, 'warehouse/index.html', locals())



def dashboard(request):

    return render(request, 'warehouse/dashboard.html', locals())


# 入庫作業
@transaction.atomic
@login_required
def stock_in(request):
    bins = Bin.objects.filter(area__warehouse__wh_code='W001').annotate(
        has_stock=Case(
            When(value_bin__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    )

    if request.method == 'POST':
        hidItem_list = request.POST.get('hidItem_list')
        if hidItem_list:
            items = json.loads(hidItem_list)

        apply_date = request.POST.get('apply_date')
        pr_no = request.POST.get('pr_no')
        desc = request.POST.get('desc')

        save_tag = transaction.savepoint()
        try:
            stock_in = StockInForm()
            YYYYMM = datetime.now().strftime("%Y%m")
            key = "SI"+YYYYMM
            stock_in.form_no = key + str(get_series_number(key, "入庫單")).zfill(3)
            stock_in.pr_no = pr_no
            stock_in.requester = request.user
            stock_in.apply_date = apply_date
            stock_in.reason = desc
            stock_in.create_by = request.user
            stock_in.save()

            for item in items:
                Do_Transaction(request, stock_in.form_no, 'STIN', item['item_code'], item['bin_code'], int(item['qty']),
                               item['comment'])

        except Exception as e:
            transaction.savepoint_rollback(save_tag)
            print(e)

        return redirect(stock_in.get_absolute_url())
    form = StockInPForm()
    return render(request, 'warehouse/stock_in.html', locals())


@login_required
def stockin_detail(request, pk):
    # try:
    #     form = StockInForm.objects.get(pk=pk)
    #     items = StockHistory.objects.filter(batch_no=pk)
    # except StockInForm.DoesNotExist:
    #     raise Http404('Form does not exist')

    return render(request, 'stock/stockin_detail.html', locals())


def get_product_order_info(request):
    data_list = []
    if request.method == 'POST':
        product_order = request.POST.get('product_order')
        db = sap_database()

        if product_order == '':
            return JsonResponse({"status": "no_change"}, status=200)
        else:
            sql = f"""
            SELECT VBELN, ZZVERSION, ZZVERSION_SEQ, LOTNO, WGBEZ, EBELN, MENGE_PO, ZSIZE, MEINS, BUDAT, MENGE,
            NAME1, MBLNR
            FROM [PMG_SAP_Test].[dbo].[ZMMT4001] WHERE VBELN = '{product_order}'
            """

        raws = db.select_sql_dict(sql)
        for raw in raws:
            data_list.append({'product_order': raw['VBELN'], 'customer_no': '', 'version_no': raw['ZZVERSION'],
                              'version_seq': raw['ZZVERSION_SEQ'], 'lot_no': raw['LOTNO'], 'item_type': raw['WGBEZ'],
                              'packing_type': '', 'purchase_no': raw['EBELN'], 'purchase_qty': raw['MENGE_PO'],
                              'size': raw['ZSIZE'], 'purchase_unit': raw['MEINS'], 'post_date': raw['BUDAT'],
                              'order_qty': raw['MENGE'], 'supplier': raw['NAME1'], 'sap_mtr_no': raw['MBLNR']
                              })

    return JsonResponse(data_list, safe=False)


def get_product_order_stout(request):
    data_list = []
    if request.method == 'POST':
        product_order = request.POST.get('product_order')
        db = sap_database()

        if product_order == '':
            return JsonResponse({"status": "no_change"}, status=200)
        else:
            sql = f"""
            SELECT [product_order]
                  ,[size]
                  ,[qty]
                  ,[bin_id]
                  ,[purchase_no]
                  ,[version_no]
                  ,[version_seq]
            FROM [VNEDC].[dbo].[warehouse_bin_value] WHERE product_order = '{product_order}'
            """
        raws = db.select_sql_dict(sql)
        for raw in raws:
            data_list.append({'product_order': raw['product_order'], 'size': raw['size'], 'order_qty': raw['qty'],
                              'version_no': raw['version_no'], 'order_bin': raw['bin_id'],
                              'version_seq': raw['version_seq'], 'purchase_no': raw['purchase_no'],

                              })
    return JsonResponse(data_list, safe=False)


def get_purchase_no_info(request):
    data_list = []
    if request.method == 'POST':
        purchase_no = request.POST.get('purchase_no')
        db = sap_database()

        if purchase_no == '':
            return JsonResponse({"status": "no_change"}, status=200)
        else:
            sql = f"""
                    SELECT VBELN, ZZVERSION, ZZVERSION_SEQ, LOTNO, WGBEZ, EBELN, MENGE_PO, ZSIZE, MEINS, BUDAT, MENGE,
                    NAME1, MBLNR
                    FROM [PMG_SAP_Test].[dbo].[ZMMT4001] WHERE EBELN = '{purchase_no}'
                    """

        raws = db.select_sql_dict(sql)

        for raw in raws:
            data_list.append({'product_order': raw['VBELN'], 'customer_no': '', 'version_no': raw['ZZVERSION'],
                              'version_seq': raw['ZZVERSION_SEQ'], 'lot_no': raw['LOTNO'], 'item_type': raw['WGBEZ'],
                              'packing_type': '', 'purchase_no': raw['EBELN'], 'purchase_qty': raw['MENGE_PO'],
                              'size': raw['ZSIZE'], 'purchase_unit': raw['MEINS'], 'post_date': raw['BUDAT'],
                              'order_qty': raw['MENGE'], 'supplier': raw['NAME1'], 'sap_mtr_no': raw['MBLNR']
                              })

    return JsonResponse(data_list, safe=False)


def get_series_number(_key, _key_name):
    obj = Series.objects.filter(key=_key)
    if obj:
        _series = obj[0].series + 1
        obj.update(series=_series, desc=_key_name)
    else:
        _series = 1
        Series.objects.create(key=_key, series=1, desc=_key_name)
    return _series


@csrf_exempt
def stock_in_post(request):
    if request.method == "POST":
        try:
            # 解析 JSON 資料
            data = json.loads(request.body)

            # STIN-202412310001
            YYYYMM = datetime.now().strftime("%Y%m")
            key = "STIN" + YYYYMM
            form_no = key + str(get_series_number(key, "STOCKIN")).zfill(3)

            item_type = None

            mvt = MovementType.objects.get(mvt_code="STIN")

            stockin_form = StockInForm.objects.create(
                form_no=form_no,
                create_at=timezone.now(),
                create_by_id=request.user.id
            )

            for item in data:
                bin = Bin.objects.get(bin_id=item['order_bin'])

                if 'item_type' in item and item['item_type']:
                    try:
                        item_type = ItemType.objects.get(type_name=item['item_type'])

                        stockin_form_detail = StockInFormDetail(
                            form_no=stockin_form,
                            product_order=item['product_order'],
                            customer_no=item['customer_no'],
                            version_no=item['version_no'],
                            version_seq=item['version_seq'],
                            lot_no=item['lot_no'],
                            item_type=item_type,
                            packing_type=item['packing_type'],
                            purchase_no=item['purchase_no'],
                            purchase_qty=item['purchase_qty'],
                            size=item['size'],
                            purchase_unit=item['purchase_unit'],
                            post_date=item['post_date'],
                            order_qty=item['order_qty'],
                            order_bin=bin,
                            supplier=item['supplier'],
                            sap_mtr_no=item['sap_mtr_no'],
                            desc=item['desc'],
                        )
                        stockin_form_detail.save()

                        result = Do_Transaction(request, form_no, item['product_order'],
                                                item['purchase_no'], item['version_no'], item['version_seq'],
                                                item['size'], mvt,
                                                item['order_bin'], item['order_qty'], item['desc'])

                    except ItemType.DoesNotExist:
                        raise ValueError(f"Invalid item_type: {item['item_type']}")

            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


# @transaction.atomic
# @login_required
def stock_out(request):
    if request.method == 'POST':
        form = StockOutPForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = StockOutPForm()
    return render(request, 'warehouse/stock_out.html', {'form': form})


def work_order_search(request):
    product_order = request.GET.get('product_order')

    if not product_order:
        return JsonResponse({"status": "blank"}, status=200)

    bin_values = Bin_Value.objects.select_related(
        'bin__area__warehouse'  # bin->area->warehouse
    ).filter(
        product_order__icontains=product_order
    ).values(
        'bin__area__warehouse__wh_code',
        'product_order',
        'purchase_no',
        'version_no',
        'version_seq',
        'size',
        'bin',
        'qty'
    )

    data = list(bin_values)

    if not data:
        return JsonResponse({"status": "blank"}, status=200)

    return JsonResponse(data, safe=False)


def work_order_page(request):
    return render(request, 'warehouse/work_order_search.html')


# no use this
def bin_transfer(request):
    if request.GET:
        request.session['warehouse'] = request.GET.get('warehouse', '')
        request.session['product_order'] = request.GET.get('product_order', '')
        request.session['purchase_no'] = request.GET.get('purchase_no', '')
        request.session['version_no'] = request.GET.get('version_no', '')
        request.session['version_seq'] = request.GET.get('version_seq', '')
        request.session['size'] = request.GET.get('size', '')
        request.session['bin'] = request.GET.get('bin', '')
        request.session['qty'] = request.GET.get('qty', '')

        # Lấy dữ liệu từ session nếu không có GET request
    warehouse = request.session.get('warehouse', '')
    product_order = request.session.get('product_order', '')
    purchase_no = request.session.get('purchase_no', '')
    version_no = request.session.get('version_no', '')
    version_seq = request.session.get('version_seq', '')
    size = request.session.get('size', '')
    bin = request.session.get('bin', '')
    qty = request.session.get('qty', '')

    item_data = {
        'bin__area__warehouse__wh_code': warehouse,
        'product_order': product_order,
        'purchase_no': purchase_no,
        'version_no': version_no,
        'version_seq': version_seq,
        'size': size,
        'bin': bin,
        'qty': qty
    }

    return JsonResponse(item_data, safe=False)


# When click 'Transfer' button, execute this one
def bin_transfer_page(request):

    if request.GET:
        request.session['warehouse'] = request.GET.get('warehouse', '')
        request.session['product_order'] = request.GET.get('product_order', '')
        request.session['purchase_no'] = request.GET.get('purchase_no', '')
        request.session['version_no'] = request.GET.get('version_no', '')
        request.session['version_seq'] = request.GET.get('version_seq', '')
        request.session['size'] = request.GET.get('size', '')
        request.session['bin'] = request.GET.get('bin', '')
        request.session['qty'] = request.GET.get('qty', '')
        request.session['qty'] = request.GET.get('qty', '')

        # Lấy dữ liệu từ session nếu không có GET request
    warehouse = request.session.get('warehouse', '')
    product_order = request.session.get('product_order', '')
    purchase_no = request.session.get('purchase_no', '')
    version_no = request.session.get('version_no', '')
    version_seq = request.session.get('version_seq', '')
    size = request.session.get('size', '')
    bin = request.session.get('bin', '')
    qty = request.session.get('qty', '')

    mvt = MovementType.objects.get(mvt_code="TRNS")

    YYYYMM = datetime.now().strftime("%Y%m")
    key = "TRNS" + YYYYMM
    form_no = key + str(get_series_number(key, "TRANSFER")).zfill(3)

    if request.method == 'POST':
        form = BinTransferForm(request.POST)
        if form.is_valid():
            bin_selected = form.cleaned_data['bin']
            qty = form.cleaned_data['qty']

            Do_Transaction(request, form_no, product_order, purchase_no, version_no, version_seq, size, mvt,
                           bin_selected, qty, desc=None)
            Do_Transaction(request, form_no, product_order, purchase_no, version_no, version_seq, size, mvt,
                           bin, -qty, desc=None)

            item_data = {
                'bin__area__warehouse__wh_code': warehouse,
                'product_order': product_order,
                'purchase_no': purchase_no,
                'version_no': version_no,
                'version_seq': version_seq,
                'size': size,
                'bin': bin,
                'qty': qty
            }
            return render(request, 'warehouse/work_order_search.html', locals())
    form = BinTransferForm()

    return render(request, 'warehouse/bin/bin_transfer.html', locals())
    # return JsonResponse(item_data, safe=False)


