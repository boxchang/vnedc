# Generated by Django 3.2.25 on 2024-12-19 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0003_auto_20241219_1021'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bin_value_history',
            old_name='action_qty',
            new_name='act_qty',
        ),
    ]