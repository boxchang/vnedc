# Generated by Django 3.2.25 on 2024-08-08 10:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0034_auto_20240808_1023'),
    ]

    operations = [
        migrations.RenameField(
            model_name='parameter_type',
            old_name='param_code',
            new_name='param_type_code',
        ),
        migrations.RemoveField(
            model_name='parameter_type',
            name='param_name',
        ),
    ]
