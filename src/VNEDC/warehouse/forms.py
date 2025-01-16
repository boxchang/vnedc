from datetime import timedelta, date, datetime

from django import forms
import PIL
from PIL import Image
from bootstrap_datepicker_plus.widgets import DatePickerInput
from warehouse.models import Warehouse, Area, Bin, ItemType, PackMethod, UnitType, Bin_Value
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Button, Submit, HTML
from django.utils.translation import gettext_lazy as _
from django import forms


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse  # Chỉ định model mà form này sẽ sử dụng
        fields = ['wh_code', 'wh_name', 'wh_comment', 'wh_bg']

    wh_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    wh_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    wh_comment = forms.CharField(max_length=500, required=False, widget=forms.Textarea(attrs={'class': 'form-control'}))
    wh_bg = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def save(self, commit=True):
        # Lấy instance của Warehouse từ dữ liệu form
        instance = super().save(commit=False)

        # Thực hiện các xử lý bổ sung trước khi lưu (nếu cần)
        if commit:
            instance.save()
        return instance

    def edit(self, commit=True):
        # Lấy instance của Warehouse từ dữ liệu form
        instance = super().save(commit=False)

        # Thực hiện các xử lý bổ sung trước khi lưu (nếu cần)
        if commit:
            instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Kiểm tra nếu là form chỉnh sửa
        if self.instance and self.instance.pk:  # Kiểm tra nếu đối tượng đã tồn tại
            self.fields['wh_code'].widget.attrs['readonly'] = 'readonly'


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area  # Chỉ định model mà form này sẽ sử dụng
        fields = ['area_id', 'area_name', 'warehouse']

    area_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    area_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),  # Lấy tất cả các đối tượng Warehouse
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.fields['warehouse'].queryset)  # Debug queryset
        # Kiểm tra nếu là form chỉnh sửa
        if self.instance and self.instance.pk:  # Kiểm tra nếu đối tượng đã tồn tại
            self.fields['area_id'].widget.attrs['readonly'] = 'readonly'

    def save(self, commit=True):
        # Lấy instance của Warehouse từ dữ liệu form
        instance = super().save(commit=False)

        # Thực hiện các xử lý bổ sung trước khi lưu (nếu cần)
        if commit:
            instance.save()
        return instance

    def edit(self, commit=True):
        # Lấy instance của Warehouse từ dữ liệu form
        instance = super().save(commit=False)

        # Thực hiện các xử lý bổ sung trước khi lưu (nếu cần)
        if commit:
            instance.save()
        return instance


