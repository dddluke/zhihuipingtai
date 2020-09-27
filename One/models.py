import datetime
import django
from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField


# Create your models here.
# 继承AbstractUser，对原有的User表进行扩展，记得在setting中修改为AUTH_USER_MODEL = 'users.LoginUser'


class LoginUser(AbstractUser):
    """
    用户表
    """

    phone_numbers = models.CharField(verbose_name='手机号', unique=True, max_length=11)
    u_company_id = models.IntegerField(null=True)
    u_icon = models.ImageField(null=True, upload_to='uicons/%Y%m%d')
    u_type = models.CharField(null=True, max_length=10)

    def __str__(self):
        # return self.username
        return self.phone_numbers


class UserToken(models.Model):
    user = models.OneToOneField('LoginUser', models.CASCADE)
    token = models.CharField(max_length=255)


class Company(models.Model):
    """
    公司表
    """
    c_u_id = models.OneToOneField(LoginUser, default=None, null=True, on_delete=models.CASCADE, db_column='c_u_id')
    # upload_to Media_root设置的路径
    company_icon = models.ImageField(upload_to='cicons/%Y%m%d')
    company_name = models.CharField(max_length=32, unique=True)
    company_address = models.CharField(max_length=64, unique=True)
    active = models.IntegerField(default=0)
    context = models.CharField(max_length=128, null=True)  # 公司简介


#  项目由谁申请？未完成
class Project(models.Model):
    """
    项目
    """
    p_c_id = models.ForeignKey(Company, default=None, on_delete=models.CASCADE, db_column='p_c_id', null=True)
    p_u_id = models.ForeignKey(LoginUser, default=None, on_delete=models.CASCADE, db_column='p_u_id')  # 申请人id 外键关联
    p_active = models.IntegerField(default=0, null=True)
    p_name = models.CharField(max_length=32)
    p_description = models.CharField(max_length=300)
    p_type = models.CharField(max_length=20)  # 项目类型，自定义输入
    p_customer_type = models.CharField(max_length=20)
    p_party_a = models.CharField(max_length=30)  # 甲方
    p_purchase_time = models.DateTimeField()  # 采购日期
    p_setup_time = models.DateTimeField()  # 安装日期
    p_built_time = models.DateTimeField()  # 竣工日期
    p_contact_name = models.CharField(max_length=20)
    p_contact_number = models.IntegerField()  # 长度需修改
    p_province = models.CharField(max_length=10)
    p_city = models.CharField(max_length=10)
    p_address = models.CharField(max_length=100)
    p_longitude = models.DecimalField(decimal_places=20, max_digits=30)  # 经度  需修改
    p_latitude = models.DecimalField(decimal_places=20, max_digits=30)  # 纬度  需修改


class Device(models.Model):
    """
    设备
    """

    d_p_id = models.ForeignKey(Project, default=None, on_delete=models.CASCADE, db_column='d_p_id')  # 项目id
    d_m_id = models.ForeignKey(LoginUser, default=None, on_delete=models.CASCADE, db_column='d_mm_id')  # 申请人id
    d_u_id = models.IntegerField(default=None, null=True)  # 负责人id（关联
    d_active = models.IntegerField(default=0)
    d_name = models.CharField(max_length=32)
    d_series_number = models.IntegerField()  # 序列号
    d_tunnel = models.CharField(max_length=32)  # 通道
    d_status = models.CharField(max_length=20)  # 设备状态
    d_data_status = models.CharField(max_length=20)  # 设备采集状态
    d_last_contract_time = models.DateTimeField()
    d_register_time = models.DateTimeField()


class Data(models.Model):
    """
    数据项
    """

    d_d_id = models.ForeignKey(Device, default=None, on_delete=models.CASCADE, db_column='d_d_id')
    d_name = models.CharField(max_length=20)  # 数据项名称：XXX温度 etc.
    d_data = models.FloatField()  # 数据项实时数值


class Alert(models.Model):
    """
    设备告警规则
    """

    a_data_id = models.ForeignKey(Data, default=None, on_delete=models.CASCADE, db_column='a_data_id')
    a_highest_line = models.FloatField(null=True)  # 上上控制线值
    a_highest_level = models.CharField(max_length=10, null=True)
    a_highest_tip = models.CharField(max_length=20, null=True)  # 通知提示信息，由用户设置告警时设置
    a_high_line = models.FloatField(null=True)  # 上控制线值
    a_high_level = models.CharField(max_length=10, null=True)
    a_high_tip = models.CharField(max_length=20, null=True)
    a_low_line = models.FloatField(null=True)  # 下下控制线值
    a_low_level = models.CharField(max_length=10, null=True)
    a_low_tip = models.CharField(max_length=20, null=True)
    a_lowest_line = models.FloatField(null=True)  # 下控制线值
    a_lowest_level = models.CharField(max_length=10, null=True)
    a_lowest_tip = models.CharField(max_length=20, null=True)


