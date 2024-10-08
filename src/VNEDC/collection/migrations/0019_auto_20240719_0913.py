# Generated by Django 3.2.25 on 2024-07-19 09:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('collection', '0018_auto_20240719_0913'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parameter_Type',
            fields=[
                ('param_code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='param_type_update_at', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='parameterdefine',
            name='param_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='param_param_type', to='collection.parameter_type'),
        ),
    ]
