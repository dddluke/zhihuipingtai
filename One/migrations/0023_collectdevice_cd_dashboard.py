# Generated by Django 3.1.2 on 2020-10-27 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0022_auto_20201016_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectdevice',
            name='cd_dashboard',
            field=models.CharField(max_length=80, null=True),
        ),
    ]
