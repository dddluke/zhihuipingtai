# Generated by Django 3.1.2 on 2021-01-12 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0048_worksheet_w_u_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worksheet',
            name='w_doc_id',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
