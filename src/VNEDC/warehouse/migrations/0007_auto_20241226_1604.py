# Generated by Django 3.2.25 on 2024-12-26 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0006_itemtype_movementtype_stockinform_stockoutform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemtype',
            name='type_code',
            field=models.CharField(max_length=20, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='movementtype',
            name='mvt_code',
            field=models.CharField(max_length=20, primary_key=True, serialize=False),
        ),
    ]