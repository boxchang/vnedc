from django.urls import re_path as url

from collection.views import record, daily_info_create, prod_info_save, prod_info_reset, index, raw_data_api, \
    get_mach_api

urlpatterns = [
    url(r'^index/$', index, name='collection_index'),
    url(r'^record/(?P<process_code>\w+)/$', record, name='record'),
    url(r'^prod_info_save/$', prod_info_save, name='prod_info_save'),
    url(r'^prod_info_reset/$', prod_info_reset, name='prod_info_reset'),
    url(r'^daily_info_create/$', daily_info_create, name='daily_info_create'),
    url(r'^raw_data_api/(?P<data_date_start>\w+)/(?P<data_date_end>\w+)/(?P<process_type>\w+)/$', raw_data_api, name='raw_data_api'),
    url(r'^get_mach_api/', get_mach_api, name='get_mach_api'),
]