class BinForm(forms.ModelForm):
    class Meta:
        model = Bin  # Chỉ định model mà form này sẽ sử dụng
        fields = ['bin_id', 'bin_name', 'area', 'pos_x', 'pos_y', 'bin_w', 'bin_l']

    bin_id = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    bin_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    area = forms.ModelChoiceField(
        queryset=Area.objects.all(),  # Lấy tất cả các đối tượng Area
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    pos_x = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    pos_y = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    bin_w = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    bin_l = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def save(self, commit=True):
        # Lấy instance của Bin từ dữ liệu form
        instance = super().save(commit=False)

        # Thực hiện các xử lý bổ sung trước khi lưu (nếu cần)
        if commit:
            instance.save()
        return instance

    def edit(self, commit=True):
        # Lấy instance của Warehouse từ dữ liệu form
        instance = super().save(commit=False)

        # Thực hiện các xử lý bổ sung trước khi lưu (nếu cần)
        if commit:
            instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Kiểm tra nếu là form chỉnh sửa
        if self.instance and self.instance.pk:  # Kiểm tra nếu đối tượng đã tồn tại
            self.fields['bin_id'].widget.attrs['readonly'] = 'readonly'


class BinValueForm(forms.Form):
    bin = forms.CharField(
        required=True,
        label=_('Bin'),
        max_length=20,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    po_no = forms.CharField(required=True, label=_('Product Order'), max_length=20)
    size = forms.CharField(required=True, label=_('Size'), max_length=20)
    qty = forms.IntegerField(required=True, label=_('Qty'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.layout = Layout(
            Div(
                Div('bin', css_class='col-md-10'),  # Đặt class input-container vào div chứa bin
                Div(
                    HTML(
                        f"<div id='history_link'></div>"),
                    css_class='col-md-2'
                ),
                css_class='row'
            ),
            Div(
                Div('po_no', css_class='col-md-12'),
                css_class='row'
            ),
            Div(
                Div('size', css_class='col-md-12'),
                css_class='row'
            ),
            Div(
                Div('qty', css_class='col-md-12'),
                css_class='row'
            ),
        )


class BinSearchForm(forms.Form):
    bin = forms.CharField(
        required=False,
        label="Bin:",
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-left: 4vh'}))
    po_no = forms.CharField(
        required=False,
        label="PO:",
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-left: 4vh'}))
    size = forms.CharField(
        required=False,
        label="Size",
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-left: 4vh'})
    )
    from_date = forms.DateField(
        required=False,
        label="From",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'style': 'margin-left: 2vh'})
    )
    to_date = forms.DateField(
        required=False,
        label="To",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'style': 'margin-left: 5vh'})
    )

    def __init__(self, *args, bin_value=None, **kwargs):
        day7_ago = date.today() - timedelta(days=7)
        today = date.today()
        super().__init__(*args, **kwargs)
        self.fields['from_date'].initial = day7_ago
        self.fields['to_date'].initial = today


class BinTransferForm(forms.Form):
    bin = forms.ChoiceField(
        choices=[(bin['bin_id'], bin['bin_id']) for bin in Bin_Value.objects.values('bin_id').distinct()],
        label="Bin:",
        required=True,
    )
    # po = forms.ChoiceField(
    #     choices=[(po['product_order'], po['product_order']) for po in Bin_Value.objects.values('product_order').distinct()],
    #     label="Product Order:",
    #     required=True,
    # )
    # pn = forms.ChoiceField(
    #     choices=[(pn['purchase_no'], pn['purchase_no']) for pn in Bin_Value.objects.values('purchase_no').distinct()],
    #     label="Purchase No:",
    #     required=True,
    # )
    # vn = forms.ChoiceField(
    #     choices=[(vn['version_no'], vn['version_no']) for vn in Bin_Value.objects.values('version_no').distinct()],
    #     label="Version No:",
    #     required=True,
    # )
    # vs = forms.ChoiceField(
    #     choices=[(vs['version_seq'], vs['version_seq']) for vs in Bin_Value.objects.values('version_seq').distinct()],
    #     label="Version Seq:",
    #     required=True,
    # )
    # size = forms.ChoiceField(
    #     choices=[(size['size'], size['size']) for size in Bin_Value.objects.values('size').distinct()],
    #     label="Size:",
    #     required=True,
    # )
    qty = forms.IntegerField(label="Quantity", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.layout = Layout(
            Div(
                Div('bin', css_class='col-md-6'),
                # Div('size', css_class='col-md-3'),
                Div('qty', css_class='col-md-5'),
                Submit('submit', 'Confirm', css_class='btn btn-primary col-md-1', style='height: 50%; margin-top: 2.5%;'
                                                                                        'padding-right: 10px'),
                css_class='row'
            ),
            # Div(
            #     Div('po', css_class='col-md-3'),
            #     Div('pn', css_class='col-md-3'),
            #     Div('vn', css_class='col-md-3'),
            #     Div('vs', css_class='col-md-2'),
            #     css_class='row'
            # ),

        )


class StockInPForm(forms.Form):
    product_order = forms.CharField(max_length=20, label="訂單", required=False, )  # VBELN 收貨單號
    customer_no = forms.CharField(max_length=20, label="客戶", required=False,)  # 無
    version_no = forms.CharField(max_length=20, label="包裝版本號", required=False,)  # ZZVERSION
    version_seq = forms.CharField(max_length=20, label="版次", required=False, )  # ZZVERSION_SEQ
    lot_no = forms.CharField(max_length=20, label="LOT NUMBER", required=False, )  # LOTNO
    item_type = forms.ModelChoiceField(queryset=ItemType.objects.all(), label="收貨類型", required=True)
    # item_type = forms.CharField(max_length=20, label="收貨類型", required=False, )  # WGBEZ 物料群組說明
    # packing_type = forms.CharField(max_length=20, label="包裝方式", required=False, )  # 包裝方式
    packing_type = forms.ModelChoiceField(queryset=PackMethod.objects.all(), label="包裝方式")
    purchase_no = forms.CharField(max_length=20, label="採購單號", required=False, )  # EBELN 採購單號
    purchase_qty = forms.CharField(max_length=20, label="採購數量", required=False, )  # MENGE_PO 採購數量
    size = forms.CharField(max_length=20, label="SIZE", required=False, )  # ZSIZE 尺寸
    # purchase_unit = forms.CharField(max_length=20, label="採購單位", required=False, )  # MEINS 數量單位
    purchase_unit = forms.ModelChoiceField(queryset=UnitType.objects.all(), label="單位")
    post_date = forms.DateField(label="過帳日期")  # BUDAT收貨日期
    order_qty = forms.CharField(max_length=20, label="收貨數量", required=False, initial=0)  # MENGE
    # order_bin = forms.CharField(max_length=20, label="訂單儲格", required=False, )
    order_bin = forms.ModelChoiceField(queryset=Bin.objects.all(), label="訂單儲格")
    gift_qty = forms.CharField(max_length=20, label="贈品數量", required=False, initial=0)
    gift_bin = forms.CharField(max_length=20, label="贈品儲格", required=False, )
    supplier = forms.CharField(max_length=10, label="供應商", required=False)  # NAME1
    sap_mtr_no = forms.CharField(max_length=20, label="物料文件", required=False, )  # MBLNR
    desc = forms.CharField(max_length=2000, label="備註", required=False, widget=forms.Textarea(attrs={'rows': 2, 'cols': 15}))
    # comment = forms.CharField(max_length=200, label="備註", required=False, )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True

        self.helper.layout = Layout(
            Div(
                Div('purchase_no', css_class='col-md-3'),
                Div('customer_no', css_class='col-md-3'),
                Div('version_no', css_class='col-md-3'),
                Div('version_seq', css_class='col-md-3'),
                css_class='row'),
            Div(
                Div('product_order', css_class='col-md-3'),
                Div('sap_mtr_no', css_class='col-md-3'),
                Div('item_type', css_class='col-md-3'),
                Div('packing_type', css_class='col-md-3'),
                css_class='row'),
            Div(
                Div('post_date', css_class='col-md-3'),
                Div('supplier', css_class='col-md-3'),
                Div('lot_no', css_class='col-md-2'),
                Div('size', css_class='col-md-2'),
                Div(Button('bin_clear', '刪除', css_class='btn btn-light'),
                    css_class='col-md-1 d-flex align-items-center pt-3'),
                Div('purchase_qty', css_class='col-md-3'),
                Div('purchase_unit', css_class='col-md-3'),
                Div('order_qty', css_class='col-md-2'),
                Div('order_bin', css_class='col-md-2'),
                Div(Button('bin_search', '查詢', css_class='btn btn-light'),
                    css_class='col-md-1 d-flex align-items-center pt-3'),
                Div('desc', css_class='col-md-10'),
                Div(HTML(
                    '<a href="#" class="btn btn-info" id="create""><i class="fas fa-plus-circle"></i> 加入</a>'),
                    css_class='col-md-2 d-flex align-items-center pt-3'),
                css_class='row'),
        )

        self.fields['post_date'].widget = DatePickerInput(
            attrs={'value': (datetime.now()).strftime('%Y-%m-%d')},
            options={
                "format": "YYYY-MM-DD",
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
            }
        )


class StockInPForm2(forms.Form):
    product_order = forms.CharField(max_length=20, label="訂單", required=False, )  # VBELN 收貨單號
    customer_no = forms.CharField(max_length=20, label="客戶", required=False,)  # 無
    version_no = forms.CharField(max_length=20, label="包裝版本號", required=False,)  # ZZVERSION
    version_seq = forms.CharField(max_length=20, label="版次", required=False, )  # ZZVERSION_SEQ
    lot_no = forms.CharField(max_length=20, label="LOT NUMBER", required=False, )  # LOTNO
    item_type = forms.CharField(max_length=20, label="收貨類型", required=False, )  # WGBEZ 物料群組說明
    packing_type = forms.CharField(max_length=20, label="包裝方式", required=False, )  # 包裝方式
    purchase_no = forms.CharField(max_length=20, label="採購單號", required=False, )  # EBELN 採購單號
    purchase_qty = forms.CharField(max_length=20, label="採購數量", required=False, )  # MENGE_PO 採購數量
    size = forms.CharField(max_length=20, label="SIZE", required=False, )  # ZSIZE 尺寸
    purchase_unit = forms.CharField(max_length=20, label="採購單位", required=False, )  # MEINS 數量單位
    post_date = forms.DateField(label="過帳日期")  # BUDAT收貨日期
    order_qty = forms.CharField(max_length=20, label="收貨數量", required=False, initial=0)  # MENGE
    order_bin = forms.CharField(max_length=20, label="訂單儲格", required=False, )
    gift_qty = forms.CharField(max_length=20, label="贈品數量", required=False, initial=0)
    gift_bin = forms.CharField(max_length=20, label="贈品儲格", required=False, )
    supplier = forms.CharField(max_length=10, label="供應商", required=False)  # NAME1
    sap_mtr_no = forms.CharField(max_length=20, label="物料文件", required=False, )  # MBLNR
    desc = forms.CharField(max_length=2000, label="備註", required=False, widget=forms.Textarea(attrs={'rows': 2, 'cols': 15}))
    comment = forms.CharField(max_length=200, label="備註", required=False, )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True

        self.helper.layout = Layout(
            Div(
                Div('product_order', css_class='col-md-3'),
                Div('customer_no', css_class='col-md-3'),
                Div('version_no', css_class='col-md-3'),
                Div('version_seq', css_class='col-md-3'),
                css_class='row'),
            Div(
                Div('post_date', css_class='col-md-3'),
                Div('sap_mtr_no', css_class='col-md-3'),
                Div('item_type', css_class='col-md-3'),
                Div('packing_type', css_class='col-md-3'),
                Div('', css_class='col-md-3'),
                css_class='row'),
            Div(
                Div('purchase_no', css_class='col-md-3'),
                Div('supplier', css_class='col-md-3'),
                Div('lot_no', css_class='col-md-2'),
                Div('size', css_class='col-md-2'),
                Div('purchase_qty', css_class='col-md-3'),
                Div('purchase_unit', css_class='col-md-3'),
                Div('order_qty', css_class='col-md-2'),
                Div('order_bin', css_class='col-md-2'),
                Div(Button('bin_search', '查詢', css_class='btn btn-light', onclick="stock_item_popup();"),
                    css_class='col-md-1 d-flex align-items-center pt-3'),
                Div('comment', css_class='col-md-10'),
                Div(HTML(
                    '<a href="#" class="btn btn-info" onclick="add_item();"><i class="fas fa-plus-circle"></i> 加入</a>'),
                    css_class='col-md-2 d-flex align-items-center pt-3'),
                css_class='row'),
        )

        self.fields['post_date'].widget = DatePickerInput(
            attrs={'value': (datetime.now()).strftime('%Y-%m-%d')},
            options={
                "format": "YYYY-MM-DD",
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
            }
        )


class StockOutPForm(forms.Form):
    product_order = forms.CharField(max_length=20, label="訂單", required=False, )  # VBELN 收貨單號
    # customer_no = forms.CharField(max_length=20, label="客戶", required=False,)  # 無
    # version_no = forms.CharField(max_length=20, label="包裝版本號", required=False,)  # ZZVERSION
    # version_seq = forms.CharField(max_length=20, label="版次", required=False, )  # ZZVERSION_SEQ
    # lot_no = forms.CharField(max_length=20, label="LOT NUMBER", required=False, )  # LOTNO
    # item_type = forms.ModelChoiceField(queryset=ItemType.objects.all(), label="收貨類型", required=True)
    # item_type = forms.CharField(max_length=20, label="收貨類型", required=False, )  # WGBEZ 物料群組說明
    # packing_type = forms.CharField(max_length=20, label="包裝方式", required=False, )  # 包裝方式
    # packing_type = forms.ModelChoiceField(queryset=PackMethod.objects.all(), label="包裝方式")
    purchase_no = forms.CharField(max_length=20, label="採購單號", required=False, )  # EBELN 採購單號
    # purchase_qty = forms.CharField(max_length=20, label="採購數量", required=False, )  # MENGE_PO 採購數量
    # size = forms.CharField(max_length=20, label="SIZE", required=False, )  # ZSIZE 尺寸
    # purchase_unit = forms.CharField(max_length=20, label="採購單位", required=False, )  # MEINS 數量單位
    # purchase_unit = forms.ModelChoiceField(queryset=UnitType.objects.all(), label="單位")
    # post_date = forms.DateField(label="過帳日期")  # BUDAT收貨日期
    # order_qty = forms.CharField(max_length=20, label="收貨數量", required=False, initial=0)  # MENGE
    # order_bin = forms.CharField(max_length=20, label="訂單儲格", required=False, )
    # order_bin = forms.ModelChoiceField(queryset=Bin.objects.all(), label="訂單儲格")
    # gift_qty = forms.CharField(max_length=20, label="贈品數量", required=False, initial=0)
    # gift_bin = forms.CharField(max_length=20, label="贈品儲格", required=False, )
    # supplier = forms.CharField(max_length=10, label="供應商", required=False)  # NAME1
    # sap_mtr_no = forms.CharField(max_length=20, label="物料文件", required=False, )  # MBLNR
    # desc = forms.CharField(max_length=2000, label="備註", required=False, widget=forms.Textarea(attrs={'rows': 2, 'cols': 15}))
    # comment = forms.CharField(max_length=200, label="備註", required=False, )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True

        self.helper.layout = Layout(
            Div(
                Div('product_order', css_class='col-md-6'),
                Div('purchase_no', css_class='col-md-6'),
                css_class='row')

        )


# class StockOutPForm(forms.Form):
#     apply_date = forms.DateField(label="異動日期")
#     desc = forms.CharField(max_length=250, label="說明", required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 15}))
#     item_code = forms.CharField(max_length=20, label="料號", required=False,)
#     bin_code = forms.CharField(max_length=20, label="儲格", required=False, )
#     qty = forms.CharField(max_length=10, label="數量", required=False, initial=1)
#     comment = forms.CharField(max_length=30, label="備註", required=False, )
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         self.helper = FormHelper()
#         self.helper.form_tag = False
#         self.helper.form_show_errors = True
#
#         self.helper.layout = Layout(
#             Div(
#                 Div('apply_date', css_class='col-md-3'),
#                 css_class='row'),
#             Div(
#                 Div('desc', css_class='col-md-12'),
#                 css_class='row'),
#             Div(
#                 Div('item_code', css_class='col-md-2'),
#                 Div('bin_code', css_class='col-md-2'),
#                 Div(Button('bin_search', '查詢', css_class='btn btn-light', onclick="stock_item_popup();"),
#                     css_class='col-md-1 d-flex align-items-center pt-3'),
#                 Div('qty', css_class='col-md-1'),
#                 Div('comment', css_class='col-md-3'),
#                 Div(HTML(
#                     '<a href="#" class="btn btn-info" onclick="add_item();"><i class="fas fa-plus-circle"></i> 加入</a>'),
#                     css_class='col-md-2 d-flex align-items-center pt-3'),
#                 css_class='row'),
#         )
#
#         self.fields['apply_date'].widget = DatePickerInput(
#             attrs={'value': (datetime.now()).strftime('%Y-%m-%d')},
#             options={
#                 "format": "YYYY-MM-DD",
#                 "showClose": False,
#                 "showClear": False,
#                 "showTodayButton": False,
#             }
#         )


# class StockOutPForm(forms.Form):
#     product_order = forms.CharField(max_length=20, label="訂單", required=False, )  # VBELN 收貨單號
#     # customer_no = forms.CharField(max_length=20, label="客戶", required=False,)  # 無
#     version_no = forms.CharField(max_length=20, label="包裝版本號", required=False,)  # ZZVERSION
#     version_seq = forms.CharField(max_length=20, label="版次", required=False, )  # ZZVERSION_SEQ
#     # lot_no = forms.CharField(max_length=20, label="LOT NUMBER", required=False, )  # LOTNO
#     # item_type = forms.ModelChoiceField(queryset=ItemType.objects.all(), label="收貨類型", required=True)
#     # item_type = forms.CharField(max_length=20, label="收貨類型", required=False, )  # WGBEZ 物料群組說明
#     # packing_type = forms.CharField(max_length=20, label="包裝方式", required=False, )  # 包裝方式
#     # packing_type = forms.ModelChoiceField(queryset=PackMethod.objects.all(), label="包裝方式")
#     purchase_no = forms.CharField(max_length=20, label="採購單號", required=False, )  # EBELN 採購單號
#     # purchase_qty = forms.CharField(max_length=20, label="採購數量", required=False, )  # MENGE_PO 採購數量
#     size = forms.CharField(max_length=20, label="SIZE", required=False, )  # ZSIZE 尺寸
#     # purchase_unit = forms.CharField(max_length=20, label="採購單位", required=False, )  # MEINS 數量單位
#     # purchase_unit = forms.ModelChoiceField(queryset=UnitType.objects.all(), label="單位")
#     post_date = forms.DateField(label="過帳日期")  # BUDAT收貨日期
#     order_qty = forms.CharField(max_length=20, label="收貨數量", required=False, initial=0)  # MENGE
#     # order_bin = forms.CharField(max_length=20, label="訂單儲格", required=False, )
#     order_bin = forms.ModelChoiceField(queryset=Bin.objects.all(), label="訂單儲格")
#     gift_qty = forms.CharField(max_length=20, label="贈品數量", required=False, initial=0)
#     gift_bin = forms.CharField(max_length=20, label="贈品儲格", required=False, )
#     # supplier = forms.CharField(max_length=10, label="供應商", required=False)  # NAME1
#     # sap_mtr_no = forms.CharField(max_length=20, label="物料文件", required=False, )  # MBLNR
#     desc = forms.CharField(max_length=2000, label="備註", required=False, widget=forms.Textarea(attrs={'rows': 2, 'cols': 15}))
#     # comment = forms.CharField(max_length=200, label="備註", required=False, )
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         self.helper = FormHelper()
#         self.helper.form_tag = False
#         self.helper.form_show_errors = True
#
#         self.helper.layout = Layout(
#             Div(
#                 Div('product_order', css_class='col-md-3'),
#                 Div('version_no', css_class='col-md-3'),
#                 Div('version_seq', css_class='col-md-3'),
#                 Div('purchase_no', css_class='col-md-3'),
#                 css_class='row'),
#             Div(
#                 Div('post_date', css_class='col-md-3'),
#                 Div('size', css_class='col-md-2'),
#
#                 Div('order_qty', css_class='col-md-2'),
#                 Div('order_bin', css_class='col-md-2'),
#                 Div(Button('bin_clear', '刪除', css_class='btn btn-light', onclick="stock_item_popup();"),
#                     css_class='col-md-1 d-flex align-items-center pt-3'),
#                 Div(Button('bin_search', '查詢', css_class='btn btn-light', onclick="stock_item_popup();"),
#                     css_class='col-md-1 d-flex align-items-center pt-3'),
#                 Div('desc', css_class='col-md-10'),
#                 Div(HTML(
#                     '<a href="#" class="btn btn-info" id="create""><i class="fas fa-plus-circle"></i> 加入</a>'),
#                     css_class='col-md-2 d-flex align-items-center pt-3'),
#                 css_class='row'),
#         )
#
#         self.fields['post_date'].widget = DatePickerInput(
#             attrs={'value': (datetime.now()).strftime('%Y-%m-%d')},
#             options={
#                 "format": "YYYY-MM-DD",
#                 "showClose": False,
#                 "showClear": False,
#                 "showTodayButton": False,
#             }
#         )



