from django.urls import re_path as url
from . import views
from spiderweb.views import spiderweb, abnormal_recover, spiderweb_config
from mes.views import work_order_list, index, runcard_detail, ipqc_log, fast_check, runcard_info, \
    runcard_api, thickness_data_api, fast_check2, machine_master_data_format, process_type_master_data_format, \
    parameter_define_master_data_format, excel_api, monthly_check, account_check, insert_parameter, test

urlpatterns = [
    url(r'^config/layout', views.config_layout, name='config_layout'),
    url(r'^config', views.spiderweb_config, name='spiderweb_config'),
    url(r'^toggle_device_status/', views.toggle_device_status, name='toggle_device_status'),
    url(r'^abnormal_recover/(?P<pk>\d+)', abnormal_recover, name='abnormal_recover'),

]