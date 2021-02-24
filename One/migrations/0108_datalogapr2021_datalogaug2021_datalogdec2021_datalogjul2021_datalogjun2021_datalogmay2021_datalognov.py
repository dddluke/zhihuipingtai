# Generated by Django 3.1.2 on 2021-02-23 09:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0107_contactus_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataLogSep2021',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dl_value', models.CharField(max_length=50, null=True)),
                ('dl_time', models.DateTimeField(null=True)),
                ('dl_month', models.IntegerField(default=2)),
                ('dl_g_id', models.ForeignKey(db_column='dl_g_id_sep', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='One.datagroup')),
            ],
        ),
        migrations.CreateModel(
            name='DataLogOct2021',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dl_value', models.CharField(max_length=50, null=True)),
                ('dl_time', models.DateTimeField(null=True)),
                ('dl_month', models.IntegerField(default=2)),
                ('dl_g_id', models.ForeignKey(db_column='dl_g_id_oct', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='One.datagroup')),
            ],
        ),
        migrations.CreateModel(
            name='DataLogNov2021',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dl_value', models.CharField(max_length=50, null=True)),
                ('dl_time', models.DateTimeField(null=True)),
                ('dl_month', models.IntegerField(default=2)),
                ('dl_g_id', models.ForeignKey(db_column='dl_g_id_nov', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='One.datagroup')),
            ],
        ),
        migrations.CreateModel(
            name='DataLogMay2021',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dl_value', models.CharField(max_length=50, null=True)),
                ('dl_time', models.DateTimeField(null=True)),
                ('dl_month', models.IntegerField(default=2)),
                ('dl_g_id', models.ForeignKey(db_column='dl_g_id_may', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='One.datagroup')),
            ],
        ),
        migrations.CreateModel(
            name='DataLogJun2021',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dl_value', models.CharField(max_length=50, null=True)),
                ('dl_time', models.DateTimeField(null=True)),
                ('dl_month', models.IntegerField(default=2)),
                ('dl_g_id', models.ForeignKey(db_column='dl_g_id_jun', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='One.datagroup')),
            ],
        ),
        migrations.CreateModel(
            name='DataLogJul2021',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dl_value', models.CharField(max_length=50, null=True)),
                ('dl_time', models.DateTimeField(null=True)),
                ('dl_month', models.IntegerField(default=2)),
                ('dl_g_id', models.ForeignKey(db_column='dl_g_id_jul', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='One.datagroup')),
            ],
        ),
        migrations.CreateModel(
            name='DataLogDec2021',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dl_value', models.CharField(max_length=50, null=True)),
                ('dl_time', models.DateTimeField(null=True)),
                ('dl_month', models.IntegerField(default=2)),
                ('dl_g_id', models.ForeignKey(db_column='dl_g_id_dec', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='One.datagroup')),
            ],
        ),
        migrations.CreateModel(
            name='DataLogAug2021',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dl_value', models.CharField(max_length=50, null=True)),
                ('dl_time', models.DateTimeField(null=True)),
                ('dl_month', models.IntegerField(default=2)),
                ('dl_g_id', models.ForeignKey(db_column='dl_g_id_aug', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='One.datagroup')),
            ],
        ),
        migrations.CreateModel(
            name='DataLogApr2021',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dl_value', models.CharField(max_length=50, null=True)),
                ('dl_time', models.DateTimeField(null=True)),
                ('dl_month', models.IntegerField(default=2)),
                ('dl_g_id', models.ForeignKey(db_column='dl_g_id_apr', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='One.datagroup')),
            ],
        ),
    ]
