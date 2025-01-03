from django.urls import path
from django.urls import re_path as url

from warehouse.views import index, stock_in, stockin_detail, get_product_order_info, \
    stock_in_post
from . import views


urlpatterns = [
    url(r'^test/$', views.test, name='test'),
    url(r'^show_warehouse/(?P<pk>\w+)/$', views.show_warehouse, name='show_warehouse'),
    url(r'^edit/(?P<warehouse_code>\w+)/$', views.edit_warehouse, name='edit_warehouse'),
    url(r'^create/$', views.create_warehouse, name='warehouse_create'),
    url(r'^delete/(?P<pk>\w+)/$', views.warehouse_delete, name='warehouse-delete'),

    url(r'^area/edit/(?P<area_code>[^/]+)/$', views.edit_area, name='edit_area'),
    url(r'^area/create/(?P<wh_code>[^/]+)/$', views.create_area, name='area_create'),
    url(r'^area/area_by_warehouse/(?P<wh_code>\w+)/$', views.area_by_warehouse, name='area_by_warehouse'),
    url(r'^area/delete/(?P<pk>[^/]+)/$', views.area_delete, name='area-delete'),
    url(r'^area/list/$', views.area_list, name='area_list'),


    url(r'^bin/bin_action/$', views.bin_action, name='bin_action'),
    url(r'^bin/search/$', views.bin_search, name='bin_search'),
    url(r'^bin/check_po_exists/$', views.check_po_exists, name='check_po_exists'),
    url(r'^bin/create/(?P<area_code>[^/]+)$', views.create_bin, name='bin_create'),
    url(r'^bin/edit/(?P<bin_code>[^/]+)/$', views.edit_bin, name='edit_bin'),
    url(r'^bin/list/$', views.bin_list, name='bin_list'),
    url(r'^bin/bin_by_area/(?P<area_code>[^/]+)$', views.bin_by_area, name='bin_by_area'),
    url(r'^bin/delete/(?P<pk>[^/]+)/$', views.bin_delete, name='bin-delete'),
    url(r'^$', views.warehouse_list, name='warehouse_list'),
    url(r'^stock_in/', stock_in, name='stock_in'),
    url(r'^stockin_detail/(?P<pk>\w+)/$', stockin_detail, name='stockin_detail'),
    url(r'^get_product_order_info/', get_product_order_info, name='get_product_order_info'),
    url(r'^stock_in_post/', stock_in_post, name='stock_in_post'),
    url(r'^$', views.index, name='warehouse_index'),

]




