# Generated by Django 3.1.2 on 2020-10-12 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0010_remove_devicemaintainrecord_dm_o_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='knowledge',
            name='k_user_name',
            field=models.CharField(default=0, max_length=32),
        ),
    ]
