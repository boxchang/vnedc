# Generated by Django 3.2.25 on 2024-07-25 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0026_auto_20240723_1658'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterdefine',
            name='scada_column',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='parameterdefine',
            name='scada_table',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]