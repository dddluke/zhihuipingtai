# Generated by Django 3.1.2 on 2021-01-11 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0043_auto_20210111_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worksheet',
            name='w_content',
            field=models.CharField(max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='worksheet',
            name='w_name',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='worksheet',
            name='w_status',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='worksheet',
            name='w_type',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
