# VNEDC/settings/production.py

from .base import *

PROD = True

SECRET_KEY = '8i7h&)&2z!$!e710^%m)i4f(7_lpn)8ofu8&)djhix$q^66k0s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'VNEDC',
        'USER': 'vnedc',
        'PASSWORD': 'vnedc#2024',
        'HOST': '10.13.104.181',
        'PORT': '1433',

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
}
