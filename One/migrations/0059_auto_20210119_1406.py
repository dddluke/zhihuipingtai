# Generated by Django 3.1.2 on 2021-01-19 14:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0058_auto_20210119_1349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectdevice',
            name='cd_m_id',
            field=models.ForeignKey(db_column='cd_m_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='capply', to=settings.AUTH_USER_MODEL),
        ),
    ]
