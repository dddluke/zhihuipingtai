# Generated by Django 3.1.2 on 2020-10-13 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0012_solution_s_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='knowledgemediastore',
            name='m_k_ip',
            field=models.CharField(max_length=40, null=True),
        ),
    ]
