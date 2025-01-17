# Generated by Django 3.2.25 on 2025-01-03 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0011_packmethod_unittype'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bin_value',
            old_name='po_no',
            new_name='product_no',
        ),
        migrations.RenameField(
            model_name='bin_value_history',
            old_name='po_no',
            new_name='product_no',
        ),
        migrations.AddField(
            model_name='bin_value',
            name='purchase_no',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='bin_value',
            name='version_no',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='bin_value',
            name='version_seq',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='bin_value_history',
            name='purchase_no',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='bin_value_history',
            name='version_no',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='bin_value_history',
            name='version_seq',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]