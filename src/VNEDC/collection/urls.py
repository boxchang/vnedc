from django.urls import re_path as url

from collection.views import record, daily_info_create, prod_info_save, prod_info_reset, index

urlpatterns = [
    url(r'^index/$', index, name='collection_index'),
    url(r'^record/(?P<process_code>\w+)/$', record, name='record'),
    url(r'^prod_info_save/$', prod_info_save, name='prod_info_save'),
    url(r'^prod_info_reset/$', prod_info_reset, name='prod_info_reset'),
    url(r'^daily_info_create/$', daily_info_create, name='daily_info_create'),
]