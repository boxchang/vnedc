from django.urls import re_path as url

from chart.views import param_value, param_value_api, get_param_define_api, param_value_product_api, \
    param_value_product, get_param_code_api

urlpatterns = [
    url(r'^param_value/$', param_value, name='param_value'),
    url(r'^param_value_api/$', param_value_api, name='param_value_api'),
    url(r'^get_param_define_api/$', get_param_define_api, name='get_param_define_api'),
    url(r'^get_param_code_api/$', get_param_code_api, name='get_param_code_api'),
    url(r'^param_value_product/$', param_value_product, name='param_value_product'),
    url(r'^param_value_product_api/$', param_value_product_api, name='param_value_product_api'),
]