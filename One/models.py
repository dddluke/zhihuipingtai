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
    company_number = models.IntegerField(null=True)
    # u_department = models.CharField(max_length=32, null=True)  # 用户所在部门，默认为空
    u_icon = models.FileField(null=True, upload_to='uicons/%Y%m%d')
    u_type = models.CharField(default='游客', max_length=10)
    tag = models.ManyToManyField('Tag')
    project = models.ManyToManyField('Project')
    collectdevice = models.ManyToManyField('Collectdevice')
    knowledge = models.ManyToManyField('Knowledge')
    is_employee = models.BooleanField(default=0)
    wisepasstoken = models.TextField(null=True)
    work = models.CharField(verbose_name='职务', max_length=10, null=True)
    openid = models.CharField(verbose_name='微信OpenId', max_length=100, null=True)

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


# class Company(models.Model):
#     """
#     公司表
#     """
#     id = models.BigAutoField(primary_key=True)
#     c_u_id = models.OneToOneField(LoginUser, default=None, null=True, on_delete=models.CASCADE, db_column='c_u_id')
#     # upload_to Media_root设置的路径
#     company_icon = models.FileField(upload_to='cicons/%Y%m%d')
#     company_name = models.CharField(max_length=32, unique=True)
#     company_address = models.CharField(max_length=64, unique=False)
#     active = models.IntegerField(default=0)
#     context = models.CharField(max_length=128, null=True, unique=False)  # 公司简介
#
#     # def toDict(self):
#     #     return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])  # type(self._meta.fields).__name__
class Company(models.Model):
    """
    公司表
    """
    id = models.BigAutoField(primary_key=True)
    c_u_id = models.OneToOneField(LoginUser, default=None, null=True, on_delete=models.CASCADE, db_column='c_u_id')
    # upload_to Media_root设置的路径
    company_name = models.CharField(null=True, max_length=32, unique=True, verbose_name='企业名')  # 企业名
    company_mailbox = models.CharField(null=True, max_length=50, unique=True, verbose_name='企业邮箱')  # 邮箱
    company_address = models.CharField(null=True, max_length=110, unique=True, verbose_name='企业地址')  # 地址
    company_zip_code = models.IntegerField(null=True, verbose_name='企业邮编')  # 邮编
    company_icon = models.ImageField(null=True, upload_to='cicons/%Y%m%d', verbose_name='企业标志')  # 企业标志
    company_content = models.CharField(max_length=5000, blank=True, null=True, verbose_name='企业简介')  # 非必传
    company_register_number = models.BigIntegerField(null=True, verbose_name="营业执照注册号")
    company_license = models.ImageField(null=True, upload_to='license/%Y%m%d', verbose_name="营业执照副本扫描件")
    company_begin_date = models.DateTimeField(null=True, verbose_name="企业成立日期")
    company_office_number = models.CharField(max_length=30, unique=True, null=True, verbose_name="企业对公账号")
    company_boss_ID_card = models.ImageField(upload_to='ID_card/%Y%m%d', null=True, verbose_name="法人代表身份证")
    company_business_range = models.CharField(max_length=200, blank=True, null=True, verbose_name="经营范围")  # 非必传
    company_register_money = models.CharField(max_length=30, blank=True, null=True, verbose_name="注册资本")  # 非必传
    # company_organize_code = models.CharField(max_length=30, blank=True, null=True, verbose_name="组织机构代码")  # 非必传
    active = models.IntegerField(blank=True, null=True, default=0, verbose_name="公司激活状态")
    draft = models.BooleanField(default=0)


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
    p_c_address = models.CharField(max_length=50, null=True)
    p_city = models.CharField(max_length=10, null=True)
    p_address = models.CharField(max_length=100, null=True)
    p_register_time = models.DateTimeField(null=True)
    p_dashboard = models.TextField(null=True)
    p_position = models.CharField(null=True, max_length=40, verbose_name="经纬度")

    # p_longitude = models.DecimalField(decimal_places=20, max_digits=30, null=True)  # 经度  需修改
    # p_latitude = models.DecimalField(decimal_places=20, max_digits=30, null=True)  # 纬度  需修改


