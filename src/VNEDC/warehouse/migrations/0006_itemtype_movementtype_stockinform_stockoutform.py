# Generated by Django 3.2.25 on 2024-12-26 16:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('warehouse', '0005_alter_bin_value_history_old_qty'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemType',
            fields=[
                ('type_code', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('type_name', models.CharField(max_length=20)),
                ('desc', models.CharField(blank=True, max_length=200, null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('create_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='itemtype_create_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StockOutForm',
            fields=[
                ('form_no', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('order_no', models.CharField(blank=True, max_length=20, null=True)),
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
                ('comment', models.CharField(blank=True, max_length=2000, null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('create_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockout_form_create_by', to=settings.AUTH_USER_MODEL)),
                ('gift_bin', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockout_gift_bin', to='warehouse.bin')),
                ('item_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockout_itemtype', to='warehouse.itemtype')),
                ('order_bin', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockout_order_bin', to='warehouse.bin')),
            ],
        ),
        migrations.CreateModel(
            name='StockInForm',
            fields=[
                ('form_no', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('order_no', models.CharField(blank=True, max_length=20, null=True)),
                ('customer_no', models.CharField(blank=True, max_length=20, null=True)),
                ('version_no', models.CharField(blank=True, max_length=20, null=True)),
                ('version_seq', models.CharField(blank=True, max_length=20, null=True)),
                ('lot_no', models.CharField(blank=True, max_length=20, null=True)),
                ('packing_type', models.CharField(blank=True, max_length=20, null=True)),
                ('purchase_no', models.CharField(blank=True, max_length=20, null=True)),
                ('purchase_qty', models.CharField(blank=True, max_length=20, null=True)),
                ('size', models.CharField(blank=True, max_length=20, null=True)),
                ('purchase_unit', models.CharField(blank=True, max_length=20, null=True)),
                ('post_date', models.CharField(blank=True, max_length=20, null=True)),
                ('order_qty', models.CharField(blank=True, max_length=20, null=True)),
                ('gift_qty', models.CharField(blank=True, max_length=20, null=True)),
                ('supplier', models.CharField(blank=True, max_length=20, null=True)),
                ('sap_mtr_no', models.CharField(blank=True, max_length=20, null=True)),
                ('comment', models.CharField(blank=True, max_length=2000, null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('create_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockin_form_create_by', to=settings.AUTH_USER_MODEL)),
                ('gift_bin', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockin_gift_bin', to='warehouse.bin')),
                ('item_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockin_itemtype', to='warehouse.itemtype')),
                ('order_bin', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockin_order_bin', to='warehouse.bin')),
            ],
        ),
        migrations.CreateModel(
            name='MovementType',
            fields=[
                ('mvt_code', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('mvt_name', models.CharField(max_length=20)),
                ('desc', models.CharField(blank=True, max_length=200, null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('create_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='mvt_create_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
