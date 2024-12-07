from django.urls import path
from django.urls import re_path as url

from warehouse.views import index
from . import views


urlpatterns = [

    url(r'^warehouse/delete/(?P<pk>\w+)/$', views.warehouse_delete, name='warehouse-delete'),
    url(r'^warehouse/edit/(?P<warehouse_code>\w+)/$', views.edit_warehouse, name='edit_warehouse'),
    url(r'^warehouse/list/$', views.warehouse_list, name='warehouse_list'),
    url(r'^warehouse/create/$', views.create_warehouse, name='warehouse_create'),
    url(r'^warehouse/test/$', views.test, name='test'),

    url(r'^area/delete/(?P<pk>\w+)/$', views.area_delete, name='area-delete'),
    url(r'^area/edit/(?P<area_code>\w+)/$', views.edit_area, name='edit_area'),
    url(r'^area/list/$', views.area_list, name='area_list'),
    url(r'^area/create/(?P<wh_code>\w+)/$', views.create_area, name='area_create'),
    url(r'^area/area_by_warehouse/(?P<wh_code>\w+)/$', views.area_by_warehouse, name='area_by_warehouse'),

    url(r'^bin/create/(?P<area_code>\w+)$', views.create_bin, name='bin_create'),
    url(r'^bin/delete/(?P<pk>\w+)/$', views.bin_delete, name='bin-delete'),
    url(r'^bin/edit/(?P<bin_code>\w+)/$', views.edit_bin, name='edit_bin'),
    url(r'^bin/list/$', views.bin_list, name='bin_list'),
    url(r'^bin/bin_by_area/(?P<area_code>\w+)$', views.bin_by_area, name='bin_by_area'),
    url(r'^$', index, name='warehouse_index'),
]




