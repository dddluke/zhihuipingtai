# Generated by Django 3.1.1 on 2020-10-10 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0003_knowledge_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='knowledge',
            name='k_status',
            field=models.IntegerField(default=0),
        ),
    ]
