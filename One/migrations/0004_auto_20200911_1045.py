# Generated by Django 3.1.1 on 2020-09-11 10:45

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0003_auto_20200911_0947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicemaintainrecord',
            name='dm_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 11, 10, 45, 14, 860768)),
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('d_name', models.CharField(max_length=20)),
                ('d_data', models.FloatField()),
                ('d_d_id', models.ForeignKey(db_column='d_d_id', default=None, on_delete=django.db.models.deletion.CASCADE, to='One.device')),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('a_highest_line', models.FloatField()),
                ('a_highest_level', models.CharField(choices=[(1, '正常'), (2, '提醒'), (3, '告警')], max_length=10)),
                ('a_highest_tip', models.CharField(max_length=20)),
                ('a_high_line', models.FloatField()),
                ('a_high_level', models.CharField(choices=[(1, '正常'), (2, '提醒'), (3, '告警')], max_length=10)),
                ('a_high_tip', models.CharField(max_length=20)),
                ('a_low_line', models.FloatField()),
                ('a_low_level', models.CharField(choices=[(1, '正常'), (2, '提醒'), (3, '告警')], max_length=10)),
                ('a_low_tip', models.CharField(max_length=20)),
                ('a_lowest_line', models.FloatField()),
                ('a_lowest_level', models.CharField(choices=[(1, '正常'), (2, '提醒'), (3, '告警')], max_length=10)),
                ('a_lowest_tip', models.CharField(max_length=20)),
                ('a_data_id', models.ForeignKey(db_column='a_data_id', default=None, on_delete=django.db.models.deletion.CASCADE, to='One.data')),
            ],
        ),
    ]
