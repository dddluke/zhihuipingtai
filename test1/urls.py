"""test1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import traceback
from collections import Counter

import requests
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from jsonpath import jsonpath
from requests.auth import HTTPBasicAuth
from rest_framework import permissions
from rest_framework_swagger.views import get_swagger_view

from One import consumers
from One import models as m
from One import views as v
from .views import *

# from verifications import urls
schema_view = get_swagger_view(title='API文档')

schema_view = get_schema_view(
    openapi.Info(
        title="API接口文档平台",  # 必传
        default_version='v1',  # 必传
        description="这是一个美轮美奂的接口文档",
        terms_of_service="http://api.xiaogongjin.site",
        contact=openapi.Contact(email="xiaogongjin@qq.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # 权限类
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('backendlogin/', admin.site.urls),
    path('one/', include('One.urls')),
    path('text/', include('text.urls')),
    # ('upload',path.join(STATIC_ROOT,'upload').replace('\\','/') ),
    # path('static/', include('static')),
    path(r'chat/', consumers.ChatConsumer),
    path(r'verification/', include('verifications.urls')),
    # path(r'verification/', include('verifications.urls')),
    path(r'docs/', schema_view),
    # path(r'login/', login),
    path(r'', TemplateView.as_view(template_name='index.html')),
    # path(r'blogin/', blogin),
    # url(r'', TemplateView.as_view(template_name='chat.html')),
    path(r'notifications/', include('notifications.urls', namespace='notifications')),
    path(r'my_notificaitons/', v.my_notifications, name="my_notifications"),
    # 第三方登录
    # path('', include('social_django.urls', namespace='social')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path(r'redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schemaredoc'),

]
urlpatterns += staticfiles_urlpatterns()
ip = 'http://124.164.247.45:4694/'
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
# from django_apscheduler.jobstores import
import datetime

def timedelta(sign, dt, value):
    """
    对指定时间进行加减运算，几秒、几分、几小时、几日、几周、几月、几年
    sign: y = 年, m = 月, w = 周, d = 日, h = 时, n = 分钟, s = 秒
    dt: 日期，只能是datetime或datetime.date类型
    value: 加减的数值
    return: 返回运算后的datetime类型值
    """
    if not isinstance(dt, datetime.datetime) and not isinstance(dt, datetime.date):
        raise Exception("日期类型错误")

    if sign == 'y':
        year = dt.year + value
        if isinstance(dt, datetime.date):
            return datetime.datetime(year, dt.month, dt.day)
        elif isinstance(dt, datetime.datetime):
            return datetime.datetime(year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
        else:
            return None
    elif sign == 'm':
        year = dt.year
        month = dt.month + value
        ### 如果月份加减后超出范围，则需要计算一下，对年份进行处理 ###
        # 如果月份加减后等于0时，需要特殊处理一下
        if month == 0:
            year = year - 1
            month = 12
        else:
            # 对年月进行处理
            year = year + month // 12
            month = month % 12
        if isinstance(dt, datetime.date):
            return datetime.datetime(year, month, dt.day)
        elif isinstance(dt, datetime.datetime):
            return datetime.datetime(year, month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
        else:
            return None
    elif sign == 'w':
        delta = datetime.timedelta(weeks=value)
    elif sign == 'd':
        delta = datetime.timedelta(days=value)
    elif sign == 'h':
        delta = datetime.timedelta(hours=value)
    elif sign == 'n':
        delta = datetime.timedelta(minutes=value)
    elif sign == 's':
        delta = datetime.timedelta(seconds=value)
    else:
        return None

    return dt + delta

def alarm():
    """
    对某设备的所有参数组 进行单独的webaccess数据获取，并将三个数据进行判断取其一返回前端
    :param request: 机械设备ID device_id
    :return:
    """
    print('---------报警开始-----------')
    now = datetime.datetime.now()
    print(now)
    i = 0
    groups = m.DataGroup.objects.filter(has_alert=1)  # 获取有报警规则的设备参数组
    # print('报警测试组')
    # print(groups)
    data = m.Data.objects.filter(d_name='dfgsdhfshdgfhsdf')
    for group in groups:
        datas = m.Data.objects.filter(d_g_id_id=group.id)  # 获取有报警规则的设备参数个数
        data = data | datas
        for date in datas:
            i += 1
    # print('报警测试数据')
    # print(datas)
    datas = data
    i = str(i)  # 参数个数
    now = datetime.datetime.now()
    time = timedelta(sign='s', value=-4, dt=now)
    # time = timedelta(sign='n', value=-10, dt=time)
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    # time = now.strftime('%Y-%m-%d %H:%M:%S')
    ProjectName = 'test'
    url = ip + 'WaWebService/Json/GetDataLog' + '/' + ProjectName + '/' + 'node1'
    headers = {"Content-Type": "application/json"}
    # request数据格式,Total指有几个tag
    format_header0 = '{"StartTime":"'
    format_header0 = format_header0 + str(time)
    format_header1 = '","IntervalType":"M","Interval":1,"Records":1'
    format_header = format_header0 + format_header1 + ',"Tags": '
    format_tail = '}'

    taglist = []
    for data in datas:
        name = data.d_name
        taglistchild = {"Name": str(name), "DataType": 0}
        taglist.append(taglistchild)
    format_body = str(taglist)
    http_format = format_header + format_body + format_tail
    http_format = str(http_format)
    http_format = http_format.replace("'", '"')  # request里必须使用双引号
    # print(http_format)
    data = json.loads(http_format)  # 必须先将str变成Json
    data = json.dumps(data)  # 再将Json变成str，这样才能被requests模块正确使用
    # print(data)
    # 发送带身份验证的post请求
    print('---------------------通讯开始------------------')
    now = datetime.datetime.now()
    print(now)
    resp = requests.post(url, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'), timeout=60)
    response = resp.content.decode()  # str
    r_str = json.loads(response)  # dict
    print('---------------------通讯结束------------------')
    now = datetime.datetime.now()
    print(now)
    # print(r_str)
    # try:
    realtimevalue = jsonpath(r_str, '$.DataLog..Values[0]')
    realtimetag = jsonpath(r_str, '$.DataLog..Name')
    # print(realtimetag)
    for group in groups:  # 每个组
        groupname = group.dg_name
        device = m.Device.objects.get(id=group.dg_d_id_id)
        project = m.Project.objects.get(id=device.d_p_id_id)
        company = m.Company.objects.get(id=project.p_c_id_id)
        dict1 = {'name': groupname, 'value': 0, 'device': device.d_name}
        data = m.Data.objects.filter(d_g_id=group.id)
        # print(d.d_name)
        if not data:  # 设备未设置参数
            group.realtimevalue = '#'
            group.save()
            continue
        valuelist = []
        a = []
        for d in data:  # 三个值
            # print(d.d_name)
            if d.d_name in realtimetag:
                # print(d.d_name)
                b = realtimetag.index(d.d_name)
                # print(b)
                value = realtimevalue[b]
                # print(value)
                if value == '#':
                    continue
                valuelist.append(value)
                # print(valuelist)
            else:
                pass
        if not valuelist:
            continue
        for r in valuelist:
            r = str(r)
            r = r.replace("['", "")
            r = r.replace("']", "")
            r = float(r)
            r = round(r, 2)
            # r = '#'
            a.append(r)
        # print(a)
        print('---------------------开始比对------------------')
        now = datetime.datetime.now()
        print(now)
        b = dict(Counter(a))
        # print(b)
        c = [key for key, value in b.items() if value >= 1]
        # print(c)
        c = c[0]
        dict1["value"] = c
        # print(dict1)

        datagroup = m.DataGroup.objects.get(dg_name=groupname, dg_d_id_id=group.dg_d_id_id)
        alert = m.Alert.objects.get(a_datagroup_id=datagroup.id)

        c = round(c, 2)
        alarmlog = m.AlarmLog()
        name = str(project.p_name) + '-' + str(device.d_name) + '-' + str(datagroup.dg_name)
        alarmlog.log_name = name
        alarmlog.log_alarm_data = c
        alarmlog.log_device = device
        alarmlog.log_project = project
        alarmlog.log_company = company
        alarmlog.log_group_name = dict1['name']
        alarmlog.log_time = datetime.datetime.now()
        if c >= alert.a_highest_line:
            alarmlog.log_alarm_type = alert.a_highest_level
            alarmlog.log_message = alert.a_highest_tip
            alarmlog.save()
            device.d_alert_count += 1
            device.save()
        elif c >= alert.a_high_line:
            alarmlog.log_alarm_type = alert.a_high_level
            alarmlog.log_message = alert.a_high_tip
            alarmlog.save()
            device.d_alert_count += 1
            device.save()
        elif c <= alert.a_lowest_line:
            alarmlog.log_alarm_type = alert.a_lowest_level
            alarmlog.log_message = alert.a_lowest_tip
            alarmlog.save()
            device.d_alert_count += 1
            device.save()
        elif c <= alert.a_low_line:
            alarmlog.log_alarm_type = alert.a_low_level
            alarmlog.log_message = alert.a_low_tip
            alarmlog.save()
            device.d_alert_count += 1
            device.save()
        datagroup.realtimevalue = c
        datagroup.realtime = time
        datagroup.save()
        print('------结束----------')
    # except Exception as e:
    #     print("获取实时值失败")
    #     traceback.print_exc()
    now = datetime.datetime.now()
    print(now)

    return True

def realtime():
    """
    对某设备的所有参数组 进行单独的webaccess数据获取，并将三个数据进行判断取其一返回前端
    :param request: 机械设备ID device_id
    :return:
    """
    print('---------报警开始-----------')
    now = datetime.datetime.now()
    print(now)
    i = 0
    groups = m.DataGroup.objects.filter(has_data=1)  # 获取有报警规则的设备参数组
    # print('报警测试组')
    # print(groups)
    data = m.Data.objects.filter(d_name='dfgsdhfshdgfhsdf')
    for group in groups:
        datas = m.Data.objects.filter(d_g_id_id=group.id)  # 获取有报警规则的设备参数个数
        data = data | datas
        for date in datas:
            i += 1
    # print('报警测试数据')
    # print(datas)
    datas = data
    i = str(i)  # 参数个数
    now = datetime.datetime.now()
    time = timedelta(sign='s', value=-4, dt=now)
    # time = timedelta(sign='n', value=-10, dt=time)
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    # time = now.strftime('%Y-%m-%d %H:%M:%S')
    ProjectName = 'test'
    url = ip + 'WaWebService/Json/GetDataLog' + '/' + ProjectName + '/' + 'node1'
    headers = {"Content-Type": "application/json"}
    # request数据格式,Total指有几个tag
    format_header0 = '{"StartTime":"'
    format_header0 = format_header0 + str(time)
    format_header1 = '","IntervalType":"M","Interval":1,"Records":1'
    format_header = format_header0 + format_header1 + ',"Tags": '
    format_tail = '}'

    taglist = []
    for data in datas:
        name = data.d_name
        taglistchild = {"Name": str(name), "DataType": 0}
        taglist.append(taglistchild)
    format_body = str(taglist)
    http_format = format_header + format_body + format_tail
    http_format = str(http_format)
    http_format = http_format.replace("'", '"')  # request里必须使用双引号
    # print(http_format)
    data = json.loads(http_format)  # 必须先将str变成Json
    data = json.dumps(data)  # 再将Json变成str，这样才能被requests模块正确使用
    # print(data)
    # 发送带身份验证的post请求
    print('---------------------通讯开始------------------')
    now = datetime.datetime.now()
    print(now)
    resp = requests.post(url, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'), timeout=60)
    response = resp.content.decode()  # str
    r_str = json.loads(response)  # dict
    print('---------------------通讯结束------------------')
    now = datetime.datetime.now()
    print(now)
    # print(r_str)
    # try:
    realtimevalue = jsonpath(r_str, '$.DataLog..Values[0]')
    realtimetag = jsonpath(r_str, '$.DataLog..Name')
    # print(realtimetag)
    for group in groups:  # 每个组
        groupname = group.dg_name
        device = m.Device.objects.get(id=group.dg_d_id_id)
        project = m.Project.objects.get(id=device.d_p_id_id)
        company = m.Company.objects.get(id=project.p_c_id_id)
        dict1 = {'name': groupname, 'value': 0, 'device': device.d_name}
        data = m.Data.objects.filter(d_g_id=group.id)
        # print(d.d_name)
        if not data:  # 设备未设置参数
            group.realtimevalue = '#'
            group.save()
            continue
        valuelist = []
        a = []
        for d in data:  # 三个值
            # print(d.d_name)
            if d.d_name in realtimetag:
                # print(d.d_name)
                b = realtimetag.index(d.d_name)
                # print(b)
                value = realtimevalue[b]
                # print(value)
                if value == '#':
                    continue
                valuelist.append(value)
                # print(valuelist)
            else:
                pass
        if not valuelist:
            continue
        for r in valuelist:
            r = str(r)
            r = r.replace("['", "")
            r = r.replace("']", "")
            r = float(r)
            r = round(r, 2)
            # r = '#'
            a.append(r)
        # print(a)
        print('---------------------开始比对------------------')
        now = datetime.datetime.now()
        print(now)
        b = dict(Counter(a))
        # print(b)
        c = [key for key, value in b.items() if value >= 1]
        # print(c)
        c = c[0]
        dict1["value"] = c
        # print(dict1)
        datagroup = m.DataGroup.objects.get(dg_name=groupname)
        alert = m.Alert.objects.get(a_datagroup_id=datagroup.id)

        c = round(c, 2)
        alarmlog = m.AlarmLog()
        name = str(project.p_name) + '-' + str(device.d_name) + '-' + str(datagroup.dg_name)
        alarmlog.log_name = name
        alarmlog.log_alarm_data = c
        alarmlog.log_device = device
        alarmlog.log_project = project
        alarmlog.log_company = company
        alarmlog.log_group_name = dict1['name']
        alarmlog.log_time = datetime.datetime.now()
        if c >= alert.a_highest_line:
            alarmlog.log_alarm_type = alert.a_highest_level
            alarmlog.log_message = alert.a_highest_tip
            alarmlog.save()
            device.d_alert_count += 1
            device.save()
        elif c >= alert.a_high_line:
            alarmlog.log_alarm_type = alert.a_high_level
            alarmlog.log_message = alert.a_high_tip
            alarmlog.save()
            device.d_alert_count += 1
            device.save()
        elif c <= alert.a_lowest_line:
            alarmlog.log_alarm_type = alert.a_lowest_level
            alarmlog.log_message = alert.a_lowest_tip
            alarmlog.save()
            device.d_alert_count += 1
            device.save()
        elif c <= alert.a_low_line:
            alarmlog.log_alarm_type = alert.a_low_level
            alarmlog.log_message = alert.a_low_tip
            alarmlog.save()
            device.d_alert_count += 1
            device.save()
        datagroup.realtimevalue = c
        datagroup.realtime = time
        datagroup.save()
        print('------结束----------')
    # except Exception as e:
    #     print("获取实时值失败")
    #     traceback.print_exc()
    now = datetime.datetime.now()
    print(now)

    return True

def historydata():
    """
        对某设备的所有参数组 进行单独的webaccess数据获取，并将三个数据进行判断取其一返回前端
        :param request: 机械设备ID device_id
        :return:
        """
    print('---------报警开始-----------')
    now = datetime.datetime.now()
    print(now)
    i = 0
    groups = m.DataGroup.objects.filter(has_alert=1)  # 获取有报警规则的设备参数组
    # print('报警测试组')
    # print(groups)
    data = m.Data.objects.filter(d_name='dfgsdhfshdgfhsdf')
    for group in groups:
        datas = m.Data.objects.filter(d_g_id_id=group.id)  # 获取有报警规则的设备参数个数
        data = data | datas
        for date in datas:
            i += 1
    # print('报警测试数据')
    # print(datas)
    datas = data
    i = str(i)  # 参数个数
    now = datetime.datetime.now()
    time = timedelta(sign='s', value=-4, dt=now)
    # time = timedelta(sign='n', value=-10, dt=time)
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    # time = now.strftime('%Y-%m-%d %H:%M:%S')
    ProjectName = 'test'
    url = ip + 'WaWebService/Json/GetDataLog' + '/' + ProjectName + '/' + 'node1'
    headers = {"Content-Type": "application/json"}
    # request数据格式,Total指有几个tag
    format_header0 = '{"StartTime":"'
    format_header0 = format_header0 + str(time)
    format_header1 = '","IntervalType":"M","Interval":1,"Records":3'
    format_header = format_header0 + format_header1 + ',"Tags": '
    format_tail = '}'
    taglist = []
    for data in datas:
        name = data.d_name
        taglistchild = {"Name": str(name), "DataType": 0}
        taglist.append(taglistchild)
    format_body = str(taglist)
    http_format = format_header + format_body + format_tail
    http_format = str(http_format)
    http_format = http_format.replace("'", '"')  # request里必须使用双引号
    # print(http_format)
    data = json.loads(http_format)  # 必须先将str变成Json
    data = json.dumps(data)  # 再将Json变成str，这样才能被requests模块正确使用
    # print(data)
    # 发送带身份验证的post请求
    print('---------------------通讯开始------------------')
    now = datetime.datetime.now()
    print(now)
    resp = requests.post(url, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'), timeout=60)
    response = resp.content.decode()  # str
    r_str = json.loads(response)  # dict
    print('---------------------通讯结束------------------')
    now = datetime.datetime.now()
    print(now)
    # print(r_str)
    # try:
    realtimevalue = jsonpath(r_str, '$.DataLog..Values[0]')
    realtimetag = jsonpath(r_str, '$.DataLog..Name')
    print(realtimevalue)
    print(realtimetag)
    return True

def test():
    print('---------定时器任务-----------')

executors = {
    'default': ThreadPoolExecutor(20)
}
scheduler = BackgroundScheduler(executors=executors, daemon=True)
scheduler.add_job(alarm, 'interval', minutes=10)  # 每30分钟进行数据点位告警检测
# scheduler.add_job(historydata, 'cron', hour=9, minute=30)  # 每天0点30分进行历史数据获取
# scheduler.add_job(historydata, 'interval', minutes=1)  # 每天0点30分进行历史数据获取
# scheduler.job.Job.pause()
scheduler.start()

