# Generated by Django 3.2.25 on 2024-10-18 08:35

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('spiderweb', '0004_auto_20241017_1017'),
    ]

    operations = [
        migrations.CreateModel(
            name='Monitor_Device_Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('func_name', models.CharField(max_length=50)),
                ('comment', models.CharField(max_length=200)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('notice_flag', models.BooleanField(blank=True, null=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_device', to='spiderweb.monitor_device_list')),
                ('status_code', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='check_log_status', to='spiderweb.monitor_status')),
            ],
        ),
        migrations.DeleteModel(
            name='Check_Log',
        ),
    ]