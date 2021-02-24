# Generated by Django 3.1.2 on 2021-01-27 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0068_data_d_g_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='FitSub',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fs_name', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='fittings',
            name='f_image',
            field=models.ImageField(null=True, upload_to='fittings_image/%Y%m%d', verbose_name='配件设备图片'),
        ),
        migrations.AlterField(
            model_name='defaultimage',
            name='image',
            field=models.ImageField(null=True, upload_to='default/%Y%m%d'),
        ),
        migrations.AlterField(
            model_name='fittings',
            name='f_else',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='fittings',
            name='f_machine',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='fittings',
            name='f_number',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='knowledge',
            name='k_content',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='fittings',
            name='f_subject',
            field=models.ForeignKey(max_length=20, on_delete=django.db.models.deletion.CASCADE, to='One.fitsub'),
        ),
    ]
