# Generated by Django 3.2.25 on 2024-12-19 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0002_bin_value_history_act_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bin_value_history',
            name='qty',
        ),
        migrations.AddField(
            model_name='bin_value_history',
            name='action_qty',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bin_value_history',
            name='new_qty',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bin_value_history',
            name='old_qty',
            field=models.IntegerField(default=0),
        ),
    ]
