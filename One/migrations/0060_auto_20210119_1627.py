# Generated by Django 3.1.2 on 2021-01-19 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0059_auto_20210119_1406'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='data',
            name='d_data',
        ),
        migrations.AddField(
            model_name='data',
            name='d_description',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
