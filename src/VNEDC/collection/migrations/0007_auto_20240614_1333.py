# Generated by Django 3.2.25 on 2024-06-14 13:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0006_auto_20240614_1321'),
    ]

    operations = [
        migrations.RenameField(
            model_name='daily_prod_info',
            old_name='production_name_a1',
            new_name='prod_name_a1',
        ),
        migrations.RenameField(
            model_name='daily_prod_info',
            old_name='production_name_a2',
            new_name='prod_name_a2',
        ),
        migrations.RenameField(
            model_name='daily_prod_info',
            old_name='production_name_b1',
            new_name='prod_name_b1',
        ),
        migrations.RenameField(
            model_name='daily_prod_info',
            old_name='production_name_b2',
            new_name='prod_name_b2',
        ),
        migrations.RenameField(
            model_name='daily_prod_info',
            old_name='production_size_a1',
            new_name='prod_size_a1',
        ),
        migrations.RenameField(
            model_name='daily_prod_info',
            old_name='production_size_a2',
            new_name='prod_size_a2',
        ),
        migrations.RenameField(
            model_name='daily_prod_info',
            old_name='production_size_b1',
            new_name='prod_size_b1',
        ),
        migrations.RenameField(
            model_name='daily_prod_info',
            old_name='production_size_b2',
            new_name='prod_size_b2',
        ),
    ]
