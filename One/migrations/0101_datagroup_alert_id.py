# Generated by Django 3.1.2 on 2021-02-07 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0100_alarmlog_log_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='datagroup',
            name='alert_id',
            field=models.IntegerField(null=True),
        ),
    ]
