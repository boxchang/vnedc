# Generated by Django 3.2.25 on 2024-07-19 09:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0020_parameterdefine_side'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameter_type',
            name='process_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='param_type_process_type', to='collection.process_type'),
        ),
    ]
