from django.urls import re_path as url

from chart.views import param_value, param_value_api, get_param_define_api, param_value_product_api, \
    param_value_product, get_param_code_api, get_machines_by_plant, param_value_rate_api, param_value_rate, heat_value, \
    get_heat_data, get_flow_data, get_box_heat_rate

urlpatterns = [
    url(r'^param_value/$', param_value, name='param_value'),
    url(r'^param_value_rate/$', param_value_rate, name='param_value_rate'),
    url(r'^param_value_api/$', param_value_api, name='param_value_api'),
    url(r'^get_param_define_api/$', get_param_define_api, name='get_param_define_api'),
    url(r'^get_param_code_api/$', get_param_code_api, name='get_param_code_api'),
    url(r'^param_value_product/$', param_value_product, name='param_value_product'),
    url(r'^param_value_product_api/$', param_value_product_api, name='param_value_product_api'),
    url(r'^param_value_rate_api/$', param_value_rate_api, name='param_value_rate_api'),
    url(r'^get_machines_by_plant/$', get_machines_by_plant, name='get_machines_by_plant'),
    url(r'^heat_value/$', heat_value, name='heat_value'),
    url(r'^get_heat_data/$', get_heat_data, name='get_heat_data'),
    url(r'^get_flow_data/$', get_flow_data, name='get_flow_data'),
    url(r'^get_box_heat_rate/$', get_box_heat_rate, name='get_box_heat_rate'),
]