class Collectdevice(models.Model):
    """
    采集设备
    """
    cd_p_id = models.ForeignKey(Project, null=True, default=None, on_delete=models.CASCADE, db_column='cd_p_id')  # 项目id
    cd_c_id = models.ForeignKey(Company, null=True, default=None, on_delete=models.CASCADE, db_column='cd_c_id')  # 公司id
    cd_m_id = models.ForeignKey(LoginUser, null=True, related_name='capply', on_delete=models.CASCADE,
                                db_column='cd_m_id')  # 申请人id
    # cd_nodeid = models.CharField(max_length=32)  # 研华采集设备的id
    cd_name = models.CharField(max_length=32, null=True)
    cd_produce_time = models.CharField(max_length=32, null=True)
    cd_manufacturer = models.CharField(max_length=32, null=True)
    cd_install_time = models.DateTimeField(null=True)
    cd_SN = models.CharField(max_length=40, null=True)
    cd_SIM = models.CharField(max_length=30, null=True)
    cd_GPS = models.CharField(null=True, max_length=40)
    cd_placed = models.CharField(null=True, max_length=40)  # 安装位置
    cd_data_status = models.CharField(max_length=20, null=True)  # 设备采集状态
    cd_last_contract_time = models.DateTimeField(null=True)

    cd_port_number = models.IntegerField(null=True)  # 端口号
    cd_description = models.CharField(max_length=100, null=True)  # 描述
    cd_unit_number = models.CharField(max_length=100, null=True)  # 组ID
    cd_device_type = models.CharField(max_length=100, null=True)  # 设备类型
    cd_primary_ip = models.CharField(max_length=30, null=True)  # 设备主通讯IP
    cd_primary_port = models.CharField(max_length=10, null=True)  # 设备主通讯端口
    cd_primary_address = models.CharField(max_length=50, null=True)  # 设备主通讯地址
    cd_secondary_ip = models.CharField(max_length=30, null=True)  # 设备副通讯IP
    cd_secondary_port = models.CharField(max_length=10, null=True)
    cd_secondary_address = models.CharField(max_length=50, null=True)
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

    d_p_id = models.ForeignKey(Project, default=None, on_delete=models.CASCADE, db_column='d_p_id', null=True)  # 项目id
    d_m_id = models.ForeignKey(LoginUser, default=None, on_delete=models.CASCADE, db_column='d_mm_id',
                               null=True)  # 申请人id
    d_c_id = models.ForeignKey(Collectdevice, default=None, on_delete=models.CASCADE, db_column='d_c_id',
                               null=True)  # 采集设备id
    d_co_id = models.ForeignKey(Company, default=None, on_delete=models.CASCADE, db_column='d_co_id', null=True)  # 公司id
    d_u_id = models.IntegerField(default=None, null=True)  # 负责人id（关联
    d_active = models.IntegerField(default=1)
    d_name = models.CharField(max_length=32, null=True)  # 设备名称
    d_GPS = models.CharField(max_length=60, null=True)  # GPS信息
    d_produce_time = models.DateTimeField(null=True)  # 出厂日期
    d_manufacturer = models.CharField(max_length=32, null=True)  # 设备制造商
    d_status = models.CharField(max_length=20, null=True, default='健康')  # 设备状态
    d_register_time = models.DateTimeField(null=True)  # 平台注册日期
    d_alert_count = models.IntegerField(default=0)
    d_company_number = models.IntegerField(null=True)  # 设备在公司中编号
    # d_series_number = models.IntegerField()  # 序列号
    # d_tunnel = models.CharField(max_length=32)  # 通道
    # d_data_status = models.CharField(max_length=20)  # 设备采集状态
    # d_last_contract_time = models.DateTimeField()


class Devicedata(models.Model):
    """
    机械设备属性
    """
    ddd_d_id = models.ForeignKey(Device, default=None, on_delete=models.CASCADE, db_column='ddd_d_id')  # 机械设备id
    ddd_name = models.CharField(max_length=32)  # 属性名
    ddd_detail = models.CharField(max_length=60, null=True)  # 属性参数


class DataGroup(models.Model):
    """
    机械设备数据项组
    """
    dg_name = models.CharField(max_length=32)  # 组名
    dg_d_id = models.ForeignKey(Device, default=None, on_delete=models.CASCADE, db_column='dg_d_id')  # 机械设备id
    realtimevalue = models.CharField(max_length=32, null=True)
    realtime = models.DateTimeField(null=True)
    has_data = models.BooleanField(default=0)
    has_alert = models.BooleanField(default=0)
    alert_id = models.IntegerField(null=True)
    dg_type = models.CharField(max_length=32,default='其他')


