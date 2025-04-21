from datetime import datetime
from bootstrap_datepicker_plus.widgets import DatePickerInput
from crispy_forms.helper import FormHelper
from django import forms
from django.core.validators import RegexValidator


class DateRangeForm(forms.Form):
    # Trường tháng (người dùng chọn tháng và năm)
    month = forms.CharField(
        widget=forms.DateInput(attrs={'type': 'month'}),
        label='Select Month',
        validators=[RegexValidator(r'^\d{4}-\d{2}$', 'Enter a valid month in YYYY-MM format')]
    )


class DailyReportCmt(forms.Form):
    date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=DatePickerInput(
            attrs={'value': (datetime.now()).strftime('%Y-%m-%d')},
            options={
                "format": "YYYY-MM-DD",
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
            }
        ),
        label="Date"
    )
    comment = forms.CharField(
        label="Comment",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
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



