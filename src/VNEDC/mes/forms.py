from django import forms
from django.core.validators import RegexValidator

class DateRangeForm(forms.Form):
    # Trường tháng (người dùng chọn tháng và năm)
    month = forms.CharField(
        widget=forms.DateInput(attrs={'type': 'month'}),
        label='Select Month',
        validators=[RegexValidator(r'^\d{4}-\d{2}$', 'Enter a valid month in YYYY-MM format')]
    )

# from ckeditor_uploader.widgets import CKEditorUploadingWidget
#
#
# class DateRangeForm(forms.Form):
#     # Optional CKEditor text input (if needed for notes or comments)
#     notes = forms.CharField(widget=CKEditorUploadingWidget(), required=False)
#
#     # Start and end date fields for the calendar
#     start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
#     end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))



