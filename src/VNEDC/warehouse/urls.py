from django.urls import path
from django.urls import re_path as url

from warehouse.views import index, packing_material_stock_in, packing_material_stock_out, stockin_detail, \
    get_product_order_info, \
    packing_material_stock_in_post, packing_material_stock_out_post, dashboard, get_purchase_no_info, work_order_search, \
    work_order_page, bin_transfer, \
    bin_transfer_page, get_product_order_stout, work_order_bin_search, work_order_hist_data, get_purchase_no_stout, \
    bin_adjust_page, bin_adjust, upload_excel, bin_value_import, search_bin_value, warehouse_map
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
    url(r'^bin/check_po_exists/$', views.check_po_exists, name='check_po_exists'),
    url(r'^bin/create/(?P<area_code>[^/]+)$', views.create_bin, name='bin_create'),
    url(r'^bin/edit/(?P<bin_code>[^/]+)/$', views.edit_bin, name='edit_bin'),
    url(r'^bin/list/$', views.bin_list, name='bin_list'),
    url(r'^bin/bin_by_area/(?P<area_code>[^/]+)$', views.bin_by_area, name='bin_by_area'),
    url(r'^bin/delete/(?P<pk>[^/]+)/$', views.bin_delete, name='bin-delete'),
    url(r'^bin/bin_value_import/$', bin_value_import, name="bin_value_import"),

    url(r'^bin/search/$', views.bin_search, name='bin_search'),
    url(r'^get-areas/$', views.get_areas, name='get_areas'),
    url(r'^get-bins/$', views.get_bins, name='get_bins'),
    url(r'^get-bin-data/$', views.get_bin_data, name='get_bin_data'),
    url(r'^search-bin-value/$', search_bin_value, name="search_bin_value"),
    url(r'^$', views.warehouse_list, name='warehouse_list'),

    url(r'^packing_material_stock_in/', packing_material_stock_in, name='packing_material_stock_in'),
    url(r'^packing_material_stock_out/', packing_material_stock_out, name='packing_material_stock_out'),
    url(r'^stockin_detail/(?P<pk>\w+)/$', stockin_detail, name='stockin_detail'),
    url(r'^get_product_order_info/', get_product_order_info, name='get_product_order_info'),
    url(r'^get_product_order_stout/', get_product_order_stout, name='get_product_order_stout'),
    url(r'^get_purchase_no_stout/', get_purchase_no_stout, name='get_purchase_no_stout'),
    url(r'^get_purchase_no_info/', get_purchase_no_info, name='get_purchase_no_info'),
    url(r'^packing_material_stock_in_post/', packing_material_stock_in_post, name='packing_material_stock_in_post'),
    url(r'^packing_material_stock_out_post/', packing_material_stock_out_post, name='packing_material_stock_out_post'),
    url(r'^dashboard/', dashboard, name='warehouse_dashboard'),
    url(r'^upload/$', upload_excel, name="upload_excel"),

    url(r'^work_order_search/$', work_order_search, name='work_order_search'),
    url(r'^work_order_hist_data/$', work_order_hist_data, name='work_order_hist_data'),
    url(r'^work_order_bin_search/$', work_order_bin_search, name='work_order_bin_search'),
    url(r'^work_order_page/$', work_order_page, name='work_order_page'),
    url(r'^bin_transfer_page/$', bin_transfer_page, name='bin_transfer_page'),
    url(r'^bin/transfer/$', bin_transfer, name='bin_transfer'),
    url(r'^bin_adjust_page/$', bin_adjust_page, name='bin_adjust_page'),
    url(r'^bin/adjust/$', bin_adjust, name='bin_adjust'),
    url(r'^map/(?P<pk>\w+)/$', warehouse_map, name='warehouse_map'),
    url(r'^$', views.index, name='warehouse_index'),
]




