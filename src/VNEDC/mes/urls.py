from django.urls import re_path as url
from .views import work_order_list, index

urlpatterns = [
    url('work_orders/', work_order_list, name='work_order_list'),
    url('', index, name='index'),
]
