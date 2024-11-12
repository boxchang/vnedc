from django.urls import re_path as url
from spiderweb.views import spiderweb
from mes.views import work_order_list, index, runcard_detail, ipqc_log, fast_check, runcard_info, \
    runcard_api, thickness_data_api, fast_check2, machine_master_data_format, process_type_master_data_format, \
    parameter_define_master_data_format, excel_api, monthly_check

urlpatterns = [
    url(r'^work_orders/', work_order_list, name='work_order_list'),
    url(r'^detail/', runcard_detail, name='runcard_detail'),
    url(r'^ipqc_log/', ipqc_log, name='runcard_ipqc_log'),
    url(r'^runcard_info/', runcard_info, name='runcard_info'),
    url(r'^fast_check/', fast_check, name='fast_check'),
    url(r'^fast_check2/', fast_check2, name='fast_check2'),
    url(r'^machine_master_data_format/', machine_master_data_format, name='machine_master_data_format'),
    url(r'^process_type_master_data_format/', process_type_master_data_format, name='process_type_master_data_format'),
    url(r'^parameter_define_master_data_format/', parameter_define_master_data_format, name='parameter_define_master_data_format'),
    url(r'^excel_api/', excel_api, name='excel_api'),
    url(r'^runcard_api/(?P<runcard>[\w-]+)/$', runcard_api, name='runcard_api'),
    url(r'^thickness_data_api/', thickness_data_api, name='thickness_data_api'),
    url(r'^spiderweb/', spiderweb, name='spiderweb'),
    url(r'^monthly_check/', monthly_check, name='monthly_check'),
    # url('', index, name='index'),
]