# Generated by Django 3.2.25 on 2025-01-03 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0015_bin_value_history_batch_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='bin_value_history',
            name='comment',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
