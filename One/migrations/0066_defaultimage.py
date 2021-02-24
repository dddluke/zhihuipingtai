# Generated by Django 3.1.2 on 2021-01-22 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0065_fittings'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('image', models.FileField(null=True, upload_to='default/%Y%m%d')),
            ],
        ),
    ]
