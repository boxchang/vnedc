# Generated by Django 3.2.25 on 2024-06-14 13:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('collection', '0003_remove_parameterdefine_data_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametervalue',
            name='plant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='param_value_plant', to='collection.plant'),
        ),
        migrations.CreateModel(
            name='Daily_Prod_Info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_date', models.DateField()),
                ('production_name_a1', models.CharField(max_length=50)),
                ('production_size_a1', models.CharField(max_length=50)),
                ('production_name_a2', models.CharField(max_length=50)),
                ('production_size_a2', models.CharField(max_length=50)),
                ('production_name_b1', models.CharField(max_length=50)),
                ('production_size_b1', models.CharField(max_length=50)),
                ('production_name_b2', models.CharField(max_length=50)),
                ('production_size_b2', models.CharField(max_length=50)),
                ('coagulant_time', models.CharField(max_length=50)),
                ('latex_time', models.CharField(max_length=50)),
                ('tooling_time', models.CharField(max_length=50)),
                ('create_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('create_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='daily_info_create_at', to=settings.AUTH_USER_MODEL)),
                ('plant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_info_plant', to='collection.plant')),
                ('update_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='daily_info_update_at', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
