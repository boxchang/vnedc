from django.urls import re_path as url
from .views import work_order_list, index, runcard_detail, ipqc_log, fast_check, runcard_info, \
    runcard_api, thickness_data_api, fast_check2, agent_storage, machine_status

urlpatterns = [
    url(r'^work_orders/', work_order_list, name='work_order_list'),
    url(r'^detail/', runcard_detail, name='runcard_detail'),
    url(r'^ipqc_log/', ipqc_log, name='runcard_ipqc_log'),
    url(r'^runcard_info/', runcard_info, name='runcard_info'),
    url(r'^fast_check/', fast_check, name='fast_check'),
    url(r'^fast_check2/', fast_check2, name='fast_check2'),
    url(r'^check_disk/', agent_storage, name='check_disk'),
    url(r'^machine_status/', machine_status, name='machine_status'),
    url(r'^runcard_api/(?P<runcard>[\w-]+)/$', runcard_api, name='runcard_api'),
    url(r'^thickness_data_api/', thickness_data_api, name='thickness_data_api'),
    url('', index, name='index'),
]