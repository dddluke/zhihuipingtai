# Generated by Django 3.1.2 on 2021-01-25 10:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0067_auto_20210125_1018'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='d_g_id',
            field=models.ForeignKey(db_column='d_g_id', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='One.datagroup'),
        ),
    ]
