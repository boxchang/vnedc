from django.apps import AppConfig
from filelist.templatetags import filelist_tags


class FilelistConfig(AppConfig):
    name = 'filelist'

    def ready(self):
        filelist_tags
