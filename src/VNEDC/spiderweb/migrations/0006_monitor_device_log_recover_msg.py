# Generated by Django 3.2.25 on 2024-10-22 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spiderweb', '0005_auto_20241018_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitor_device_log',
            name='recover_msg',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]