class Data(models.Model):
    """
    数据项
    """
    d_cd_id = models.ForeignKey(Collectdevice, default=None, on_delete=models.CASCADE, db_column='d_cd_id',
                                null=True)  # 采集设备id
    d_d_id = models.ForeignKey(Device, default=None, on_delete=models.DO_NOTHING, db_column='d_d_id',
                               null=True)  # 机械设备ID
    d_name = models.CharField(max_length=50, null=True)  # 数据项编号：A1002349 etc.
    d_description = models.CharField(max_length=50, null=True)  # 数据项简介：XXX温度 0-150 etc.
    d_nickname = models.CharField(max_length=50, null=True)  # 数据项简称
    d_alarm = models.BooleanField(default=False)  # 数据项是否有报警规则
    d_g_id = models.ForeignKey(DataGroup, default=None, blank=True, null=True, on_delete=models.SET_NULL,
                               db_column='d_g_id')  # 数据项组ID
    # d_data = models.FloatField()  # 数据项实时数值


class DataLogJan2021(models.Model):
    """
    数据历史记录，图表用
    """
    dl_g_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='dl_g_id_jan',
                                null=True)  # 设备属性组id
    dl_d_name = models.CharField(max_length=50, null=True)
    dl_value = models.CharField(max_length=50, null=True)
    dl_time = models.DateTimeField(null=True)
    dl_month = models.IntegerField(default=1)


class DataLogFeb2021(models.Model):
    """
    数据历史记录，图表用
    """
    dl_g_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='dl_g_id_feb',
                                null=True)  # 设备属性组id
    dl_d_name = models.CharField(max_length=50, null=True)
    dl_value = models.CharField(max_length=50, null=True)
    dl_time = models.DateTimeField(null=True)
    dl_month = models.IntegerField(default=2)


class DataLogMar2021(models.Model):
    """
    数据历史记录，图表用
    """
    dl_g_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='dl_g_id_mar',
                                null=True)  # 设备属性组id
    dl_d_name = models.CharField(max_length=50, null=True)
    dl_value = models.CharField(max_length=50, null=True)
    dl_time = models.DateTimeField(null=True)
    dl_month = models.IntegerField(default=2)


class DataLogMay2021(models.Model):
    """
    数据历史记录，图表用
    """
    dl_g_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='dl_g_id_may',
                                null=True)  # 设备属性组id
    dl_d_name = models.CharField(max_length=50, null=True)
    dl_value = models.CharField(max_length=50, null=True)
    dl_time = models.DateTimeField(null=True)
    dl_month = models.IntegerField(default=2)


class DataLogApr2021(models.Model):
    """
    数据历史记录，图表用
    """
    dl_g_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='dl_g_id_apr',
                                null=True)  # 设备属性组id
    dl_d_name = models.CharField(max_length=50, null=True)
    dl_value = models.CharField(max_length=50, null=True)
    dl_time = models.DateTimeField(null=True)
    dl_month = models.IntegerField(default=2)


class DataLogJun2021(models.Model):
    """
    数据历史记录，图表用
    """
    dl_g_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='dl_g_id_jun',
                                null=True)  # 设备属性组id
    dl_d_name = models.CharField(max_length=50, null=True)
    dl_value = models.CharField(max_length=50, null=True)
    dl_time = models.DateTimeField(null=True)
    dl_month = models.IntegerField(default=2)


class DataLogJul2021(models.Model):
    """
    数据历史记录，图表用
    """
    dl_g_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='dl_g_id_jul',
                                null=True)  # 设备属性组id
    dl_d_name = models.CharField(max_length=50, null=True)
    dl_value = models.CharField(max_length=50, null=True)
    dl_time = models.DateTimeField(null=True)
    dl_month = models.IntegerField(default=2)


class DataLogAug2021(models.Model):
    """
    数据历史记录，图表用
    """
    dl_g_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='dl_g_id_aug',
                                null=True)  # 设备属性组id
    dl_d_name = models.CharField(max_length=50, null=True)
    dl_value = models.CharField(max_length=50, null=True)
    dl_time = models.DateTimeField(null=True)
    dl_month = models.IntegerField(default=2)


