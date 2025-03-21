# Generated by Django 3.2.25 on 2024-12-28 13:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0009_rename_comment_stockinform_desc'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockinform',
            name='customer_no',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='desc',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='gift_bin',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='gift_qty',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='item_type',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='lot_no',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='order_bin',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='order_no',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='order_qty',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='packing_type',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='post_date',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='purchase_no',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='purchase_qty',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='purchase_unit',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='sap_mtr_no',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='size',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='version_no',
        ),
        migrations.RemoveField(
            model_name='stockinform',
            name='version_seq',
        ),
        migrations.CreateModel(
            name='StockInFormDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('supplier', models.CharField(blank=True, max_length=20, null=True)),
                ('sap_mtr_no', models.CharField(blank=True, max_length=20, null=True)),
                ('desc', models.CharField(blank=True, max_length=2000, null=True)),
                ('form_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stockin_detail_form', to='warehouse.stockinform')),
                ('item_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockin_itemtype', to='warehouse.itemtype')),
                ('order_bin', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockin_order_bin', to='warehouse.bin')),
            ],
        ),
    ]