class Devicemaintainrecord(models.Model):
    """
    设备维修记录
    """

    dm_d_id = models.ForeignKey(Device, default=None, on_delete=models.CASCADE, db_column='dm_d_id')
    dm_o_id = models.ForeignKey(LoginUser, default=None, on_delete=models.CASCADE, db_column='dm_o_id')
    dm_d_detail = models.CharField(max_length=2000)
    dm_time = models.DateTimeField()


class Worksheet(models.Model):
    """
    工单
    """
    w_e_id = models.ForeignKey(LoginUser, default=None, on_delete=models.CASCADE, db_column='w_e_id')
    w_name = models.CharField(max_length=20)
    w_type = models.CharField(max_length=20)  # 工单类型，由用户自定义上传
    w_content = models.CharField(max_length=2000)
    w_status = models.CharField(max_length=10)
    w_time = models.DateTimeField()


class Worksheetmedia(models.Model):
    """
    工单图库
    """
    wm_w_id = models.ForeignKey(Worksheet, default=None, on_delete=models.CASCADE, db_column='wm_w_id')
    wm_w_image = models.ImageField(upload_to='wmedia/%Y%m%d')
    wm_date = models.DateTimeField()


class Knowledge(models.Model):
    """
    知识库/行业资讯
    """

    k_user_id = models.IntegerField()  # 编辑人，一般为运营人员
    k_title = models.CharField(max_length=32)
    k_type = models.CharField(max_length=10)
    k_date = models.DateTimeField()
    k_content = models.CharField(max_length=20000)  # 内容


class Solution(models.Model):
    """
    知识库、行业资讯解决方案
    """

    s_user_id = models.IntegerField()  # 编辑人
    s_k_id = models.ForeignKey(Knowledge, on_delete=models.CASCADE, db_column='s_k_id')
    s_title = models.CharField(max_length=32)
    s_type = models.CharField(max_length=20)
    s_date = models.DateTimeField()
    s_content = models.CharField(max_length=20000)  # 内容


class KnowledgeMediaStore(models.Model):
    """
    知识库与行业资讯多媒体库
    """

    m_k_id = models.ForeignKey(Knowledge, default=None, on_delete=models.CASCADE, db_column='m_k_id')  # 知识库或行业资讯id
    m_k_filepath = models.ImageField(upload_to='kmedia/%Y%m%d')
    m_type = models.CharField(max_length=10)
    m_date = models.DateTimeField()


class Message(models.Model):
    """
    聊天记录
    """

    sender = models.ForeignKey(LoginUser, related_name='sent_message', on_delete=models.SET_NULL, blank=True, null=True,
                               verbose_name='发送者')
    recipient = models.ForeignKey(LoginUser, related_name='receive_messages', on_delete=models.SET_NULL, blank=True,
                                  null=True, verbose_name='接收者')
    message = models.TextField(blank=True, null=True, verbose_name='内容')
    unread = models.BooleanField(default=True, db_index=True, verbose_name='是否未读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()


class Complainrecord(models.Model):
    """
    客户投诉记录
    """

    cr_u_id = models.ForeignKey(LoginUser, related_name='sender', on_delete=models.SET_NULL, db_column='cr_u_id',
                                blank=True, null=True, )
    cr_e_id = models.ForeignKey(LoginUser, related_name='receiver', on_delete=models.SET_NULL, db_column='cr_e_id',
                                blank=True, null=True, )
    cr_detail = models.CharField(max_length=200)
    cr_date = models.DateTimeField()
    cr_type = models.CharField(max_length=10)


class Comment(models.Model):
    """
    客服评价
    """

    cm_u_id = models.ForeignKey(LoginUser, related_name='customer', on_delete=models.SET_NULL, db_column='cm_u_id',
                                blank=True, null=True, )
    cm_e_id = models.ForeignKey(LoginUser, related_name='service', on_delete=models.SET_NULL, db_column='cm_e_id',
                                blank=True, null=True, )
    cm_detail = models.CharField(max_length=200)
    cm_date = models.DateTimeField()
    cm_type = models.CharField(max_length=10)
