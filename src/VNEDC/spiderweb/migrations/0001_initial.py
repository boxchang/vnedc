# Generated by Django 3.2.25 on 2024-10-07 09:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Device_Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=100, unique=True)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='device_type_update_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Monitor_Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=100, unique=True)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='monitor_type_update_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Monitor_Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_name', models.CharField(max_length=100, unique=True)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='monitor_status_update_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Monitor_Device_List',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_name', models.CharField(max_length=100)),
                ('ip_address', models.CharField(blank=True, max_length=50, null=True)),
                ('port', models.CharField(blank=True, max_length=100, null=True)),
                ('plant', models.CharField(blank=True, max_length=50, null=True)),
                ('enable', models.CharField(default='Y', max_length=1)),
                ('status_update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.CharField(blank=True, max_length=500, null=True)),
                ('job_start_time', models.CharField(blank=True, max_length=20, null=True)),
                ('job_frequency', models.CharField(blank=True, max_length=10, null=True)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('device_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monitor_list_device_type', to='spiderweb.device_type')),
                ('monitor_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monitor_list_monitor_type', to='spiderweb.monitor_type')),
                ('status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='monitor_list_status', to='spiderweb.monitor_status')),
                ('update_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='monitor_list_update_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