class DataLogSep2021(models.Model):
    """
    数据历史记录，图表用
    """
    dl_g_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='dl_g_id_sep',
                                null=True)  # 设备属性组id
    dl_d_name = models.CharField(max_length=50, null=True)
    dl_value = models.CharField(max_length=50, null=True)
    dl_time = models.DateTimeField(null=True)
    dl_month = models.IntegerField(default=2)


class DataLogOct2021(models.Model):
    """
    数据历史记录，图表用
    """
    dl_g_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='dl_g_id_oct',
                                null=True)  # 设备属性组id
    dl_d_name = models.CharField(max_length=50, null=True)
    dl_value = models.CharField(max_length=50, null=True)
    dl_time = models.DateTimeField(null=True)
    dl_month = models.IntegerField(default=2)


class DataLogNov2021(models.Model):
    """
    数据历史记录，图表用
    """
    dl_g_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='dl_g_id_nov',
                                null=True)  # 设备属性组id
    dl_d_name = models.CharField(max_length=50, null=True)
    dl_value = models.CharField(max_length=50, null=True)
    dl_time = models.DateTimeField(null=True)
    dl_month = models.IntegerField(default=2)


class DataLogDec2021(models.Model):
    """
    数据历史记录，图表用
    """
    dl_g_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='dl_g_id_dec',
                                null=True)  # 设备属性组id
    dl_d_name = models.CharField(max_length=50, null=True)
    dl_value = models.CharField(max_length=50, null=True)
    dl_time = models.DateTimeField(null=True)
    dl_month = models.IntegerField(default=2)


class Alert(models.Model):
    """
    设备告警规则
    """
    a_datagroup_id = models.ForeignKey(DataGroup, default=None, on_delete=models.CASCADE, db_column='a_datagroup_id',
                                       null=True)
    a_company_id = models.ForeignKey(Company, default=None, on_delete=models.CASCADE, db_column='a_company_id',
                                     null=True)
    a_project_id = models.ForeignKey(Project, default=None, on_delete=models.CASCADE, db_column='a_project_id',
                                     null=True)
    a_c_id = models.ForeignKey(Collectdevice, default=None, on_delete=models.CASCADE, db_column='a_c_id', null=True)
    a_device_id = models.ForeignKey(Device, default=None, on_delete=models.CASCADE, db_column='a_device_id', null=True)

    a_highest_line = models.FloatField(null=True)  # 上上控制线值
    a_highest_level = models.CharField(max_length=10, default='告警')
    a_highest_tip = models.CharField(max_length=20, null=True)  # 通知提示信息，由用户设置告警时设置
    a_high_line = models.FloatField(null=True)  # 上控制线值
    a_high_level = models.CharField(max_length=10, default='预警')
    a_high_tip = models.CharField(max_length=20, null=True)
    a_low_line = models.FloatField(null=True)  # 下下控制线值
    a_low_level = models.CharField(max_length=10, default='预警')
    a_low_tip = models.CharField(max_length=20, null=True)
    a_lowest_line = models.FloatField(null=True)  # 下控制线值
    a_lowest_level = models.CharField(max_length=10, default='告警')
    a_lowest_tip = models.CharField(max_length=20, null=True)


# 告警记录
class AlarmLog(models.Model):
    """
    告警记录
    """
    log_name = models.CharField(max_length=100, null=True)
    log_alarm_type = models.CharField(max_length=20, null=True)  # 告警级别
    log_alarm_data = models.CharField(max_length=10, null=True)  # 设备告警时的值
    log_device = models.ForeignKey(Device, default=None, on_delete=models.DO_NOTHING, db_column='log_device', null=True)
    log_project = models.ForeignKey(Project, default=None, on_delete=models.DO_NOTHING, db_column='log_project',
                                    null=True)
    log_company = models.ForeignKey(Company, default=None, on_delete=models.DO_NOTHING, db_column='log_company',
                                    null=True)
    log_group_name = models.CharField(max_length=20, null=True)
    log_message = models.CharField(max_length=50, default='设备数值超出告警值')
    log_type = models.CharField(max_length=10, default='未解决')  # 告警后状态（已解决，未解决）
    log_repair = models.CharField(max_length=200, null=True)  # 维修信息
    log_time = models.DateTimeField(max_length=30, null=True)


