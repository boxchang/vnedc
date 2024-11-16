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
    CHOICES = [(_('Chlorine Free'), _('Chlorine Free')), (_('Polymer Free'), _('Polymer Free')), (_('Alkaline Tank pH Test'), _('Alkaline Tank pH Test')), (_('Machine Shutdown'), _('Machine Shutdown')),]
    SIZE_OPTION = [('', '---'), ('XXS', 'XXS'), ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'),]
    HAND_SPECS = [('JH(中國)-細', 'JH(中國)-細'), ('JH(中國)-粗', 'JH(中國)-粗'), ('PT(印尼)-細', 'PT(印尼)-細'), ('SK(馬來西亞)-細', 'SK(馬來西亞)-細'), ('SK(馬來西亞)-粗', 'SK(馬來西亞)-粗'), ('MC(馬來西亞)-細', 'MC(馬來西亞)-細')]
    hour = [(str(hh).zfill(2), str(hh).zfill(2)) for hh in range(0, 24)]
    min = [(str(mm).zfill(2), str(mm).zfill(2)) for mm in range(0, 60)]
    prod_name_a1 = forms.ChoiceField(choices=[('', '---')], required=False, label=_('A1 Production'), widget=forms.Select(attrs={'class': 'select2'}))
    prod_size_a1 = forms.ChoiceField(required=False, label=_('A1 Size'), choices=SIZE_OPTION)
    prod_name_a2 = forms.ChoiceField(choices=[('', '---')], required=False, label=_('A2 Production'), widget=forms.Select(attrs={'class': 'select2'}))
    prod_size_a2 = forms.ChoiceField(required=False, label=_('A2 Size'), choices=SIZE_OPTION)
    prod_name_b1 = forms.ChoiceField(choices=[('', '---')], required=False, label=_('B1 Production'), widget=forms.Select(attrs={'class': 'select2'}))
    prod_size_b1 = forms.ChoiceField(required=False, label=_('B1 Size'), choices=SIZE_OPTION)
    prod_name_b2 = forms.ChoiceField(choices=[('', '---')], required=False, label=_('B2 Production'), widget=forms.Select(attrs={'class': 'select2'}))
    prod_size_b2 = forms.ChoiceField(required=False, label=_('B2 Size'), choices=SIZE_OPTION)
    remark = forms.MultipleChoiceField(required=False, label=_('Remark'), widget=forms.CheckboxSelectMultiple, choices=CHOICES,)
    remark2 = forms.CharField(required=False, label='', widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}), max_length=500)
    coagulant_time_hour = forms.ChoiceField(required=False, label=_('Change Coagulant Time(Hour)'), choices=hour)
    coagulant_time_min = forms.ChoiceField(required=False, label=_('Change Coagulant Time(Minute)'), choices=min)
    latex_time_hour = forms.ChoiceField(required=False, label=_('Change Latex Time(Hour)'), choices=hour)
    latex_time_min = forms.ChoiceField(required=False, label=_('Change Latex Time(Minute)'), choices=min)
    tooling_time_hour = forms.ChoiceField(required=False, label=_('Change Tooling Time(Hour)'), choices=hour)
    tooling_time_min = forms.ChoiceField(required=False, label=_('Change Tooling Time(Minute)'), choices=min)
    plant = forms.ModelChoiceField(required=False, label=_('Plant'), queryset=Plant.objects.all())
    handmold_brand = forms.ChoiceField(choices=[('', '-------'), ('china', '中國 China'), ('indo', '印尼 Indonesia')], required=False, label='手模規格')
    handmold_spec = forms.MultipleChoiceField(choices=HAND_SPECS, required=False, widget=forms.CheckboxSelectMultiple, label='手模規格')
    class Meta:
        model = Daily_Prod_Info
        fields = ('prod_name_a1', 'prod_size_a1',
                  'prod_name_a2', 'prod_size_a2', 'prod_name_b1', 'prod_size_b1',
                  'prod_name_b2', 'prod_size_b2', 'remark', 'coagulant_time_hour', 'coagulant_time_min',
                  'latex_time_hour', 'latex_time_min', 'tooling_time_hour', 'tooling_time_min', 'remark2', 'handmold_spec')


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
                css_class='row'
            ),
            Div(
                Div('prod_size_a1', css_class='col-md-3'),
                Div('prod_size_a2', css_class='col-md-3'),
                Div('prod_size_b1', css_class='col-md-3'),
                Div('prod_size_b2', css_class='col-md-3'),
                css_class='row'
            ),
            Div(
                Div(
                    Div(
                        Div('remark', css_class='col daily_info_remark'),
                        css_class='row'
                    ),
                    Div(
                        Div('remark2', css_class='col'),
                        css_class='row'
                    ),
                    css_class='col-md-6'
                ),
                Div(
                    Div(
                        Div('coagulant_time_hour', css_class='col'),
                        Div('coagulant_time_min', css_class='col'),
                        css_class='row'
                    ),
                    Div(
                        Div('latex_time_hour', css_class='col'),
                        Div('latex_time_min', css_class='col'),
                        css_class='row'
                    ),
                    Div(
                        Div('tooling_time_hour', css_class='col'),
                        Div('tooling_time_min', css_class='col'),
                        css_class='row'
                    ),
                    css_class='col-md-6'
                ),
                css_class='row'
            ),
            Div(
                Div(
                    'handmold_spec',
                    css_class='col-md-12 horizontal-checkboxes'
                ),
            )
        )


