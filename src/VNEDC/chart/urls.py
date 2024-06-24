from django.urls import re_path as url

from chart.views import param_value, param_value_api, get_param_define_api

urlpatterns = [
    url(r'^param_value/$', param_value, name='param_value'),
    url(r'^param_value_api/$', param_value_api, name='param_value_api'),
    url(r'^get_param_define_api/$', get_param_define_api, name='get_param_define_api'),
]