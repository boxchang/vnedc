# Generated by Django 3.2.25 on 2024-08-06 08:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20240718_0843'),
        ('collection', '0030_machine_mold_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterdefine',
            name='data_owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='param_define_unit', to='users.unit'),
        ),
    ]