class Devicemaintainrecord(models.Model):
    """
    设备维修记录
    """

    dm_d_id = models.ForeignKey(Device, default=None, on_delete=models.CASCADE, db_column='dm_d_id')
    dm_o_id = models.ForeignKey(LoginUser, default=None, on_delete=models.CASCADE, db_column='dm_o_id')
    dmo_name = models.CharField(max_length=20, null=True)
    dm_name = models.CharField(max_length=20, null=True)
    dm_d_detail = models.TextField()
    dm_time = models.DateTimeField()


class Worksheet(models.Model):
    """
    工单
    """
    w_e_id = models.ForeignKey(LoginUser, default=None, on_delete=models.CASCADE, db_column='w_e_id')
    w_u_phone = models.CharField(verbose_name='手机号', null=True, max_length=20)  # 手机号
    w_name = models.CharField(max_length=20, null=True)  # 工单名称
    w_type = models.CharField(max_length=20, null=True)  # 工单类型，由用户自定义上传
    w_content = models.CharField(max_length=2000, null=True)
    w_status = models.CharField(max_length=10, null=True)
    w_wechat = models.BooleanField(default=True)  # 微信创建为true，在pc完善后为false
    w_doc_id = models.IntegerField(default=None, null=True)  # None代表不存在解决方案
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

    k_user_id = models.CharField(max_length=32)  # 编辑人，一般为运营人员
    k_user_name = models.CharField(max_length=32, default=0)  # 编辑人姓名
    k_title = models.CharField(max_length=32)
    tag = models.ManyToManyField('Tag')
    k_type = models.CharField(max_length=10)
    k_date = models.DateTimeField()
    k_content = models.TextField()  # 内容
    k_status = models.IntegerField(default=0)  # 是否有解决方案
    k_thumbs_up = models.IntegerField(default=0)  # 点赞量
    k_visit = models.IntegerField(default=0)
    k_verify = models.IntegerField(default=0)  # 是否审核 1 审核完成 0 未审核
    k_checker = models.CharField(max_length=10, null=True)  # 审核人
    k_condition = models.CharField(max_length=8, null=True)  # 文章状态 转载 编辑
    k_v_date = models.DateTimeField(null=True)  # 审核文章时间
    k_draft = models.BooleanField(default=0)


class Tag(models.Model):
    """
    知识库/行业资讯
    """
    tag_name = models.CharField(max_length=10)


# class Collect(models.Model):
class Thumbs(models.Model):
    """
    点赞记录
    """
    thu_user_id = models.IntegerField()  # 点赞人ID
    thu_k_id = models.ForeignKey(Knowledge, default=None, on_delete=models.CASCADE)


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


class Doc(models.Model):
    doc_user_id = models.IntegerField(null=True)
    w_id = models.IntegerField(null=True)
    docfile = models.FileField(upload_to='tech/%Y%m%d')
    doc_f_ip = models.CharField(max_length=40, null=True)
    doc_is_active = models.BooleanField(default=False)


@receiver(pre_delete, sender=Doc)
def doc_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.docfile.delete(False)


# 配件类表
class FitSub(models.Model):
    fs_name = models.CharField(max_length=10, unique=True)  # 配件类名


# 配件信息表
class Fittings(models.Model):
    f_name = models.CharField(max_length=20, )  # 配件名
    f_subject = models.ForeignKey(FitSub, max_length=20, on_delete=models.CASCADE)  # 配件种类
    f_number = models.CharField(null=True, max_length=20)  # 产品编号
    f_machine = models.CharField(null=True, max_length=20)  # 机组编号
    f_else = models.TextField(null=True, blank=True)
    f_image = models.ImageField(upload_to='fittings_image/%Y%m%d', null=True, verbose_name="配件设备图片")


# 图片库
class DefaultImage(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(null=True, upload_to='default/%Y%m%d')


class ContactUs(models.Model):
    name = models.CharField(null=True, max_length=20)
    company = models.CharField(null=True, max_length=40)
    contactnumber = models.CharField(null=True, max_length=40)
    question = models.TextField(null=True, blank=True)
    read = models.BooleanField(default=0)
    date = models.DateTimeField(null=True)
