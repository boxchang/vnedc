# Generated by Django 3.2.25 on 2024-08-06 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0031_parameterdefine_data_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterdefine',
            name='input_time',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
