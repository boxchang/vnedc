# VNEDC/settings/test-demo.py

from .test import *

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.mysql',
        # Or path to database file if using sqlite3.
        'NAME': 'pms_demo',   # DB name
        'USER': 'nico',                       # Not used with sqlite3.
        'PASSWORD': 'nicodb#123',               # Not used with sqlite3.
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': 'git-runner.it.srv.dc',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '3306',
    },
}