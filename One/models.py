import datetime
import django
from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

# Create your models here.
# 继承AbstractUser，对原有的User表进行扩展，记得在setting中修改为AUTH_USER_MODEL = 'users.LoginUser'


class LoginUser(AbstractUser):
    """
    用户表
    """

    phone_numbers = models.CharField(verbose_name='手机号', unique=True, max_length=11)
    u_company_id = models.IntegerField(null=True)
    u_icon = models.FileField(null=True, upload_to='uicons/%Y%m%d')
    u_type = models.CharField(default='游客', max_length=10)
    tag = models.CharField(null=True, max_length=20)
    project = models.ManyToManyField('Project')
    collectdevice = models.ManyToManyField('Collectdevice')
    is_employee = models.BooleanField(default=0)
    wisepasstoken = models.TextField(null=True)

    def __str__(self):
        # return self.username
        return self.phone_numbers


@receiver(pre_delete, sender=LoginUser)
def loginuser_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.u_icon.delete(False)

# class UserToken(models.Model):
#     user = models.OneToOneField('LoginUser', models.CASCADE)
#     token = models.CharField(max_length=255)

# 研华token
class WisePassToken(models.Model):
    token = models.TextField(null=True)

class Company(models.Model):
    """
    公司表
    """
    id = models.BigAutoField(primary_key=True)
    c_u_id = models.OneToOneField(LoginUser, default=None, null=True, on_delete=models.CASCADE, db_column='c_u_id')
    # upload_to Media_root设置的路径
    company_icon = models.FileField(upload_to='cicons/%Y%m%d')
    company_name = models.CharField(max_length=32, unique=True)
    company_address = models.CharField(max_length=64, unique=False)
    active = models.IntegerField(default=0)
    context = models.CharField(max_length=128, null=True, unique=False)  # 公司简介

    # def toDict(self):
    #     return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])  # type(self._meta.fields).__name__


#  项目由谁申请？未完成
class Project(models.Model):
    """
    项目
    """
    p_c_id = models.ForeignKey(Company, default=None, on_delete=models.CASCADE, db_column='p_c_id', null=True)
    p_u_id = models.ForeignKey(LoginUser, default=None, related_name='apply', on_delete=models.CASCADE,
                               db_column='p_u_id', verbose_name='申请人')  # 申请人id 外键关联
    # p_o_id = models.ForeignKey(LoginUser, default=None, related_name='response', null=True, on_delete=models.CASCADE, db_column='p_o_id', verbose_name='项目负责人')  # 项目负责人or设备负责人
    p_active = models.IntegerField(default=1, null=True)
    p_name = models.CharField(max_length=32)
    p_description = models.CharField(max_length=300, null=True, unique=False)
    p_type = models.CharField(max_length=20, null=True)  # 项目类型，自定义输入  项目标签
    p_customer_type = models.CharField(max_length=20, null=True)
    p_party_a = models.CharField(max_length=30)  # 甲方
    p_purchase_time = models.CharField(max_length=30, null=True)  # 采购日期
    p_setup_time = models.CharField(max_length=30, null=True)  # 安装日期
    p_built_time = models.CharField(max_length=30, null=True)  # 竣工日期
    p_contact_name = models.CharField(max_length=20, null=True)
    p_contact_number = models.CharField(max_length=11, null=True)  # 长度需修改
    p_province = models.CharField(max_length=10, null=True)
    p_city = models.CharField(max_length=10, null=True)
    p_address = models.CharField(max_length=100, null=True)
    p_register_time = models.DateTimeField(null=True)
    p_dashboard = models.TextField(null=True)
    # p_longitude = models.DecimalField(decimal_places=20, max_digits=30, null=True)  # 经度  需修改
    # p_latitude = models.DecimalField(decimal_places=20, max_digits=30, null=True)  # 纬度  需修改


class Collectdevice(models.Model):
    """
    采集设备
    """
    cd_p_id = models.ForeignKey(Project, default=None, on_delete=models.CASCADE, db_column='cd_p_id')  # 项目id
    cd_c_id = models.ForeignKey(Company, default=None, on_delete=models.CASCADE, db_column='cd_c_id')  # 公司id
    cd_m_id = models.ForeignKey(LoginUser, default=None, related_name='capply', on_delete=models.CASCADE, db_column='cd_m_id')  # 申请人id
    cd_nodeid = models.CharField(max_length=32)  # 研华采集设备的id
    cd_name = models.CharField(max_length=32, null=True)
    cd_produce_time = models.CharField(max_length=32, null=True)
    cd_manufacturer = models.CharField(max_length=32, null=True)
    # loginuser = models.ManyToManyField('Loginuser')
    # cd_active = models.IntegerField(default=0)
    # cd_series_number = models.IntegerField()  # 序列号
    # cd_tunnel = models.CharField(max_length=32)  # 通道
    #
    # cd_status = models.CharField(max_length=20)  # 设备状态
    # cd_data_status = models.CharField(max_length=20)  # 设备采集状态
    # cd_last_contract_time = models.DateTimeField()
    # cd_register_time = models.DateTimeField()
    # cd_dashboard = models.CharField(max_length=80, null=True)


