# Generated by Django 3.1.2 on 2021-01-25 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0066_defaultimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='d_d_id',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='DataGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dg_name', models.CharField(max_length=32)),
                ('dg_d_id', models.ForeignKey(db_column='dg_d_id', default=None, on_delete=django.db.models.deletion.CASCADE, to='One.device')),
            ],
        ),
    ]
