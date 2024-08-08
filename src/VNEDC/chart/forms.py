from django import forms
from collection.models import Plant, Machine, Daily_Prod_Info, Process_Type, ParameterDefine, Parameter_Type
from django.utils.translation import gettext_lazy as _
from bootstrap_datepicker_plus.widgets import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Button
from datetime import datetime, date, timedelta


class SearchForm(forms.Form):
    day7_ago = date.today() - timedelta(days=7)
    today = date.today()
    data_date_start = forms.DateField(label=_("Start Date"), widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    data_date_end = forms.DateField(label=_("End Date"), widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    plant = forms.ModelChoiceField(required=True, label=_('plant'), queryset=Plant.objects.all())
    mach = forms.ModelChoiceField(required=True, label=_('mach_name'), queryset=Machine.objects.all())
    process_type = forms.ModelChoiceField(required=True, label=_('process_type'), queryset=Process_Type.objects.all().order_by('show_order'))
    param_define = forms.ModelChoiceField(required=True, label=_('param_define'), queryset=ParameterDefine.objects.none())
    control_high = forms.CharField(required=False, label=_('control_high'))
    control_low = forms.CharField(required=False, label=_('control_low'))

    def __init__(self, *args, submit_title='Submit', **kwargs):
        super().__init__(*args, **kwargs)
        day7_ago = date.today() - timedelta(days=7)
        today = date.today()
        self.fields['data_date_start'].initial = day7_ago
        self.fields['data_date_end'].initial = today
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True

        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        Div('data_date_start', css_class='col'),
                        css_class='row'
                    ),
                    Div(
                        Div('plant', css_class='col'),
                        css_class = 'row'),
                    css_class='col-md-2'
                ),
                Div(
                    Div(
                        Div('data_date_end', css_class='col'),
                        css_class='row'
                    ),
                    Div(
                        Div('mach', css_class='col'),
                        css_class='row'),
                    css_class='col-md-2'
                ),
                Div(
                    Div(
                        Div('control_high', css_class='col'),
                        css_class='row'
                    ),
                    Div(
                        Div('process_type', css_class='col'),
                        css_class='row'),
                    css_class='col-md-2'
                ),
                Div(
                    Div(
                        Div('control_low', css_class='col'),
                        css_class='row'
                    ),
                    Div(
                        Div('param_define', css_class='col'),
                        css_class='row'),
                    css_class='col-md-2'
                ),
                Div(
                    Div(
                        Div(Button('submit', _('Submit'), css_class='btn btn-info btn-search'), css_class='col'),
                        css_class='row'),
                    css_class='col-md-2'
                ),
                css_class='row'),
        )

class ProductionSearchForm(forms.Form):
    data_date_start = forms.DateField(label=_("Start Date"), widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    data_date_end = forms.DateField(label=_("End Date"), widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    product = forms.ChoiceField(required=True, label=_('Product'), widget=forms.Select(attrs={'class': 'select2'}))
    process_type = forms.ModelChoiceField(required=True, label=_('process_type'), queryset=Process_Type.objects.all().order_by('show_order'))
    param_code = forms.ModelChoiceField(required=True, label=_('param_code'), queryset=Parameter_Type.objects.none())

    def __init__(self, *args, submit_title='Submit', **kwargs):
        day7_ago = date.today() - timedelta(days=7)
        today = date.today()
        super().__init__(*args, **kwargs)
        self.fields['data_date_start'].initial = day7_ago
        self.fields['data_date_end'].initial = today

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True

        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        Div('product', css_class='col'),
                        css_class='row'),
                    Div(
                        Div('data_date_start', css_class='col'),
                        css_class='row'
                    ),
                    css_class='col-md-3'
                ),
                Div(
                    Div(
                        Div('process_type', css_class='col'),
                        css_class='row'),
                    Div(
                        Div('data_date_end', css_class='col'),
                        css_class='row'
                    ),
                    css_class='col-md-3'
                ),
                Div(
                    Div(
                        Div('param_code', css_class='col'),
                        css_class='row'),
                    css_class='col-md-3'
                ),
                Div(
                    Div(
                        Div(Button('submit', _('Submit'), css_class='btn btn-info btn-search'), css_class='col'),
                        css_class='row'),
                    css_class='col-md-3'
                ),
                css_class='row'),
        )