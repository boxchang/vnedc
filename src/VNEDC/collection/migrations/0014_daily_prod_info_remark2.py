# Generated by Django 3.2.25 on 2024-07-13 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0013_parameterdefine_auto_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='daily_prod_info',
            name='remark2',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