class Cdevicedata(models.Model):
    """
    采集设备属性
    """
    cdd_c_id = models.ForeignKey(Collectdevice, default=None, on_delete=models.CASCADE, db_column='cd_p_id')  # 采集设备id
    cdd_name = models.CharField(max_length=32)  # 属性名
    cdd_data = models.CharField(max_length=32)  # 属性数值


class Device(models.Model):
    """
    机械设备
    """

    d_p_id = models.ForeignKey(Project, default=None, on_delete=models.CASCADE, db_column='d_p_id')  # 项目id
    d_m_id = models.ForeignKey(LoginUser, default=None, on_delete=models.CASCADE, db_column='d_mm_id')  # 申请人id
    d_c_id = models.ForeignKey(Collectdevice, default=None, on_delete=models.CASCADE, db_column='d_c_id')  # 采集设备id
    d_u_id = models.IntegerField(default=None, null=True)  # 负责人id（关联
    d_active = models.IntegerField(default=0)
    d_name = models.CharField(max_length=32)
    d_series_number = models.IntegerField()  # 序列号
    d_tunnel = models.CharField(max_length=32)  # 通道
    d_status = models.CharField(max_length=20)  # 设备状态
    d_data_status = models.CharField(max_length=20)  # 设备采集状态
    d_last_contract_time = models.DateTimeField()
    d_register_time = models.DateTimeField()


class Devicedata(models.Model):
    """
    机械设备属性
    """
    ddd_d_id = models.ForeignKey(Device, default=None, on_delete=models.CASCADE, db_column='ddd_d_id')  # 机械设备id
    ddd_name = models.CharField(max_length=32)  # 属性名
    ddd_data = models.FloatField()  # 属性实时数值


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

    dmo_name = models.CharField(max_length=20, null=True)
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
    wm_w_image = models.FileField(upload_to='wmedia/%Y%m%d')
    wm_date = models.DateTimeField()


class Knowledge(models.Model):
    """
    知识库/行业资讯
    """

    k_user_id = models.IntegerField()  # 编辑人，一般为运营人员
    k_user_name = models.CharField(max_length=32, default=0)
    k_title = models.CharField(max_length=32)
    k_tag = models.CharField(default='无', max_length=20, blank=True)
    k_type = models.CharField(max_length=10)
    k_date = models.DateTimeField()
    k_content = models.CharField(max_length=20000)  # 内容
    k_status = models.BooleanField(default=0)  # 是否有解决方案


class Enterprise(models.Model):
    """
    企业动态
    """
    e_user_id = models.IntegerField()  # 编辑人，一般为运营人员
    e_user_name = models.CharField(max_length=32, default=0)
    e_title = models.CharField(max_length=32)
    e_image = models.FileField(upload_to='emedia/%Y%m%d')  # 封面图片
    e_date = models.DateTimeField()
    e_content = models.TextField()  # 内容

@receiver(pre_delete, sender=Enterprise)
def enterprise_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.e_image.delete(False)

class Solution(models.Model):
    """
    知识库、行业资讯解决方案
    """

    s_user_id = models.ForeignKey(LoginUser, default=None, on_delete=models.CASCADE, db_column='s_user_id')  # 编辑人
    s_k_id = models.ForeignKey(Knowledge, on_delete=models.CASCADE, db_column='s_k_id')
    s_user_name = models.CharField(max_length=32, default=0)
    s_title = models.CharField(max_length=32)
    s_type = models.CharField(max_length=20)
    s_date = models.DateTimeField()
    s_content = models.CharField(max_length=20000)  # 内容


class KnowledgeMediaStore(models.Model):
    """
    知识库与行业资讯多媒体库
    """

    # m_k_id = models.CharField(max_length=10, db_column='m_k_id', null=True)  # 知识库或行业资讯id
    m_k_filepath = models.FileField(upload_to='kmedia/%Y%m%d')
    m_k_ip = models.CharField(max_length=40, null=True)
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
    message = models.TextField(blank=True, null=True, verbose_name='聊天信息')
    # unread = models.BooleanField(default=True, db_index=True, verbose_name='是否未读')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'chat_records'
        verbose_name = '客服聊天记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id

    # def mark_as_read(self):
    #     if self.unread:
    #         self.unread = False
    #         self.save()




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


class Test(models.Model):
    t = models.FileField(upload_to='tmedia/%Y%m%d')
