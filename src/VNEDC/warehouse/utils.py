import datetime
import uuid

from warehouse.models import MovementType, Bin, Bin_Value, Bin_Value_History


def Do_Transaction(request, form_no, product_order, purchase_no, version_no, version_seq, size, mvt, bin_code, qty, purchase_unit, desc):
    try:
        qty = float(qty)
        bin = Bin.objects.get(bin_id=bin_code)
        mvt = MovementType.objects.get(mvt_code=mvt)
        if bin and product_order and purchase_no:
            # 更新庫存資料
            invs = Bin_Value.objects.filter(product_order=product_order, purchase_no=purchase_no, version_no=version_no,
                                            version_seq=version_seq, size=size, bin=bin)
            if invs:
                remain_qty = int(invs.first().qty) + qty
            else:
                remain_qty = qty

            if remain_qty >= 0:
                if remain_qty == 0:
                    Bin_Value.objects.filter(product_order=product_order, purchase_no=purchase_no,
                                                       version_no=version_no,
                                                       version_seq=version_seq, size=size, bin=bin).delete()
                else:
                    Bin_Value.objects.update_or_create(product_order=product_order, purchase_no=purchase_no,
                                                       version_no=version_no,
                                                       version_seq=version_seq, size=size, bin=bin,
                                                       defaults={'qty': remain_qty, 'purchase_unit': purchase_unit, 'update_by': request.user})

                if qty > 0:
                    Bin_Value_History.objects.create(batch_no=form_no, product_order=product_order,
                                                     purchase_no=purchase_no, version_no=version_no,
                                                     version_seq=version_seq, size=size, bin=bin, mvt=mvt, plus_qty=qty,
                                                     minus_qty=0, remain_qty=remain_qty, comment=desc,
                                                     purchase_unit=purchase_unit,
                                                     create_by=request.user)
                else:
                    Bin_Value_History.objects.create(batch_no=form_no, product_order=product_order,
                                                     purchase_no=purchase_no, version_no=version_no,
                                                     version_seq=version_seq, size=size, bin=bin, mvt=mvt, plus_qty=0,
                                                     minus_qty=-qty, remain_qty=remain_qty,
                                                     purchase_unit=purchase_unit,
                                                     comment=desc, create_by=request.user)
                result = "DONE"
            else:
                msg = '無庫存可以扣帳'
                print(msg)
                raise ValueError(msg)
    except Exception as e:
        print(e)
        result = "ERROR"
    return result


def transfer_stock(product_order, purchase_no, version_no, version_seq, size, bin_code_from, bin_code_to, warehouse, qty):
    try:
        # Bước 1: Kiểm tra số lượng trong kho xuất
        bin_from = Bin_Value.objects.get(product_order=product_order, purchase_no=purchase_no, version_no=version_no,
                                         version_seq=version_seq, size=size, bin_id=bin_code_from,
                                         bin__area__warehouse__wh_code=warehouse)
        bin_to = Bin_Value.objects.get(bin_id=bin_code_to, bin__area__warehouse__wh_code=warehouse,
                                       product_order=product_order, purchase_no=purchase_no, version_no=version_no,
                                       version_seq=version_seq, size=size,)

        # Lấy thông tin sản phẩm trong kho xuất
        inv_from = Bin_Value.objects.filter(
            product_order=product_order,
            purchase_no=purchase_no,
            version_no=version_no,
            version_seq=version_seq,
            size=size,
            bin_id=bin_from.bin_id
        ).first()
        print(inv_from)

        if not inv_from or inv_from.qty < qty:
            raise ValueError("Không đủ số lượng trong kho xuất.")

        # Bước 2: Cập nhật số lượng trong kho xuất (giảm số lượng)
        inv_from.qty -= qty
        inv_from.save()

        # Bước 3: Kiểm tra và cập nhật số lượng trong kho đích
        inv_to = Bin_Value.objects.filter(
            product_order=product_order,
            purchase_no=purchase_no,
            version_no=version_no,
            version_seq=version_seq,
            size=size,
            bin=bin_to.bin_id
        ).first()

        if inv_to:
            # Nếu kho đích đã có sản phẩm, cập nhật số lượng
            inv_to.qty += qty
        else:
            # Nếu kho đích chưa có sản phẩm, tạo mới
            inv_to = Bin_Value(
                product_order=product_order,
                purchase_no=purchase_no,
                version_no=version_no,
                version_seq=version_seq,
                size=size,
                bin=bin_to,
                qty=qty,
                status="IN_TRANSIT"  # Ví dụ trạng thái trong quá trình chuyển
            )
        inv_to.save()

        return {"success": True, "message": "Chuyển hàng thành công."}

    except Exception as e:
        return {"success": False, "message": str(e)}

















