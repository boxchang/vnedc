# Generated by Django 3.2.25 on 2024-11-13 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0040_alter_parameter_type_control_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='daily_prod_info',
            name='handmold_brand',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='daily_prod_info',
            name='handmold_spec',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
