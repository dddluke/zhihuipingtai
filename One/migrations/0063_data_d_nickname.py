# Generated by Django 3.1.2 on 2021-01-20 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0062_auto_20210120_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='d_nickname',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
