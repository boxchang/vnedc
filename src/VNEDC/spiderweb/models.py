from django.db import models
from django.utils import timezone
from django.conf import settings


class Monitor_Status(models.Model):
    status_name = models.CharField(max_length=100, unique=True)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='monitor_status_update_by')

    def __str__(self):
        return self.status_name


class Monitor_Type(models.Model):
    type_name = models.CharField(max_length=100, unique=True)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='monitor_type_update_by')

    def __str__(self):
        return self.type_name


class Device_Type(models.Model):
    type_name = models.CharField(max_length=100, unique=True)
    job_frequency = models.CharField(max_length=10, null=False, blank=False)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='device_type_update_by')

    def __str__(self):
        return self.type_name


class Monitor_Device_List(models.Model):
    monitor_type = models.ForeignKey(Monitor_Type, related_name='monitor_list_monitor_type', on_delete=models.CASCADE, null=False,
                              blank=False)
    device_type = models.ForeignKey(Device_Type, related_name='monitor_list_device_type', on_delete=models.CASCADE, null=False,
                              blank=False)
    device_group = models.CharField(max_length=100, null=True, blank=True)
    device_name = models.CharField(max_length=100, null=False, blank=False)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    port = models.CharField(max_length=100, null=True, blank=True)
    plant = models.CharField(max_length=50, null=True, blank=True)
    enable = models.CharField(max_length=1, null=False, blank=False, default='Y')
    status = models.ForeignKey(Monitor_Status, related_name='monitor_list_status', on_delete=models.DO_NOTHING, null=True,
                              blank=True)
    status_update_at = models.DateTimeField(default=timezone.now)
    comment = models.CharField(max_length=500, null=True, blank=True)
    job_start_time = models.CharField(max_length=20, null=True, blank=True)
    job_frequency = models.CharField(max_length=10, null=False, blank=False)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='monitor_list_update_by')

    def __str__(self):
        return self.device_name
