from django.urls import re_path as url
from .views import work_order_list, index, runcard_detail, ipqc_log

urlpatterns = [
    url(r'^work_orders/', work_order_list, name='work_order_list'),
    url(r'^detail/', runcard_detail, name='runcard_detail'),
    url(r'^ipqc_log/', ipqc_log, name='runcard_ipqc_log'),
    url('', index, name='index'),
]
