# Generated by Django 3.1.2 on 2020-10-12 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0011_knowledge_k_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='s_user_name',
            field=models.CharField(default=0, max_length=32),
        ),
    ]
