# Generated by Django 3.2.25 on 2025-01-06 08:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0018_auto_20250103_1430'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockoutform',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='customer_no',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='gift_bin',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='gift_qty',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='item_type',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='lot_no',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='order_bin',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='order_qty',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='packing_type',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='post_date',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='product_order',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='purchase_no',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='purchase_qty',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='purchase_unit',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='sap_mtr_no',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='size',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='version_no',
        ),
        migrations.RemoveField(
            model_name='stockoutform',
            name='version_seq',
        ),
        migrations.CreateModel(
            name='StockOutFormDetail',
            fields=[
                ('form_no', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('product_order', models.CharField(blank=True, max_length=20, null=True)),
                ('customer_no', models.CharField(blank=True, max_length=20, null=True)),
                ('version_no', models.CharField(blank=True, max_length=20, null=True)),
                ('version_seq', models.CharField(blank=True, max_length=20, null=True)),
                ('lot_no', models.CharField(blank=True, max_length=20, null=True)),
                ('packing_type', models.CharField(blank=True, max_length=20, null=True)),
                ('purchase_no', models.CharField(blank=True, max_length=20, null=True)),
                ('purchase_qty', models.CharField(blank=True, max_length=20, null=True)),
                ('size', models.CharField(blank=True, max_length=20, null=True)),
                ('purchase_unit', models.CharField(max_length=20, null=True)),
                ('post_date', models.CharField(blank=True, max_length=20, null=True)),
                ('order_qty', models.CharField(blank=True, max_length=20, null=True)),
                ('gift_qty', models.CharField(blank=True, max_length=20, null=True)),
                ('supplier', models.CharField(blank=True, max_length=20, null=True)),
                ('sap_mtr_no', models.CharField(blank=True, max_length=20, null=True)),
                ('desc', models.CharField(blank=True, max_length=2000, null=True)),
                ('gift_bin', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockout_gift_bin', to='warehouse.bin')),
                ('item_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockout_itemtype', to='warehouse.itemtype')),
                ('order_bin', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockout_order_bin', to='warehouse.bin')),
            ],
        ),
    ]