# Generated by Django 3.2.25 on 2024-12-06 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spiderweb', '0006_monitor_device_log_recover_msg'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitor_status',
            name='ref_url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
