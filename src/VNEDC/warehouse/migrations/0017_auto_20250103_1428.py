# Generated by Django 3.2.25 on 2025-01-03 14:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0016_bin_value_history_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bin_value_history',
            name='act_type',
        ),
        migrations.AddField(
            model_name='bin_value_history',
            name='mvt',
            field=models.ForeignKey(default='PACKING_INNERBOX', on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockin_hist_mvt', to='warehouse.movementtype'),
            preserve_default=False,
        ),
    ]