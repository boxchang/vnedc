# Generated by Django 3.2.25 on 2024-10-17 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spiderweb', '0002_auto_20241014_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='check_log',
            name='notice_flag',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]