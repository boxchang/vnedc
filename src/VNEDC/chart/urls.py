from django.urls import re_path as url

from chart.views import test

urlpatterns = [
    url(r'^test/$', test, name='test'),
]