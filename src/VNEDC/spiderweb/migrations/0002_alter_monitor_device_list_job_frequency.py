# Generated by Django 3.2.25 on 2024-10-08 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spiderweb', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitor_device_list',
            name='job_frequency',
            field=models.CharField(default=5, max_length=10),
            preserve_default=False,
        ),
    ]
