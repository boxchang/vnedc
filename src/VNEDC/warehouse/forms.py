from datetime import timedelta, date, datetime

from django import forms
import PIL
from PIL import Image
from bootstrap_datepicker_plus.widgets import DatePickerInput
from warehouse.models import Warehouse, Area, Bin, ItemType, PackMethod, UnitType, Bin_Value, Plant
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Button, Submit, HTML
from django.utils.translation import gettext_lazy as _
from django import forms


class WarehouseForm(forms.ModelForm):
    wh_plant = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Warehouse  # Chỉ định model mà form này sẽ sử dụng
        fields = ['wh_code', 'wh_name', 'wh_comment', 'wh_plant', 'wh_bg']

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

        # Lấy danh sách Plant từ database
        plant_choices = Plant.objects.values_list('plant_code', 'plant_name')

        # Gán danh sách lựa chọn vào ChoiceField
        self.fields['wh_plant'].choices = [('', 'Choose Plant')] + list(plant_choices)

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
        label=_("Location:"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-left: 4vh'}))
    po_no = forms.CharField(
        required=False,
        label=_("Product Order:"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-left: 4vh'}))
    size = forms.CharField(
        required=False,
        label=_("Size"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-left: 4vh'})
    )
    from_date = forms.DateField(
        required=False,
        label=_("From"),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'style': 'margin-left: 2vh'})
    )
    to_date = forms.DateField(
        required=False,
        label=_("To"),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'style': 'margin-left: 5vh'})
    )

    def __init__(self, *args, bin_value=None, **kwargs):
        day7_ago = date.today() - timedelta(days=7)
        today = date.today()
        super().__init__(*args, **kwargs)
        self.fields['from_date'].initial = day7_ago
        self.fields['to_date'].initial = today


