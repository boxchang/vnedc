from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import WarehouseForm, AreaForm, BinForm
from .models import Warehouse, Area, Bin


# Warehouse
def create_warehouse(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST, request.FILES)  # Xử lý dữ liệu POST và FILES
        if form.is_valid():
            form.save()  # Lưu dữ liệu vào database
            return redirect('warehouse_list')  # Điều hướng đến trang thành công
    else:
        form = WarehouseForm()  # Tạo form trống

    return render(request, 'warehouse/create_warehouse.html', {'form': form})

def warehouse_list(request):
    # Lấy toàn bộ danh sách warehouse từ cơ sở dữ liệu
    warehouses = Warehouse.objects.all()

    return render(request, 'warehouse/list_warehouse.html', {'warehouses': warehouses})

def edit_warehouse(request, warehouse_code):
    # Lấy đối tượng Warehouse cần chỉnh sửa dựa trên mã kho (wh_code)
    warehouse = get_object_or_404(Warehouse, wh_code=warehouse_code)

    if request.method == 'POST':
        # Khởi tạo form với dữ liệu từ request
        form = WarehouseForm(request.POST, request.FILES, instance=warehouse)

        if form.is_valid():
            form.save()  # Lưu các thay đổi vào cơ sở dữ liệu
            # messages.success(request, "Warehouse updated successfully!")  # Thông báo thành công
            return redirect('warehouse_list')  # Điều hướng về danh sách kho
    else:
        # Khởi tạo form với dữ liệu hiện tại của warehouse
        form = WarehouseForm(instance=warehouse)

    return render(request, 'warehouse/edit_warehouse.html', {'form': form, 'warehouse': warehouse})


def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)

    if request.method == 'POST':
        # Xóa đối tượng
        warehouse.delete()

        # Trả về phản hồi AJAX nếu yêu cầu là AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX
            return JsonResponse({'message': 'Warehouse deleted successfully.', 'success': True}, status=200)

        # Điều hướng thông thường nếu không phải là AJAX
        return redirect('warehouse_list')

    # Không cần render trang riêng cho việc xóa
    return JsonResponse({'message': 'Invalid request method.'}, status=400)


def test(request):

    warehouse_image = Warehouse.objects.get(wh_code='TEST')
    x = warehouse_image

    return render(request, 'warehouse/test.html', {'warehouse_image': warehouse_image})


# Area
def create_area(request, wh_code):
    if request.method == 'POST':
        form = AreaForm(request.POST)  # Xử lý dữ liệu POST và FILES
        if form.is_valid():
            form.save()  # Lưu dữ liệu vào database
            return redirect('area_by_warehouse', wh_code=wh_code)  # Điều hướng đến trang thành công
    else:
        form = AreaForm(initial={'warehouse': wh_code})  # Tạo form trống

    return render(request, 'warehouse/area/create_area.html', {'form': form})

def area_list(request):
    areas = Area.objects.all()
    return render(request, 'warehouse/area/list_area.html', {'areas': areas})

def area_by_warehouse(request, wh_code):
    # Lấy đối tượng Warehouse tương ứng với wh_code
    warehouse = Warehouse.objects.get(wh_code=wh_code)

    if warehouse:
        # Lấy tất cả các Area có wh_code là mã kho của warehouse
        areas = Area.objects.filter(warehouse=warehouse)
    else:
        areas = []

    # Truyền dữ liệu vào context
    return render(request, 'warehouse/area/area_by_warehouse.html', {'areas': areas, 'warehouse': warehouse, 'wh_code': wh_code})


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

    return render(request, 'warehouse/area/edit_area.html', {'form': form, 'area': area})


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
            return redirect(f'area_by_warehouse', wh_code=wh)

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
            bin_instance = form.save(commit=False)
            bin_instance.area = area
            bin_instance.save()
            return redirect('bin_by_area', area_code=area_code)  # Điều hướng đến trang bin_by_area
    else:
        # Truyền đối tượng area vào form, không phải chỉ area_code
        form = BinForm(initial={'area': area})

    return render(request, 'warehouse/bin/create_bin.html', {'form': form, 'area': area})

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

    return render(request, 'warehouse/bin/edit_bin.html', {'form': form, 'bin': bin, 'area_code': area_code})


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
    return render(request, 'warehouse/bin/bin_by_area.html', {'bins': bins, 'area': area, 'area_code': area_code, 'wh_code': wh_code})

def index(request):
    return render(request, 'warehouse/index.html')