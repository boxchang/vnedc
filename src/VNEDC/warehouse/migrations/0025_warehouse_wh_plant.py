# Generated by Django 3.2.25 on 2025-02-14 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0024_stockoutformdetail_order_bin'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouse',
            name='wh_plant',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