class BinTransferForm(forms.Form):
    bin = forms.ModelChoiceField(
        queryset=Bin.objects.all().order_by('bin_id'),
        label="Location:",
        required=True,
    )

    qty = forms.IntegerField(label="Quantity", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.layout = Layout(
            Div(
                Div('bin', css_class='col-md-6'),
                Div('qty', css_class='col-md-5'),
                Submit('submit', 'Confirm', css_class='btn btn-primary col-md-1', style='height: 50%; margin-top: 2.5%;'
                                                                                        'padding-right: 10px'),
                css_class='row'
            ),
        )

class QuantityAdjustForm(forms.Form):

    qty = forms.IntegerField(label="Quantity", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.layout = Layout(
            Div(
                Div('', css_class='col-md-5'),
                Div('qty', css_class='col-md-5'),
                Submit('submit', 'Confirm', css_class='btn btn-primary col-md-1', style='height: 50%; margin-top: 2.5%;'
                                                                                        'padding-right: 10px'),
                css_class='row'
            ),
        )

class StockInPForm(forms.Form):
    product_order = forms.CharField(max_length=20, label=_("Product Order"), required=True, )  # VBELN 收貨單號
    customer_no = forms.CharField(max_length=20, label=_("Customer"), required=False,)  # 無
    version_no = forms.CharField(max_length=20, label=_("Version No"), required=True,)  # ZZVERSION
    version_seq = forms.CharField(max_length=20, label=_("Version Sequence"), required=True, )  # ZZVERSION_SEQ
    lot_no = forms.CharField(max_length=20, label=_("Lot Number"), required=False, )  # LOTNO
    item_type = forms.ModelChoiceField(queryset=ItemType.objects.all(), label=_("Receive Type"), required=False)
    packing_type = forms.ModelChoiceField(queryset=PackMethod.objects.all(), label=_("Packing Type"), required=False)
    purchase_no = forms.CharField(max_length=20, label=_("Purchase Order"), required=True, )  # EBELN 採購單號
    purchase_qty = forms.CharField(max_length=20, label=_("Purchase Quantity"), required=False, )  # MENGE_PO 採購數量
    size = forms.CharField(max_length=20, label=_("Size"), required=True, )  # ZSIZE 尺寸
    purchase_unit = forms.ModelChoiceField(queryset=UnitType.objects.all(), label=_("Unit"), required=False)
    post_date = forms.DateField(label=_("Post Date"), required=False)  # BUDAT收貨日期
    order_qty = forms.CharField(max_length=20, label=_("Quantity"), required=False, initial=0)  # MENGE
    order_bin = forms.ModelChoiceField(queryset=Bin.objects.all(), label=_("Location"))
    gift_qty = forms.CharField(max_length=20, label="Complimentary Quantity", required=False, initial=0)
    gift_bin = forms.CharField(max_length=20, label=_("Complimentary Location"), required=False, )
    supplier = forms.CharField(max_length=10, label=_("Supplier"), required=False)  # NAME1
    sap_mtr_no = forms.CharField(max_length=20, label=_("SAP Material Number"), required=False, )  # MBLNR
    desc = forms.CharField(max_length=2000, label=_("Comment"), required=False, widget=forms.Textarea(attrs={'rows': 2, 'cols': 15}))

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
                Div('lot_no', css_class='col-md-3'),
                Div('size', css_class='col-md-3'),
                Div('purchase_qty', css_class='col-md-3'),
                Div('purchase_unit', css_class='col-md-3'),
                Div('order_qty', css_class='col-md-3'),
                Div('order_bin', css_class='col-md-3'),
                Div('desc', css_class='col-md-10'),
                Div(HTML(
                    '<a href="#" class="btn btn-info" id="create""><i class="fas fa-plus-circle"></i> '+_('Add')+'</a>'),
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
    product_order = forms.CharField(max_length=20, label=_("Product Order"), required=False, )  # VBELN 訂單單號
    customer_no = forms.CharField(max_length=20, label=_("Customer"), required=False,)  # 無
    version_no = forms.CharField(max_length=20, label=_("Version No"), required=False,)  # ZZVERSION
    version_seq = forms.CharField(max_length=20, label=_("Version Sequence"), required=False, )  # ZZVERSION_SEQ
    lot_no = forms.CharField(max_length=20, label=_("Lot Number"), required=False, )  # LOTNO
    item_type = forms.CharField(max_length=20, label=_("Receive Type"), required=False, )  # WGBEZ 物料群組說明
    packing_type = forms.CharField(max_length=20, label=_("Packing Type"), required=False, )  # 包裝方式
    purchase_no = forms.CharField(max_length=20, label=_("Purchase Order"), required=False, )  # EBELN 採購單號
    purchase_qty = forms.CharField(max_length=20, label=_("Purchase Quantity"), required=False, )  # MENGE_PO 採購數量
    size = forms.CharField(max_length=20, label=_("Size"), required=False, )  # ZSIZE 尺寸
    purchase_unit = forms.CharField(max_length=20, label=_("Unit"), required=False, )  # MEINS 數量單位
    post_date = forms.DateField(label=_("Post Date"))  # BUDAT收貨日期
    order_qty = forms.CharField(max_length=20, label=_("Quantity"), required=False, initial=0)  # MENGE
    order_bin = forms.CharField(max_length=20, label=_("Location"), required=False, )
    gift_qty = forms.CharField(max_length=20, label=_("Complimentary Quantity"), required=False, initial=0)
    gift_bin = forms.CharField(max_length=20, label=_("Complimentary Location"), required=False, )
    supplier = forms.CharField(max_length=10, label=_("Supplier"), required=False)  # NAME1
    sap_mtr_no = forms.CharField(max_length=20, label=_("SAP Material Number"), required=False, )  # MBLNR
    desc = forms.CharField(max_length=2000, label=_("Comment"), required=False, widget=forms.Textarea(attrs={'rows': 2, 'cols': 15}))
    comment = forms.CharField(max_length=200, label=_("Comment"), required=False, )

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
                Div(Button('bin_search', _('Search'), css_class='btn btn-light', onclick="stock_item_popup();"),
                    css_class='col-md-1 d-flex align-items-center pt-3'),
                Div('comment', css_class='col-md-10'),
                Div(HTML(
                    '<a href="#" class="btn btn-info" onclick="add_item();"><i class="fas fa-plus-circle"></i> '+_('Add')+'</a>'),
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
    product_order = forms.CharField(max_length=20, label=_("Product Order"), required=False, )  # VBELN 收貨單號
    purchase_no = forms.CharField(max_length=20, label=_("Purchase Order"), required=False, )  # EBELN 採購單號

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


class ExcelUploadForm(forms.Form):
    file = forms.FileField(
        label="Choose file Excel",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False


class BinValueSearchForm(forms.Form):
    warehouse = forms.ChoiceField(
        choices=[], required=False, widget=forms.Select(attrs={"class": "form-control"})
    )
    area = forms.ChoiceField(
        choices=[], required=False, widget=forms.Select(attrs={"class": "form-control", "disabled": "disabled"})
    )
    bin = forms.ChoiceField(
        choices=[], required=False, widget=forms.Select(attrs={"class": "form-control", "disabled": "disabled"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["warehouse"].choices = [("", "Choose Warehouse")] + list(Warehouse.objects.values_list("wh_code",
                                                                                                           "wh_name"))
        self.fields["area"].choices = [("", "Choose Area")]
        self.fields["bin"].choices = [("", "Choose Location")]


