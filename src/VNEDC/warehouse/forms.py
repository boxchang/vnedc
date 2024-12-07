from django import forms
import PIL
from PIL import Image

from warehouse.models import Warehouse, Area, Bin


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse  # Chỉ định model mà form này sẽ sử dụng
        fields = ['wh_code', 'wh_name', 'wh_comment', 'wh_bg']
        # widgets = {
        #     'wh_code': forms.TextInput(attrs={'disabled': 'disabled'}),
        # }

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
        #exclude = ['area']  # Loại bỏ trường area khỏi form
        fields = ['bin_id', 'bin_name', 'area', 'pos_x', 'pos_y', 'bin_w', 'bin_l']

    # widgets = {
    #     'area_id': forms.TextInput(attrs={'class': 'form-control'}),
    #     'area_name': forms.TextInput(attrs={'class': 'form-control'}),
    #     'wh_code': forms.Select(attrs={'class': 'form-select'}),
    # }
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
