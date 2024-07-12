from datetime import datetime
from bootstrap_datepicker_plus.widgets import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from collection.models import Plant, Machine, Daily_Prod_Info
from django.utils.translation import gettext_lazy as _


class RecordForm(forms.Form):
    data_date = forms.DateField(label=_('record_date'))
    plant = forms.ModelChoiceField(required=True, label=_('plant'), queryset=Plant.objects.all())
    mach = forms.ModelChoiceField(required=True, label=_('mach_name'), queryset=Machine.objects.none())


    def __init__(self, *args, submit_title='Submit', **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True

        self.helper.layout = Layout(
            Div(
                Div('plant', css_class='col-md-3'),
                Div('mach', css_class='col-md-3'),
                Div('data_date', css_class='col-md-3'),
                css_class='row'),
        )


        self.fields['data_date'].widget = DatePickerInput(
            attrs={'value': datetime.now().strftime('%Y-%m-%d')},
            options={
                "format": "YYYY-MM-DD",
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
            }
        )


class DailyInfoForm(forms.ModelForm):
    CHOICES = [('無氯', '無氯'), ('無二次料', '無二次料'), ('碱槽測PH值', '碱槽測PH值'),]
    hour = [(str(hh).zfill(2), str(hh).zfill(2)) for hh in range(0, 24)]
    min = [(str(mm).zfill(2), str(mm).zfill(2)) for mm in range(0, 60)]
    prod_name_a1 = forms.CharField(required=False, label='A1品項')
    prod_size_a1 = forms.CharField(required=False, label='A1尺寸')
    prod_name_a2 = forms.CharField(required=False, label='A2品項')
    prod_size_a2 = forms.CharField(required=False, label='A2尺寸')
    prod_name_b1 = forms.CharField(required=False, label='B1品項')
    prod_size_b1 = forms.CharField(required=False, label='B1尺寸')
    prod_name_b2 = forms.CharField(required=False, label='B2品項')
    prod_size_b2 = forms.CharField(required=False, label='B2尺寸')
    remark = forms.MultipleChoiceField(label="備註", widget=forms.CheckboxSelectMultiple, choices=CHOICES,)
    coagulant_time_hour = forms.ChoiceField(required=False, label='換凝固劑時間(Hour)', choices=hour)
    coagulant_time_min = forms.ChoiceField(required=False, label='換凝固劑時間(Minute)', choices=min)
    latex_time_hour = forms.ChoiceField(required=False, label='換乳膠時間(Hour)', choices=hour)
    latex_time_min = forms.ChoiceField(required=False, label='換乳膠時間(Minute)', choices=min)
    tooling_time_hour = forms.ChoiceField(required=False, label='換模時間(Hour)', choices=hour)
    tooling_time_min = forms.ChoiceField(required=False, label='換模時間(Minute)', choices=min)
    plant = forms.ModelChoiceField(required=False, label='廠別', queryset=Plant.objects.all())

    class Meta:
        model = Daily_Prod_Info
        fields = ('prod_name_a1', 'prod_size_a1',
                  'prod_name_a2', 'prod_size_a2', 'prod_name_b1', 'prod_size_b1',
                  'prod_name_b2', 'prod_size_b2', 'remark', 'coagulant_time_hour', 'coagulant_time_min',
                  'latex_time_hour', 'latex_time_min', 'tooling_time_hour', 'tooling_time_min')


    def __init__(self, *args, submit_title='Submit', **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True

        self.helper.layout = Layout(
            Div(
                Div('prod_name_a1', css_class='col-md-3'),
                Div('prod_name_a2', css_class='col-md-3'),
                Div('prod_name_b1', css_class='col-md-3'),
                Div('prod_name_b2', css_class='col-md-3'),
                css_class='row'),
            Div(
                Div('prod_size_a1', css_class='col-md-3'),
                Div('prod_size_a2', css_class='col-md-3'),
                Div('prod_size_b1', css_class='col-md-3'),
                Div('prod_size_b2', css_class='col-md-3'),
                css_class='row'),
            Div(
                Div(
                    Div('remark', css_class='col daily_info_remark')
                , css_class='col-md-6'),
                Div(
                    Div(
                        Div('coagulant_time_hour', css_class='col'),
                        Div('coagulant_time_min', css_class='col'),
                        css_class='row'),
                    Div(
                        Div('latex_time_hour', css_class='col'),
                        Div('latex_time_min', css_class='col'),
                        css_class='row'),
                    Div(
                        Div('tooling_time_hour', css_class='col'),
                        Div('tooling_time_min', css_class='col'),
                        css_class='row')
                , css_class='col-md-6'),
                css_class='row'),
        )

