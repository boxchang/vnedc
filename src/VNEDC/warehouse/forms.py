from datetime import timedelta, date

from django import forms
import PIL
from PIL import Image

from warehouse.models import Warehouse, Area, Bin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML
from django.utils.translation import gettext_lazy as _


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



