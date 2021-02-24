# Generated by Django 3.1.2 on 2021-01-12 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('One', '0049_auto_20210112_1551'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='context',
        ),
        migrations.AddField(
            model_name='company',
            name='company_begin_date',
            field=models.DateTimeField(null=True, verbose_name='企业成立日期'),
        ),
        migrations.AddField(
            model_name='company',
            name='company_boss_ID_card',
            field=models.ImageField(null=True, upload_to='ID_card/%Y%m%d', verbose_name='法人代表身份证'),
        ),
        migrations.AddField(
            model_name='company',
            name='company_business_range',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='经营范围'),
        ),
        migrations.AddField(
            model_name='company',
            name='company_content',
            field=models.CharField(blank=True, max_length=5000, null=True, verbose_name='企业简介'),
        ),
        migrations.AddField(
            model_name='company',
            name='company_license',
            field=models.ImageField(null=True, upload_to='license/%Y%m%d', verbose_name='营业执照副本扫描件'),
        ),
        migrations.AddField(
            model_name='company',
            name='company_mailbox',
            field=models.CharField(max_length=50, null=True, unique=True, verbose_name='企业邮箱'),
        ),
        migrations.AddField(
            model_name='company',
            name='company_office_number',
            field=models.CharField(max_length=30, null=True, unique=True, verbose_name='企业对公账号'),
        ),
        migrations.AddField(
            model_name='company',
            name='company_organize_code',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='组织机构代码'),
        ),
        migrations.AddField(
            model_name='company',
            name='company_register_money',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='注册资本'),
        ),
        migrations.AddField(
            model_name='company',
            name='company_register_number',
            field=models.IntegerField(null=True, verbose_name='营业执照注册号'),
        ),
        migrations.AddField(
            model_name='company',
            name='company_zip_code',
            field=models.IntegerField(null=True, verbose_name='企业邮编'),
        ),
        migrations.AlterField(
            model_name='company',
            name='active',
            field=models.IntegerField(blank=True, null=True, verbose_name='公司激活状态'),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_address',
            field=models.CharField(max_length=64, null=True, unique=True, verbose_name='企业地址'),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_icon',
            field=models.ImageField(null=True, upload_to='cicons/%Y%m%d', verbose_name='企业标志'),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_name',
            field=models.CharField(max_length=32, null=True, unique=True, verbose_name='企业名'),
        ),
    ]
