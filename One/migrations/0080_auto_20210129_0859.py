# Generated by Django 3.1.2 on 2021-01-29 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0079_auto_20210129_0845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='d_status',
            field=models.CharField(default='健康', max_length=20, null=True),
        ),
    ]
