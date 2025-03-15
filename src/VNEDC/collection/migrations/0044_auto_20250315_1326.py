# Generated by Django 3.2.25 on 2025-03-15 13:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('collection', '0043_auto_20250315_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lab_parameter_control',
            name='create_at',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='lab_parameter_control',
            name='create_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='lab_param_create_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
