from django.urls import path
from . import views

urlpatterns = [
    path('', views.file_list, name='file_list'),
    path('download/<str:key>/<path:subpath>/', views.download_file, name='download_file'),
    path('<path:subpath>/', views.file_list, name='file_list_subpath'),
]
