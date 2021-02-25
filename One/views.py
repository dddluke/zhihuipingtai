import json
import random
from datetime import timedelta
from pathlib import Path
from collections import Counter
import requests
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from jsonpath import jsonpath
from pydocx import PyDocX
from requests.auth import HTTPBasicAuth
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from test1.settings import BASE_DIR
from .models import *
from .serializers import *

localip = 'http://192.168.0.106:8009'

color = ['#e53935', '#8e24aa', '#2196f3', '#00bcd4', '#c5e1a5', '#ffca28', '#ff7043', '#e53935', '#8e24aa', '#2196f3',
         '#00bcd4', '#c5e1a5', '#ffca28', '#ff7043', '#e53935', '#8e24aa', '#2196f3', '#00bcd4', '#c5e1a5', '#ffca28',
         '#ff7043', '#e53935', '#8e24aa', '#2196f3', '#00bcd4', '#c5e1a5', '#ffca28', '#ff7043']


# 时间加减功能
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


# 搜素功能
# 搜索所有激活状态公司
class Companylist(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = []  # 权限判断相同

    def get(self, request, *args, **kwargs):
        objJson = serialize("json", Company.objects.filter(active=1))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}

        return HttpResponse(json.dumps(response_data))


class Allcompanylist(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = []  # 权限判断相同

    def get(self, request, *args, **kwargs):
        objJson = serialize("json", Company.objects.all())
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}

        return HttpResponse(json.dumps(response_data))


# 搜索所有未激活状态公司
def unactivatedcompanylist(request):
    objJson = serialize("json", Company.objects.filter(active=0))
    objStr = json.loads(objJson)
    response_data = {'code': ["200"], 'data': objStr}

    return HttpResponse(json.dumps(response_data))


class Unactivatedcompanylist(GenericAPIView):
    '''
    搜索所有未激活状态公司,需要用户为公司管理人员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = UnactivatedcompanylistSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = UnactivatedcompanylistSerializer(data=request.data)
        if serializer.is_valid():
            objJson = serialize("json", Company.objects.filter(active=0))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}

            return HttpResponse(json.dumps(response_data))

        return Response(serializer.errors)


# 返回最大页数

def max_page(page_range):
    p = str(page_range)
    s = re.findall("\d+", p)[1]
    s = int(s)
    s = s - 1
    return s


#  查看所有激活状态用户
def userlist(request):
    objJson = serialize("json", LoginUser.objects.filter(is_active=1))
    objStr = json.loads(objJson)
    response_data = {'code': ["200"], 'data': objStr}
    return HttpResponse(json.dumps(response_data))


#  查看所有未激活状态用户
def unactivateduserlist(request):
    objJson = serialize("json", LoginUser.objects.filter(is_active=0))
    objStr = json.loads(objJson)
    response_data = {'code': ["200"], 'data': objStr}
    return HttpResponse(json.dumps(response_data))


# 当停用公司管理员账号时，进行公司、项目、设备、数据、告警规则同步停用，按照顺序，高一级停用时后续同样停用
def deactivatecompany(company_id):
    company = Company.objects.get(id=company_id)
    company.active = 0
    delprojects(company_id)
    company.save()
    return True


def delprojects(company_id):
    # company_id = request.POST.get('company_id')
    projects = Project.objects.filter(p_c_id=company_id)
    if not projects:
        return True
    for project in projects:
        project.p_active = 0
        deldevice(project.id)
        project.save()
    return True


def deldevice(project_id):
    devices = Device.objects.filter(d_p_id=project_id)
    if not devices:
        return True
    for device in devices:
        device.d_active = 0
        device.save()
    return True


# def wisepasstoken():
#     return render('loading.html')


# 用户CRUD
# 手机号验证视图
class SmsView(APIView):
    '''
    发送验证码
    '''
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = SmsSerializer(data=request.data)

        if serializer.is_valid():
            code = (random.randint(1000, 100000))

            response = {
                'message': ['手机号格式正确，已发送验证码，注意查收'],
                'code': ["200"],
            }
            phone = serializer.data['phone']
            response['phone'] = phone
            response['code'] = code

            cache.set(phone, code, 150)

            return Response(response)
        return Response(serializer.errors)


# 手机号验证视图（修改密码时
class Smsvalid(APIView):
    '''
    修改密码时发送验证码
    '''
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = SmsvalidSerializer(data=request.data)

        if serializer.is_valid():
            code = (random.randint(1000, 100000))

            response = {
                'message': ['已发送验证码，注意查收'],
                'code': ["200"],
            }
            phone = serializer.data['phone']
            response['phone'] = phone
            response['code'] = code

            cache.set(phone, code, 150)

            return Response(response)
        return Response(serializer.errors)


# 注册视图
class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser()
            user.username = serializer.data['username']
            password = serializer.data['password']
            user.password = make_password(password)
            user.phone_numbers = serializer.data['phone_numbers']
            user.save()
            user_id = user.id
            response = {
                'message': ['用户注册成功'],
                'code': ["200"],
                'user_id': user_id
            }
            return Response(response)
        return Response(serializer.errors)


class UserAddTags(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def post(self, request, *args, **kwargs):
        # tags = request.GET.get('tags')
        response = request.body.decode()
        r_str = json.loads(response)
        tags = jsonpath(r_str, '$.tags[*]')
        user_id = jsonpath(r_str, '$.user_id')
        user_id = str(user_id)
        user_id = user_id.replace('[', '')
        user_id = user_id.replace(']', '')
        length = len(tags)
        print(r_str)
        print(user_id)
        print(tags)
        i = 0
        for i in range(length):
            user = LoginUser.objects.get(id=user_id)
            # newinput.i_yes_data = i_yes_data[i]
            user.tag.add(Tag.objects.get(tag_name=tags[i]))
        # user.save()

        response = {
            'message': ['添加成功'],
            'code': ["200"]
        }
        return Response(response)


# class UserTags(APIView):
#     authentication_classes = []
#     permission_classes = []
#     serializer_class = []
#
#     def get(self, request, *args, **kwargs):
#         # tags = request.GET.get('tags')
#         user_id = request.GET.get('user_id')
#         # user = LoginUser.objects.get(id=user_id)
#         tags = Tag.objects.all()
#         a = []
#         for tag in tags:
#             users = tag.loginuser_set.filter(id=user_id, tag=tag)
#             print(users)
#             print('--')
#             if users:
#                 users = tag.loginuser_set.get(id=user_id, tag=tag)
#                 a.append(tag.tag_name)
#         response = {
#             'message': ['查询成功'],
#             'code': ["200"],
#             'data': a
#         }
#         return Response(response)


class UserTags(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        # tags = request.GET.get('tags')
        user_id = request.GET.get('user_id')
        # user = LoginUser.objects.get(id=user_id)
        tags = Tag.objects.all()
        a = []
        for tag in tags:
            dict = {"type": '', 'label': '', 'effect': 'plain'}
            users = tag.loginuser_set.filter(id=user_id, tag=tag)
            dict["label"] = tag.tag_name
            if users:
                dict["effect"] = 'dark'
            a.append(dict)
        response = {
            'message': ['查询成功'],
            'code': ["200"],
            'data': a
        }
        return Response(response)


class UserEditTags(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def post(self, request, *args, **kwargs):
        # tags = request.GET.get('tags')
        response = request.body.decode()
        r_str = json.loads(response)
        tags = jsonpath(r_str, '$.tags[*]')
        user_id = jsonpath(r_str, '$.user_id')
        user_id = str(user_id)
        user_id = user_id.replace('[', '')
        user_id = user_id.replace(']', '')
        length = len(tags)
        ttag = Tag.objects.all()
        for tag in ttag:
            user = LoginUser.objects.get(id=user_id)
            tagname = tag.tag_name
            # print(user)
            try:
                user.tag.remove(Tag.objects.get(tag_name=tagname))
            except Exception as e:
                continue
        i = 0
        for i in range(length):
            user = LoginUser.objects.get(id=user_id)
            # newinput.i_yes_data = i_yes_data[i]
            user.tag.add(Tag.objects.get(tag_name=tags[i]))
        # user.save()

        response = {
            'message': ['修改成功'],
            'code': ["200"]
        }
        return Response(response)


class LeaveContactMessage(GenericAPIView):
    """
    留言
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = LeaveContactMessageSerializer

    def post(self, request, *args, **kwargs):
        serializer = LeaveContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            contact = ContactUs()
            contact.name = serializer.data['name']
            contact.company = serializer.data['company']
            contact.contactnumber = serializer.data['contactnumber']
            contact.question = serializer.data['question']
            contact.date = datetime.datetime.now()
            contact.save()
            response_data = {'code': ["200"], 'message': ['留言成功']}
            response = HttpResponse(json.dumps(response_data))
            return response

        return Response(serializer.errors, status=200)


class ContactMessageList(GenericAPIView):
    """
    留言
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = ContactMessageListSerializer

    def post(self, request, *args, **kwargs):
        serializer = ContactMessageListSerializer(data=request.data)
        if serializer.is_valid():
            contact = ContactUs.objects.all().values('id', 'name', 'company', 'date', 'read').order_by('-date')
            # objJson = serialize("json", contact)
            # objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': contact}
            response = Response(response_data)
            return response

        return Response(serializer.errors, status=200)


class ViewContactMessage(GenericAPIView):
    """
    留言
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = ViewContactMessageSerializer

    def post(self, request, *args, **kwargs):
        serializer = ViewContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            contact = ContactUs.objects.get(id=serializer.data['c_id'])
            contact.read = 1
            objJson = serialize("json", [contact])
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            response = HttpResponse(json.dumps(response_data))
            return response

        return Response(serializer.errors, status=200)


class WechatLogin(GenericAPIView):
    """
    小程序账号登录
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = WechatLoginSerializerV1

    def post(self, request, *args, **kwargs):
        serializer = WechatLoginSerializerV1(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(
                Q(username=serializer.data['ph']) | Q(phone_numbers=serializer.data['ph']) | Q(
                    email=serializer.data['ph']))
            objJson = serialize("json", LoginUser.objects.filter(id=user.id))
            objStr = json.loads(objJson)
            identity = '前台'
            type = user.u_type
            u_type = ['超级管理员', '运维顾问', '客服运营']
            if type in u_type:
                identity = '后台'
            if user.u_company_id:
                company = Company.objects.filter(id=user.u_company_id)
                if company:
                    company = Company.objects.get(id=user.u_company_id)
                    response_data = {'code': ["200"], 'data': objStr, 'identity': identity,
                                     'companyname': company.company_name}
                    return HttpResponse(json.dumps(response_data))
            companyname = '无'
            response_data = {'code': ["200"], 'data': objStr, 'identity': identity, 'companyname': companyname}
            response = HttpResponse(json.dumps(response_data))
            return response

        return Response(serializer.errors, status=200)


class WechatLoginV2(GenericAPIView):
    """
    小程序手机验证码登录
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = WechatLoginSerializerv2

    def post(self, request, *args, **kwargs):
        serializer = WechatLoginSerializerv2(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(phone_numbers=serializer.data['phone_numbers'])
            objJson = serialize("json", LoginUser.objects.filter(id=user.id))
            objStr = json.loads(objJson)
            identity = '前台'
            type = user.u_type
            u_type = ['超级管理员', '运维顾问', '客服运营']
            if type in u_type:
                identity = '后台'
            if user.u_company_id:
                company = Company.objects.filter(id=user.u_company_id)
                if company:
                    company = Company.objects.get(id=user.u_company_id)
                    response_data = {'code': ["200"], 'data': objStr, 'identity': identity,
                                     'companyname': company.company_name}
                    return HttpResponse(json.dumps(response_data))
            companyname = '无'
            response_data = {'code': ["200"], 'data': objStr, 'identity': identity, 'companyname': companyname}
            response = HttpResponse(json.dumps(response_data))
            # token = 'eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJjb3VudHJ5IjoiIiwiY3JlYXRpb25UaW1lIjoxNjAwNDEzMDUwLCJleHAiOjE2MDM5Mzk1NzcsImZpcnN0TmFtZSI6IlVzZXIiLCJpYXQiOjE2MDM5MzU5NzcsImlkIjoiMjRkOTY3MzAtZWY0NS00YTgxLWJlNzEtOWEwOWUzZWVhMjU0IiwiaXNzIjoid2lzZS1wYWFzIiwibGFzdE1vZGlmaWVkVGltZSI6MTYwMzkzNTk3NSwibGFzdE5hbWUiOiJBcHAiLCJyZWZyZXNoVG9rZW4iOiI4OTY4Zjg4ZC0xOTg4LTExZWItODNhNi0xMjRiYjdhYTY0MWUiLCJzdGF0dXMiOiJBY3RpdmUiLCJ1c2VybmFtZSI6IjQ0MjMwNzk0MkBxcS5jb20ifQ.ORCbitbFLbqyuUtQq0zOVY5vcgKMDVYfv95_cew6By3j5T43nqgFqQqszSQDZwtSVAG3XcRUJjKNjsK-L3gOcw'
            # response.set_cookie('EIToken', token, expires=timedelta(days=3))
            return response

        return Response(serializer.errors, status=200)


#  用户登录
class LoginView(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(
                Q(username=serializer.data['ph']) | Q(phone_numbers=serializer.data['ph']) | Q(
                    email=serializer.data['ph']))
            objJson = serialize("json", LoginUser.objects.filter(id=user.id))
            objStr = json.loads(objJson)
            if user.u_company_id:
                company = Company.objects.filter(id=user.u_company_id)
                if company:
                    company = Company.objects.get(id=user.u_company_id)
                    response_data = {'code': ["200"], 'data': objStr, 'companyname': company.company_name}
                    return HttpResponse(json.dumps(response_data))
            companyname = '无'
            identity = '前台'
            type = user.u_type
            u_type = ['超级管理员', '运维顾问', '客服运营']
            if type in u_type:
                identity = '后台'
            print(identity)
            response_data = {'code': ["200"], 'data': objStr, 'companyname': companyname}
            response = HttpResponse(json.dumps(response_data))
            # token = 'eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJjb3VudHJ5IjoiIiwiY3JlYXRpb25UaW1lIjoxNjAwNDEzMDUwLCJleHAiOjE2MDM5Mzk1NzcsImZpcnN0TmFtZSI6IlVzZXIiLCJpYXQiOjE2MDM5MzU5NzcsImlkIjoiMjRkOTY3MzAtZWY0NS00YTgxLWJlNzEtOWEwOWUzZWVhMjU0IiwiaXNzIjoid2lzZS1wYWFzIiwibGFzdE1vZGlmaWVkVGltZSI6MTYwMzkzNTk3NSwibGFzdE5hbWUiOiJBcHAiLCJyZWZyZXNoVG9rZW4iOiI4OTY4Zjg4ZC0xOTg4LTExZWItODNhNi0xMjRiYjdhYTY0MWUiLCJzdGF0dXMiOiJBY3RpdmUiLCJ1c2VybmFtZSI6IjQ0MjMwNzk0MkBxcS5jb20ifQ.ORCbitbFLbqyuUtQq0zOVY5vcgKMDVYfv95_cew6By3j5T43nqgFqQqszSQDZwtSVAG3XcRUJjKNjsK-L3gOcw'
            # response.set_cookie('EIToken', token, expires=timedelta(days=3))
            return response

        return Response(serializer.errors, status=200)


#  后台用户登录
class Login(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginbSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginbSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(
                Q(username=serializer.data['ph']) | Q(phone_numbers=serializer.data['ph']) | Q(
                    email=serializer.data['ph']))
            # for user in users:
            #     jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            #     jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            #     # 往添加token的数据
            #     payload = jwt_payload_handler(user=user)  # 这里需要修改为自己的数据
            #     # 生成对token进行加密
            #     token = jwt_encode_handler(payload)
            #     UserToken.objects.update_or_create(user=user, defaults={'token': token})
            # user_id = user.id
            # loginuser = LoginUser.objects.get(id=user.id)
            # user_id = loginuser.id
            # response = {
            #     'message': ['登录成功'],
            #     'code': ["200"]
            #     'user_id': [user_id],
            #     # 'token':token
            #     # 'loginuser': loginuser,
            #     # 'user_username': loginuser.username,
            #     # 'user_id': [loginuser.id],
            # }
            # return Response(response, status=200)
            objJson = serialize("json", LoginUser.objects.filter(id=user.id))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors, status=200)


#  后台用户登录
class Logout(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginbSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginbSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(
                Q(username=serializer.data['ph']) | Q(phone_numbers=serializer.data['ph']) | Q(
                    email=serializer.data['ph']))
            # for user in users:
            #     jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            #     jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            #     # 往添加token的数据
            #     payload = jwt_payload_handler(user=user)  # 这里需要修改为自己的数据
            #     # 生成对token进行加密
            #     token = jwt_encode_handler(payload)
            #     UserToken.objects.update_or_create(user=user, defaults={'token': token})
            # user_id = user.id
            # loginuser = LoginUser.objects.get(id=user.id)
            # user_id = loginuser.id
            # response = {
            #     'message': ['登录成功'],
            #     'code': ["200"]
            #     'user_id': [user_id],
            #     # 'token':token
            #     # 'loginuser': loginuser,
            #     # 'user_username': loginuser.username,
            #     # 'user_id': [loginuser.id],
            # }
            # return Response(response, status=200)
            objJson = serialize("json", LoginUser.objects.filter(id=user.id))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors, status=200)


# 修改个人信息
class Editmyprofile(APIView):
    """
    修改个人信息
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = EditmyprofileSerializer,

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get("user_id")
        print(user_id)
        # user = LoginUser.objects.get(id=serializer.data['user_id'])
        loginuser = LoginUser.objects.filter(id=user_id)

        if loginuser:
            loginuser = LoginUser.objects.get(id=user_id)
            company_id = loginuser.u_company_id
            company = Company.objects.filter(id=company_id)
            if not company:
                companyname = '无'
                companyaddress = '无'
                objJson = serialize("json", LoginUser.objects.filter(id=user_id))
                objStr = json.loads(objJson)
                response_data = {'code': ["200"], 'data': objStr, 'companyname': companyname,
                                 'companyaddress': companyaddress}
                return HttpResponse(json.dumps(response_data))
            company = Company.objects.get(id=company_id)
            companyname = company.company_name
            companyaddress = company.company_address
            objJson = serialize("json", LoginUser.objects.filter(id=user_id))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr, 'companyname': companyname,
                             'companyaddress': companyaddress}
            return HttpResponse(json.dumps(response_data))
        response1 = {
            'message': ['用户不存在'],
            # 'token':token
            'code': [404]
        }
        return Response(response1, status=200)

    def post(self, request, *args, **kwargs):
        serializer = EditmyprofileSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data['username']
            user_id = serializer.data['user_id']
            email = serializer.data['email']
            u_icon = request.FILES.get("u_icon")

            user = LoginUser.objects.get(id=serializer.data['user_id'])
            user.username = username
            user.id = user_id
            user.email = email
            if u_icon:
                instance = user
                sender = user.u_icon
                loginuser_delete(sender, instance, **kwargs)
                user.u_icon = u_icon

            user.save()

            response = {
                'message': ['用户信息修改成功'],
                'code': ["200"]

            }

            return Response(response, status=200)
        return Response(serializer.errors)


class ChangeIcon(APIView):
    '''
    小程序更换头像
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ChangeIconSerializer,

    def post(self, request, *args, **kwargs):
        serializer = ChangeIconSerializer(data=request.data)
        if serializer.is_valid():
            u_icon = request.FILES.get("u_icon")
            user = LoginUser.objects.get(id=serializer.data['user_id'])
            if u_icon:
                instance = user
                sender = user.u_icon
                loginuser_delete(sender, instance, **kwargs)
                user.u_icon = u_icon

            user.save()
            response_data = {'code': ["200"], 'message': ['用户信息修改成功']}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


class SearchDevice(APIView):
    '''
    搜素机械设备
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = SearchDeviceSerializer

    def post(self, request, *args, **kwargs):
        serializer = SearchDeviceSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])
            project = user.project.all()
            projectlist = []
            for prrrr in project:
                project_id = prrrr.id
                projectlist.append(project_id)
            # print(projectlist)
            d_name = serializer.data['d_name']
            devices = []
            if user.u_type == '设备管理员':
                for project in projectlist:
                    device = Device.objects.filter(d_name__icontains=d_name, d_p_id=project)
                    if device:
                        devices = device | device  # 合并queryset
            if user.u_type == '公司管理员':
                devices = Device.objects.filter(d_name__icontains=d_name, d_co_id=user.u_company_id)
            if user.u_type in ['运维顾问', '客服运营', '超级管理员']:
                devices = Device.objects.all().order_by('d_co_id')
            if not devices:
                response_data = {
                    'message': ['您当前没有关联的设备'],
                    'code': ["963"]
                }
                return Response(response_data)
            b = []
            d = []
            for device in devices:
                subject = device.d_c_id.cd_name
                sub_id = device.d_c_id.id
                deviceattt = []
                deviceatts = Devicedata.objects.filter(ddd_d_id=device)
                if deviceatts:
                    for deviceatt in deviceatts:
                        att = {'name': '', 'detail': ''}
                        att["name"] = deviceatt.ddd_name
                        att['detail'] = deviceatt.ddd_detail
                        deviceattt.append(att)
                data = {"devicename": device.d_name, 'ID': device.id, 'd_GPS': device.d_GPS,
                        'd_manufacturer': device.d_manufacturer, 'd_status': device.d_status,
                        'd_produce_time': device.d_produce_time, 'Boolean': True, 'deviceatt': deviceattt}

                b.append(data)
                c = {'subject': subject, 'devices': b, 'collectdevice_id': sub_id}
            d.append(c)
            response_data = {'code': ["200"], 'data': d}
            return Response(response_data)
        return Response(serializer.errors)


class SearchDeviceV1(APIView):
    """
    搜素机械设备
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = SearchDeviceSerializerV1

    def post(self, request, *args, **kwargs):
        serializer = SearchDeviceSerializerV1(data=request.data)
        if serializer.is_valid():
            company_name = serializer.data['company_name']
            company = Company.objects.get(company_name=company_name, active=1).id
            d_name = serializer.data['d_name']
            devices = Device.objects.filter(d_name__icontains=d_name, d_co_id=company).order_by('d_co_id')
            if not devices:
                response_data = {
                    'message': ['机械设备不存在'],
                    'code': ["944"]
                }
                return Response(response_data)
            b = []
            d = []
            c = None
            for device in devices:
                subject = device.d_c_id.cd_name
                sub_id = device.d_c_id.id
                deviceattt = []
                deviceatts = Devicedata.objects.filter(ddd_d_id=device)
                if deviceatts:
                    for deviceatt in deviceatts:
                        att = {'name': '', 'detail': ''}
                        att["name"] = deviceatt.ddd_name
                        att['detail'] = deviceatt.ddd_detail
                        deviceattt.append(att)
                data = {"devicename": device.d_name, 'ID': device.id, 'd_GPS': device.d_GPS,
                        'd_manufacturer': device.d_manufacturer, 'd_status': device.d_status,
                        'd_produce_time': device.d_produce_time, 'Boolean': True, 'deviceatt': deviceattt}

                b.append(data)
                c = {'subject': subject, 'devices': b, 'collectdevice_id': sub_id}
            d.append(c)
            response_data = {'code': ["200"], 'data': d}
            return Response(response_data)
        return Response(serializer.errors)


# 用户修改密码
class Changepassword(GenericAPIView):
    '''
    更改用户密码
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ChangepasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = ChangepasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])
            user_id = serializer.data['user_id']
            newpassword = serializer.data['newpassword']
            user.password = make_password(newpassword)
            user.save()
            response = {
                'message': ['密码修改成功'],
                'code': ["200"]
            }
            return Response(response)
        return Response(serializer.errors)


#  忘记密码 修改密码
class ForgotPassword(GenericAPIView):
    """忘记密码 修改密码"""
    authentication_classes = []
    permission_classes = []
    serializer_class = ForgotPasswordSerializer  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = LoginUser.objects.get(phone_numbers=serializer.data['phone_number'])
            password = serializer.data['pass_word']
            user.password = make_password(password)
            user.save()
            response = {
                'message': ['用户修改密码成功'],
                'code': ["200"]
            }
            return Response(response)
        return Response(serializer.errors)


# 用户修改手机号
class ModifyPhoneNumber(GenericAPIView):
    """用户修改手机号"""
    authentication_classes = []
    permission_classes = []
    serializer_class = ModifyPhoneNumberSerializer  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = ModifyPhoneNumberSerializer(data=request.data)

        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])
            user.phone_numbers = serializer.data['phone_number']
            user.save()
            response = {
                'message': ['用户修改手机号成功'],
                'code': ["200"]
            }
            return Response(response)
        return Response(serializer.errors)


# 采用JWT的JSONWebTokenAuthentication认证时，访问Order视图时时，要加上请求头，请求头的键为：authorization，值为：jwt空格token
# 采用自定义认证Authtication时，访问Order时，要加上请求头，请求头键为：token,值为：获取到的token

# class WeChatLogin(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     queryset = Info.objects.filter(data_type='wx').all()
#     serializer_class = InfoSerializer

#     def create(self, request, *args, **kwargs):
#         code = request.data.get('code', '')

#         if not code:
#             return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

#         # 调用微信接口获取用户唯一标识
#         url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=" \
#               "authorization_code".format(settings.WE_CHAT['AppId'], settings.WE_CHAT['AppSecret'], code)
#         wx_response = requests.get(url)
#         if wx_response.status_code != 200:
#             return Response({'message': '微信调用失败'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

#         res_data = wx_response.json()
#         if not res_data.get('openid'):
#             return Response({'message': '微信调用失败'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

#         try:
#             user = Info.objects.get(username=res_data['openid'])
#         except Info.DoesNotExist:
#             user_info = request.data.get('userInfo', '')
#             wx_name = user_info['nickName']
#             sex = user_info['gender']
#             response_image_info = requests.get(user_info['avatarUrl'])
#             user = Info.objects.create(username=res_data['openid'], sex=sex, wx_name=wx_name, data_type='wx')
#             user.set_password(res_data['openid'])
#             if response_image_info.status_code == 200:
#                 img = response_image_info.content
#                 local_avatar_url = os.path.join('user', str(user.id) + '.png')
#                 avatar_path = os.path.join(settings.MEDIA_ROOT, local_avatar_url)
#                 with open(avatar_path, 'wb') as f:
#                     f.write(img)
#             else:
#                 local_avatar_url = user_info['avatarUrl']
#             user.avatar = local_avatar_url
#             user.save()

#         # 手动签发jwt
#         refresh = RefreshToken.for_user(user)
#         avatar_url = user.avatar if user.avatar.startswith('http') else request.build_absolute_uri(
#             settings.MEDIA_URL +
#             user.avatar)

#         resp_data = {
#             "user_id": user.id,
#             "username": user.wx_name,
#             "avatar": avatar_url,
#             "refresh": str(refresh),
#             'access': str(refresh.access_token)
#         }

#         return Response(resp_data)


# class CheckCode(GenericAPIView):
#     def post(self,request):
#         generate_image_id = request.data.get('generate_image_id',"")
#         data_code = cache.get(generate_image_id)
#         user_code = request.data.get('user_code',"")
#         if data_code and user_code:
#             print(data_code,user_code)
#             if data_code.lower() == user_code.lower():
#                 return Response({'code':200})
#         return Response({'code':201})


# def upload_user_icon(request):
#     if request.method == "GET":
#         return render(request, 'upload.html')
#     elif request.method == "POST":
#         icon = request.FILES.get("icon")
#         with open("static/uploadfiles/icon.jpg", 'wb+') as save_file:
#             for part in icon.chunks():
#                 save_file.write(part)
#                 save_file.flush()
#         return HttpResponse("upload file success")


# 公司CRUD
# 创建公司
# class Createcompany(GenericAPIView):
#     '''
#     创建公司
#     '''
#     authentication_classes = []
#     permission_classes = []
#     serializer_class = CreatecompanySerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = CreatecompanySerializer(data=request.data)
#         if serializer.is_valid():
#             user_id = serializer.data["user_id"]  # 获取创建1人ID
#             company_name = serializer.data['company_name']
#             company_address = serializer.data['company_address']
#             context = serializer.data['context']
#             company_icon = request.FILES.get("company_icon")
#
#             company = Company()
#             # users = LoginUser()
#             user = LoginUser.objects.get(id=user_id)
#             company.c_u_id = user
#             company.company_name = company_name
#             company.company_address = company_address
#             company.context = context
#             company.company_icon = company_icon
#
#             company.save()
#
#             user.u_company_id = company.id  # 添加公司id到用户表
#             user.is_staff = 1
#
#             user.u_type = "公司管理员"
#             user.save()
#             response = {
#                 'message': ['公司创建成功，等待平台审核。'],
#                 # 'token':token
#                 'code': ["200"]
#             }
#
#             return Response(response, status=200)
#         return Response(serializer.errors)
# 创建公司
class Createcompany(GenericAPIView):
    '''
    创建公司
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = CreatecompanySerializer

    def post(self, request, *args, **kwargs):
        serializer = CreatecompanySerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.POST.get("user_id")  # 获取创建1人ID
            company_name = serializer.data['company_name']
            company_address = serializer.data['company_address']
            company_mailbox = serializer.data['company_mailbox']
            company_zip_code = serializer.data['company_zip_code']
            company_content = serializer.data['company_content']
            company_icon = request.FILES.get("company_icon")
            company_register_number = serializer.data['company_register_number']
            company_license = request.FILES.get('company_license')
            company_begin_date = serializer.data["company_begin_date"]
            company_office_number = serializer.data["company_office_number"]
            # company_boss_ID_card = request.FILES.get("company_boss_ID_card")
            company_business_range = serializer.data["company_business_range"]
            company_register_money = serializer.data["company_register_money"]
            # company_organize_code = serializer.data["company_organize_code"]

            company = Company()
            # users = LoginUser()
            user = LoginUser.objects.get(id=user_id)
            company.c_u_id = user  # 外键指向的是一个对象 不是属性
            company.company_name = company_name
            company.company_mailbox = company_mailbox
            company.company_address = company_address
            company.company_zip_code = company_zip_code
            company.company_content = company_content
            company.company_register_number = company_register_number
            company.company_license = company_license
            company.company_icon = company_icon
            company.company_begin_date = company_begin_date
            company.company_office_number = company_office_number
            # company.company_boss_ID_card = company_boss_ID_card
            company.company_business_range = company_business_range
            company.company_register_money = company_register_money
            # company.company_organize_code = company_organize_code
            company.active = 0
            company.draft = 0
            company.save()

            user.u_company_id = company.id  # 添加公司id到用户表
            user.is_staff = 1
            user.u_type = "公司管理员"
            user.save()
            response = {
                'message': ['公司创建成功，等待平台审核。'],
                # 'token':token
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


class CreateDraftcompany(GenericAPIView):
    '''
    创建公司
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = CreatecompanySerializer

    def post(self, request, *args, **kwargs):
        serializer = CreatecompanySerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.POST.get("user_id")  # 获取创建1人ID
            company_name = serializer.data['company_name']
            company_address = serializer.data['company_address']
            company_mailbox = serializer.data['company_mailbox']
            company_zip_code = serializer.data['company_zip_code']
            company_content = serializer.data['company_content']
            company_icon = request.FILES.get("company_icon")
            company_register_number = serializer.data['company_register_number']
            company_license = request.FILES.get('company_license')
            company_begin_date = serializer.data["company_begin_date"]
            company_office_number = serializer.data["company_office_number"]
            company_boss_ID_card = request.FILES.get("company_boss_ID_card")
            company_business_range = serializer.data["company_business_range"]
            company_register_money = serializer.data["company_register_money"]
            # company_organize_code = serializer.data["company_organize_code"]

            company = Company()
            # users = LoginUser()
            user = LoginUser.objects.get(id=user_id)
            company.c_u_id = user  # 外键指向的是一个对象 不是属性
            company.company_name = company_name
            company.company_mailbox = company_mailbox
            company.company_address = company_address
            company.company_zip_code = company_zip_code
            company.company_content = company_content
            company.company_register_number = company_register_number
            company.company_license = company_license
            company.company_icon = company_icon
            company.company_begin_date = company_begin_date
            company.company_office_number = company_office_number
            company.company_boss_ID_card = company_boss_ID_card
            company.company_business_range = company_business_range
            company.company_register_money = company_register_money
            # company.company_organize_code = company_organize_code
            company.active = 0
            company.draft = 1
            company.save()

            user.u_company_id = company.id  # 添加公司id到用户表
            user.is_staff = 1
            user.u_type = "公司管理员"
            user.save()
            response = {
                'message': ['公司创建成功，等待平台审核。'],
                # 'token':token
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


# 点击查看其他公司详情
class Companyprofile(GenericAPIView):
    '''
    点击查看其他公司详情
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        company_id = request.GET.get("company_id")
        # print(company_id)
        objJson = serialize("json", Company.objects.filter(id=company_id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))


# 查看自己所属的公司&&编辑公司信息
# class Editcompany(GenericAPIView):
#     '''
#     查看自己所属的公司&&编辑公司信息，需要公司管理员身份
#     '''
#     authentication_classes = []
#     permission_classes = []
#     serializer_class = EditcompanySerializer
#
#     def get(self, request, *args, **kwargs):
#         company_id = request.GET.get("company_id")
#         company = Company.objects.filter(id=company_id).filter(active=1)
#         if not company:
#             response = {
#                 'message': ['公司待审核或已被平台停用'],
#                 # 'token':token
#                 'code': ["998"]
#             }
#
#             return Response(response, status=200)
#
#         objJson = serialize("json", Company.objects.filter(id=company_id))
#         objStr = json.loads(objJson)
#         response_data = {'code': ["200"], 'data': objStr}
#         return HttpResponse(json.dumps(response_data))
#
#     def post(self, request, *args, **kwargs):
#
#         serializer = EditcompanySerializer(data=request.data)
#         if serializer.is_valid():
#             company_name = serializer.data['company_name']
#             company_address = serializer.data['company_address']
#             context = serializer.data['context']
#             company_icon = request.FILES.get("company_icon")
#
#             company = Company.objects.get(id=serializer.data['company_id'])
#             company.company_name = company_name
#             company.company_address = company_address
#             company.context = context
#             if company_icon:
#                 company.company_icon = company_icon
#
#             company.save()
#
#             response = {
#                 'message': ['公司信息修改成功'],
#                 'code': ["200"]
#             }
#
#             return Response(response, status=200)
#         return Response(serializer.errors)
# 查看自己所属的公司&&编辑公司信息
class Editcompany(GenericAPIView):
    '''
    查看自己所属的公司&&编辑公司信息，需要公司管理员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditcompanySerializer

    def get(self, request, *args, **kwargs):
        company_id = request.GET.get("company_id")
        company = Company.objects.filter(id=company_id).filter(active=1)
        if not company:
            response = {
                'message': ['公司待审核或已被平台停用'],
                # 'token':token
                'code': ["998"]
            }

            return Response(response, status=200)

        objJson = serialize("json", Company.objects.filter(id=company_id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))

    def post(self, request, *args, **kwargs):

        serializer = EditcompanySerializer(data=request.data)
        if serializer.is_valid():
            company = Company.objects.get(id=serializer.data['company_id'])
            company_name = serializer.data['company_name']
            company_address = serializer.data['company_address']
            company_mailbox = serializer.data['company_mailbox']
            company_zip_code = serializer.data['company_zip_code']
            company_content = serializer.data['company_content']
            if request.FILES.get("company_icon"):
                company_icon = request.FILES.get("company_icon")
                company.active = 0
            company_register_number = serializer.data['company_register_number']
            if request.FILES.get('company_license'):
                company_license = request.FILES.get('company_license')
                company.active = 0
            company_begin_date = serializer.data["company_begin_date"]
            company_office_number = serializer.data["company_office_number"]
            # if request.FILES.get("company_boss_ID_card"):
            #     company_boss_ID_card = request.FILES.get("company_boss_ID_card")
            #     company.active = 0
            company_business_range = serializer.data["company_business_range"]
            company_register_money = serializer.data["company_register_money"]
            # company_organize_code = serializer.data["company_organize_code"]

            if company_name != company.company_name or company_address != company.company_address or company_office_number != company.company_office_number:
                company.active = 0
            company.company_name = company_name
            company.company_mailbox = company_mailbox
            company.company_address = company_address
            company.company_zip_code = company_zip_code
            if company_content:
                company.company_content = company_content
            company.company_register_number = company_register_number
            if request.FILES.get('company_license'):
                company.company_license = company_license
            if request.FILES.get('company_icon'):
                company.company_icon = company_icon
            company.company_begin_date = company_begin_date
            company.company_office_number = company_office_number
            # if request.FILES.get('company_boss_ID_card'):
            #     company.company_boss_ID_card = company_boss_ID_card
            if company_business_range:
                company.company_business_range = company_business_range
            if company_register_money:
                company.company_register_money = company_register_money

            # company.active = 0

            company.save()

            response = {
                'message': ['公司信息修改成功'],
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


class EditDraftcompany(GenericAPIView):
    '''
    查看自己所属的公司&&编辑公司信息，需要公司管理员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditcompanySerializer

    def get(self, request, *args, **kwargs):
        company_id = request.GET.get("company_id")
        company = Company.objects.filter(id=company_id).filter(active=1)
        if not company:
            response = {
                'message': ['公司待审核或已被平台停用'],
                # 'token':token
                'code': ["998"]
            }

            return Response(response, status=200)

        objJson = serialize("json", Company.objects.filter(id=company_id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))

    def post(self, request, *args, **kwargs):

        serializer = EditcompanySerializer(data=request.data)
        if serializer.is_valid():
            company = Company.objects.get(id=serializer.data['company_id'])
            company_name = serializer.data['company_name']
            company_address = serializer.data['company_address']
            company_mailbox = serializer.data['company_mailbox']
            company_zip_code = serializer.data['company_zip_code']
            company_content = serializer.data['company_content']
            if request.FILES.get("company_icon"):
                company_icon = request.FILES.get("company_icon")
                company.active = 0
            company_register_number = serializer.data['company_register_number']
            if request.FILES.get('company_license'):
                company_license = request.FILES.get('company_license')
                company.active = 0
            company_begin_date = serializer.data["company_begin_date"]
            company_office_number = serializer.data["company_office_number"]
            # if request.FILES.get("company_boss_ID_card"):
            #     company_boss_ID_card = request.FILES.get("company_boss_ID_card")
            #     company.active = 0
            company_business_range = serializer.data["company_business_range"]
            company_register_money = serializer.data["company_register_money"]
            # company_organize_code = serializer.data["company_organize_code"]

            if company_name != company.company_name or company_address != company.company_address or company_office_number != company.company_office_number:
                company.active = 0
            company.company_name = company_name
            company.company_mailbox = company_mailbox
            company.company_address = company_address
            company.company_zip_code = company_zip_code
            if company_content:
                company.company_content = company_content
            company.company_register_number = company_register_number
            if request.FILES.get('company_license'):
                company.company_license = company_license
            if request.FILES.get('company_icon'):
                company.company_icon = company_icon
            company.company_begin_date = company_begin_date
            company.company_office_number = company_office_number
            # if request.FILES.get('company_boss_ID_card'):
            #     company.company_boss_ID_card = company_boss_ID_card
            if company_business_range:
                company.company_business_range = company_business_range
            if company_register_money:
                company.company_register_money = company_register_money

            # company.active = 0

            company.save()

            response = {
                'message': ['公司信息修改成功'],
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


# 停用公司，公司管理员
class Deactivatecompany(GenericAPIView):
    """
    停用公司，需要公司管理员身份或后台人员身份
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = DeactivatecompanySerializer

    def post(self, request, *args, **kwargs):
        serializer = DeactivatecompanySerializer(data=request.data)
        if serializer.is_valid():
            company = Company.objects.get(id=serializer.data['company_id'])
            company.active = 0
            # delprojects(serializer.data['company_id'])
            company.save()

            response = {
                'message': ['公司及所有项目设备停用成功'],
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 通过公司名字搜索公司
class SelectCompany(GenericAPIView):
    """
    通过公司名字搜索公司
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = SelectCompanySerializer  # 权限要求相同

    #
    # def post(self, request, *args, **kwargs):
    #     serializer = SelectCompanySerializer(data=request.data)
    #     if serializer.is_valid():
    #         company = Company.objects.get(company_name=serializer.data['company_name'])
    #         company_name = company.company_name
    #         company_address = company.company_address
    #         company_active = company.active

    def get(self, request, *args, **kwargs):
        company_name = request.GET.get("company_name")
        company = Company.objects.filter(company_name=company_name)
        if not company:
            response = {
                'message': ['公司不存在或已被平台停用'],
                # 'token':token
                'code': ["998"]
            }
            return Response(response, status=200)

        objJson = serialize("json", Company.objects.filter(company_name=company_name))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))


# 员工与公司 CRUD
# 加入公司成为员工
class Joincompany(GenericAPIView):
    '''
    加入公司成为员工
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = JoincompanySerializer

    def post(self, request, *args, **kwargs):
        serializer = JoincompanySerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['user_id']
            user = LoginUser.objects.get(id=user_id)
            user.u_company_id = serializer.data['company_id']  # LoginUser is_staff 为0
            print(user.u_company_id)
            user.save()
            response = {
                'message': ['已提交申请，等待公司管理员审核。'],
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


# 查看新员工申请，需公司管理员操作
class Unactivestafflist(GenericAPIView):
    '''
    查看新员工申请，需公司管理员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = CompanystaffSerializer

    def post(self, request, *args, **kwargs):
        serializer = CompanystaffSerializer(data=request.data)
        if serializer.is_valid():
            objJson = serialize("json",
                                LoginUser.objects.filter(u_company_id=serializer.data['company_id']).filter(is_staff=0))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# 添加用户为员工
class Enrollstaff(GenericAPIView):
    '''
    添加用户为员工，需公司管理员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EnrollstaffSerializer

    def post(self, request, *args, **kwargs):
        serializer = EnrollstaffSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])
            user.is_staff = 1
            user.u_type = "员工"
            company_id = serializer.data['company_id']
            usercount = LoginUser.objects.filter(u_company_id=company_id).count()
            print(usercount)
            user.company_number = usercount + 1
            user.save()
            response = {
                'message': ['添加成功'],
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


# 停用员工
class Deactivatestaff(GenericAPIView):
    '''
    停用员工，需公司管理员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DeactivatestaffSerializer

    def post(self, request, *args, **kwargs):
        serializer = DeactivatestaffSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])
            if user.is_staff == 0:
                response0 = {
                    'message': ['该用户不是员工'],
                    'code': [301]
                }
                return Response(response0, status=200)
            user.is_staff = 0  # 此时用户处于停用状态，但仍属于该公司
            user.u_company_id = None
            user.save()
            response = {
                'message': ['停用成功'],
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


# 查看公司员工
class Companystaff(GenericAPIView):
    '''
    查看公司员工
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = CompanystaffSerializer

    def post(self, request, *args, **kwargs):
        serializer = CompanystaffSerializer(data=request.data)

        if serializer.is_valid():
            userid = serializer.data['user_id']
            user = LoginUser.objects.get(id=userid)
            user_type = user.u_type
            if user_type == "公司管理员":
                objJson = serialize("json",
                                    LoginUser.objects.filter(u_company_id=serializer.data['company_id']).filter(
                                        is_staff=1))
                objStr = json.loads(objJson)
                response_data = {'code': ["200"], 'data': objStr}
                return HttpResponse(json.dumps(response_data))
            response = {
                'message': ['您无权进行此操作'],
                'code': ["996"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 管理员创建员工
class ManagerCreateStaff(GenericAPIView):
    """
    管理员创建员工
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = ManagerCreateStaffSerializer  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = ManagerCreateStaffSerializer(data=request.data)
        if serializer.is_valid():
            manager = LoginUser.objects.get(id=serializer.data['user_id'])
            company_id = manager.u_company_id
            user = LoginUser()  # 创建员工对象
            user.is_staff = 1
            #            user.id = serializer.data['staff_id']
            user.phone_numbers = serializer.data['staff_phone']
            user.username = serializer.data['staff_name']
            password = serializer.data['staff_password']
            user.password = make_password(password)
            user.u_company_id = manager.u_company_id
            user.work = serializer.data["staff_work"]
            user.email = serializer.data["staff_email"]

            usercount = LoginUser.objects.filter(u_company_id=company_id).count()
            print(usercount)
            user.company_number = usercount + 1
            user.save()
            response = {
                'message': ['添加员工成功'],
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


# 管理员修改员工信息
class MCSwork(GenericAPIView):
    """
    管理员修改员工信息
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = MCSworkSerializer  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = MCSworkSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data["staff_id"])  # 创建员工对象
            user.work = serializer.data["staff_work"]

            user.save()
            response = {
                'message': ['修改员工职务成功'],
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


# 管理员创建员工
class ManagerCreateStaffv2(GenericAPIView):
    """
    超级管理员创建后台员工
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = ManagerCreateStaffSerializerv2  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = ManagerCreateStaffSerializerv2(data=request.data)
        if serializer.is_valid():
            manager = LoginUser.objects.get(id=serializer.data['user_id'])
            user = LoginUser()  # 创建员工对象
            # user.is_staff = 1
            # user.is_active = 1
            #            user.id = serializer.data['staff_id']
            user.phone_numbers = serializer.data['staff_phone']
            user.username = serializer.data['staff_name']
            password = serializer.data['staff_password']
            user.u_type = serializer.data['u_type']
            user.password = make_password(password)
            user.u_company_id = manager.u_company_id
            user.save()
            response = {
                'message': ['添加员工成功'],
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


# 超级管理员创建公司管理员
class ManagerCreateStaffV3(GenericAPIView):
    """
    超级管理员创建公司管理员
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = ManagerCreateStaffSerializerv3  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = ManagerCreateStaffSerializerv3(data=request.data)
        if serializer.is_valid():
            # manager = LoginUser.objects.get(id=serializer.data['user_id'])
            user = LoginUser()  # 创建员工对象
            user.is_staff = 0
            user.u_type = '待分配'
            #            user.id = serializer.data['staff_id']
            user.phone_numbers = serializer.data['staff_phone']
            user.username = serializer.data['staff_name']
            password = serializer.data['staff_password']
            user.password = make_password(password)
            # user.u_company_id = manager.u_company_id
            user.save()
            response = {
                'message': ['添加用户成功'],
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


class Editstaff(GenericAPIView):
    """
    超级管理员修改后台员工，GET 员工id： user_id
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = EditstaffSerializer  # 权限要求相同

    def get(self, request, *args, **kwargs):
        id = request.GET.get("user_id")
        user = LoginUser.objects.filter(id=id)
        if not user:
            response = {
                'message': ['用户不存在或已停用'],
                # 'token':token
                'code': ["999"]
            }
            return Response(response, status=200)

        objJson = serialize("json", LoginUser.objects.filter(id=id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))

    def post(self, request, *args, **kwargs):
        serializer = EditstaffSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id1'])
            # user.is_staff = 1
            # user.is_active = 1
            #            user.id = serializer.data['staff_id']
            user.phone_numbers = serializer.data['staff_phone']
            user.username = serializer.data['staff_name']
            password = serializer.data['staff_password']
            user.u_type = serializer.data['u_type']
            user.password = make_password(password)
            user.save()
            response = {
                'message': ['编辑员工成功'],
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


# 管理员创建员工
class Staffcategory(GenericAPIView):
    """
    超级管理员创建后台员工, type:  客服，运维，运营
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = []  # 权限要求相同

    def get(self, request, *args, **kwargs):
        type = request.GET.get('type')

        objJson = serialize("json", LoginUser.objects.filter(u_type=type))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))


# 停用后台员工
class DeactivateStaffv2(GenericAPIView):
    '''
    停用后台员工，需要admin操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DeactivatestaffSerializerv2

    def post(self, request, *args, **kwargs):
        serializer = DeactivatestaffSerializerv2(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])
            user.is_active = 0  # 后台人员被停用
            user.save()
            response = {
                'message': ['停用成功'],
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


# 项目与公司 CRUD
# 创建项目，需公司管理员操作
class Createproject(GenericAPIView):
    '''
    创建项目，需公司管理员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = CreateprojectSerializer

    def post(self, request, *args, **kwargs):
        serializer = CreateprojectSerializer(data=request.data)
        if serializer.is_valid():
            p_u_id = serializer.data['user_id']  # 获取创建人ID
            p_c_id = serializer.data['company_id']

            project = Project()
            # users = LoginUser()
            user = LoginUser.objects.get(id=p_u_id)
            company = Company.objects.get(id=p_c_id)
            project.p_active = 1
            project.p_u_id = user
            project.p_c_id = company
            project.p_name = serializer.data['p_name']
            project.p_description = serializer.data['p_description']
            # project.p_type = serializer.data['p_type']
            project.p_customer_type = serializer.data['p_customer_type']
            project.p_party_a = serializer.data['p_party_a']
            project.p_purchase_time = serializer.data['p_purchase_time']
            project.p_setup_time = serializer.data['p_setup_time']
            project.p_built_time = serializer.data['p_built_time']
            project.p_contact_name = serializer.data['p_contact_name']
            project.p_contact_number = serializer.data['p_contact_number']
            # project.p_province = serializer.data['p_province']
            # project.p_city = serializer.data['p_city']
            project.p_c_address = serializer.data['p_c_address']
            project.p_address = serializer.data['p_address']
            project.p_dashboard = serializer.data['p_dashboard']
            project.p_position = serializer.data['p_position']
            project.p_register_time = datetime.datetime.now()
            # project.p_longitude = serializer.data['p_longitude']
            # project.p_latitude = serializer.data['p_latitude']

            project.save()
            company_id = project.p_c_id_id
            project_id = project.id
            response = {
                'message': ['项目创建成功，等待平台审核。'],
                # 'token':token
                'code': ["200"],
                'company_id': company_id,
                'project_id': project_id

            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Projectlist(GenericAPIView):
    '''
    查看项目列表, GET user_id, company_id
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        company_id = request.GET.get("company_id")
        user_id = request.GET.get("user_id")
        company = Company.objects.filter(id=company_id).filter(active=1)
        if not company:
            response = {
                'message': ['公司不存在或已被平台停用'],
                'code': ["998"]
            }
            return Response(response, status=200)
        user = LoginUser.objects.filter(id=user_id).filter(is_active=1)
        if not user:
            response = {
                'message': ['用户不存在或已停用'],
                'code': ["999"]
            }
            return Response(response, status=200)
        user = LoginUser.objects.get(id=user_id)
        # if LoginUser.objects.filter(id=user_id).filter(u_company_id=company_id).filter(u_type='公司管理员'):
        user_type = user.u_type
        u_type = ['运维', '公司管理员', '客服', '运营', '超级管理员']
        if user.u_type in u_type:
            # print(u_type)
            objJson = serialize("json", Project.objects.filter(p_c_id=company_id).filter(p_active=1))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        if LoginUser.objects.filter(id=user_id).filter(is_active=1):  # 改
            # objJson = serialize("json", Project.objects.filter(p_c_id=company_id).filter(p_active=1))
            objJson = serialize("json", user.project.all().filter(p_active=1))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))


# 查看项目信息
class Viewproject(GenericAPIView):
    '''
    查看项目信息，需要公司员工或公司管理员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ViewprojectSerializer

    def post(self, request, *args, **kwargs):
        serializer = ViewprojectSerializer(data=request.data)
        if serializer.is_valid():
            project_id = serializer.data['project_id']
            p = Project.objects.get(id=project_id)
            data = []
            collectdevices = Collectdevice.objects.filter(cd_p_id=p)
            dict = {"Name": '无设备'}
            for device in collectdevices:
                name = device.cd_name
                dict["Name"] = name
                data.append(dict)

            objJson = serialize("json", Project.objects.filter(id=project_id))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr, 'cdnames': data}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# 修改项目信息
class Editproject(GenericAPIView):
    '''
    修改项目信息，需公司管理员或后台人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditprojectSerializer

    def post(self, request, *args, **kwargs):
        serializer = EditprojectSerializer(data=request.data)
        if serializer.is_valid():
            project_id = serializer.data['project_id']

            project = Project.objects.get(id=project_id)

            project.p_name = serializer.data['p_name']
            project.p_description = serializer.data['p_description']
            # project.p_type = serializer.data['p_type']
            project.p_customer_type = serializer.data['p_customer_type']
            project.p_party_a = serializer.data['p_party_a']
            project.p_purchase_time = serializer.data['p_purchase_time']
            project.p_setup_time = serializer.data['p_setup_time']
            project.p_built_time = serializer.data['p_built_time']
            project.p_contact_name = serializer.data['p_contact_name']
            project.p_contact_number = serializer.data['p_contact_number']
            # project.p_province = serializer.data['p_province']
            # project.p_city = serializer.data['p_city']
            project.p_c_address = serializer.data['p_c_address']
            project.p_position = serializer.data['p_position']
            project.p_address = serializer.data['p_address']
            project.p_dashboard = serializer.data['p_dashboard']
            project.save()

            response = {
                'message': ['修改成功'],
                # 'token':token
                'code': ["200"]

            }

            return Response(response, 200)
        return Response(serializer.errors)


# 删除项目
class Deactivateproject(GenericAPIView):
    '''
    删除项目，需公司管理员或后台人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DelprojectSerializer

    def post(self, request, *args, **kwargs):
        serializer = DelprojectSerializer(data=request.data)
        if serializer.is_valid():
            project = Project.objects.get(id=serializer.data['project_id'])
            project.p_active = 0
            deldevice(project.id)
            project.save()

            response = {
                'message': ['项目及其设备停用成功'],
                # 'token':token
                'code': ["200"]
            }

            return Response(response, 200)
        return Response(serializer.errors)


class Signproject(GenericAPIView):
    '''
    关联用户和项目，需要公司管理员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = SignprojectSerializer

    def post(self, request, *args, **kwargs):
        serializer = SignprojectSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['p_o_id']  # 获取被指定员工ID
            id = serializer.data['project_id']  # 获取项目ID

            user = LoginUser.objects.get(id=user_id)
            user.project.add(Project.objects.get(id=id))
            project = Project.objects.get(id=id)
            collectdevice = Collectdevice.objects.filter(cd_p_id_id=project.id)
            if not collectdevice:
                if not LoginUser.objects.filter(id=user_id).filter(
                        Q(u_type='公司管理员') | Q(u_type='运营') | Q(u_type='运维顾问') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                    user.u_type = '设备管理员'
                    user.save()
                user.save()
                response = {
                    'message': ['关联成功。'],
                    # 'token':token
                    'code': ["200"]
                }
                return Response(response, status=200)
            # collectdevice = Collectdevice.objects.get(cd_p_id_id=project.id)
            for c in collectdevice:
                user.collectdevice.add(c)
            if not LoginUser.objects.filter(id=user_id).filter(
                    Q(u_type='公司管理员') | Q(u_type='运营') | Q(u_type='运维顾问') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                user.u_type = '设备管理员'
                user.save()
            user.save()
            response = {
                'message': ['关联成功。'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Responserlist(GenericAPIView):
    '''
    查看项目关联用户列表，需要公司管理员或后台人员身份, 项目id：project_id 用户id: user_id
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = SignprojectSerializerv2

    def post(self, request, *args, **kwargs):
        serializer = SignprojectSerializerv2(data=request.data)
        if serializer.is_valid():
            project_id = serializer.data['project_id']
            user_id = serializer.data['user_id']
            project = Project.objects.get(id=project_id)
            user = LoginUser.objects.get(id=user_id)
            u_type = ['员工', '公司管理员', '设备管理员']
            if user.u_type in u_type:
                objJson = serialize("json", project.loginuser_set.filter(u_type='设备管理员'))
                objStr = json.loads(objJson)
                response_data = {'code': ["200"], 'data': objStr}
                return HttpResponse(json.dumps(response_data))
            objJson = serialize("json",
                                project.loginuser_set.filter(Q(u_type='运维顾问') | Q(u_type='运营') | Q(u_type='客服运营')))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


class Unsignproject(GenericAPIView):
    '''
    取消用户与项目关联，需要公司管理员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = SignprojectSerializer

    def post(self, request, *args, **kwargs):
        serializer = SignprojectSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['p_o_id']  # 员工ID
            id = serializer.data['project_id']  # 项目ID

            user = LoginUser.objects.get(id=user_id)
            user.project.remove(Project.objects.get(id=id))

            project = Project.objects.get(id=id)
            collectdevice = Collectdevice.objects.filter(cd_p_id_id=project.id)
            if not collectdevice:
                if not user.project.all():
                    if not LoginUser.objects.filter(id=user_id).filter(
                            Q(u_type='运营') | Q(u_type='运维顾问') | Q(u_type='客服运营') | Q(u_type='超级管理员') | Q(
                                u_type='公司管理员')):
                        user.u_type = '员工'
                        user.save()
                user.save()
                response = {
                    'message': ['取消关联成功。'],
                    # 'token':token
                    'code': ["200"]
                }
                return Response(response, status=200)
            collectdevice = Collectdevice.objects.get(cd_p_id_id=project.id)
            user.collectdevice.remove(Collectdevice.objects.get(id=collectdevice.id))
            # user.u_type = '员工'
            if not user.project.all():
                if not LoginUser.objects.filter(id=user_id).filter(
                        Q(u_type='运营') | Q(u_type='运维顾问') | Q(u_type='客服运营') | Q(u_type='超级管理员') | Q(u_type='公司管理员')):
                    user.u_type = '员工'
                    user.save()
            user.save()
            response = {
                'message': ['取消关联成功。'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Collectdeviceattlistv3(GenericAPIView):
    '''
    设备管理员查看我的设备列表,拼接访问url
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = Collectdeviceattlistv3Serializer

    def post(self, request, *args, **kwargs):
        serializer = Collectdeviceattlistv3Serializer(data=request.data)
        if serializer.is_valid():
            userid = serializer.data['user_id']
            company_id = serializer.data['company_id']
            user = LoginUser.objects.get(id=userid)
            # wisepasstoken()
            if user.u_type == "公司管理员":
                company = Company.objects.get(id=company_id)
                collectdevices = Collectdevice.objects.filter(cd_c_id=company)

                # print(collectdevices)
                url = 'https://portal-apm-user1-eks004.hz.wise-paas.com.cn/api-apm/topo/node?nodeIds='
                # for collectdevice in collectdevices:
                #     nodeid = collectdevice.cd_nodeid
                #     nodeid = str(nodeid)
                #     url = url + nodeid + ','
                # url = url[:-1]
                # print(url)
                response = {
                    'message': ['设备查询成功。'],
                    # 'token':token
                    'code': ["200"],
                    'url': [url]
                }
                return Response(response, status=200)
            collectdevices = Collectdevice.objects.filter(loginuser=user)
            if not collectdevices:
                url = 'https://portal-apm-user1-eks004.hz.wise-paas.com.cn/api-apm/topo/node?nodeIds='

                response = {
                    'message': ['您当前没有关联的设备。'],
                    # 'token':token
                    'code': ["964"],
                    'url': [url]
                }
                return Response(response, status=200)

            # print(collectdevices)
            url = 'https://portal-apm-user1-eks004.hz.wise-paas.com.cn/api-apm/topo/node?nodeIds='

            # for collectdevice in collectdevices:
            #     nodeid = collectdevice.cd_nodeid
            #     nodeid = str(nodeid)
            #     url = url + nodeid + ','
            # url = url[:-1]
            # # print(url)
            token = 'cao'
            response = {
                'message': ['设备查询成功。'],
                # 'token':token
                'code': ["200"],
                'url': [url],
                'token': [token]
            }
            return Response(response, status=200)

        return Response(serializer.errors)


class Devicelistv2(GenericAPIView):
    '''
    设备管理员查看采集设备下数据信息,拼接访问url
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        nodeid = request.GET.get('id')
        url = str(nodeid)
        url = 'https://portal-apm-user1-eks004.hz.wise-paas.com.cn/api-apm/latest/data?nodeId=' + url
        response = {
            'message': ['查询成功。'],
            # 'token':token
            'code': ["200"],
            'url': [url]
        }
        return Response(response, status=200)


class Dashboardv2(GenericAPIView):
    '''
    设备管理员查看采集设备下数据信息,拼接访问url
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):

        nodeid = request.GET.get('id')
        collectdevice = Collectdevice.objects.filter(cd_nodeid=nodeid)
        if not collectdevice:
            response = {
                'message': ['采集设备不存在或已被平台停用。'],
                # 'token':token
                'code': ["969"]
            }
            return Response(response, status=200)
        collectdevice = Collectdevice.objects.get(cd_nodeid=nodeid)
        project = collectdevice.cd_p_id
        url = project.p_dashboard
        if not url:
            response = {
                'message': ['当前没有组态画面。'],
                # 'token':token
                'code': ["962"]
            }
            return Response(response, status=200)
        response = {
            'message': ['查询成功。'],
            # 'token':token
            'code': ["200"],
            'dashboardurl': [url]
        }
        return Response(response, status=200)


class Applycollectdevice(GenericAPIView):
    '''
    添加采集设备信息，需公司管理员或运维人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ApplycollectdeviceSerializer

    def post(self, request, *args, **kwargs):
        serializer = ApplycollectdeviceSerializer(data=request.data)
        if serializer.is_valid():
            d_m_id = serializer.data['user_id']  # 获取创建人ID
            # cd_p_id = serializer.data['project_id']
            # cd_c_id = serializer.data['company_id']
            # print(cd_c_id)

            device = Collectdevice.objects.get(cd_name=serializer.data['cd_name'])
            user = LoginUser.objects.get(id=d_m_id)
            # project = Project.objects.get(id=cd_p_id)
            # company = Company.objects.get(id=cd_c_id)
            # device.cd_p_id = project
            device.cd_m_id = user
            # device.cd_c_id = company

            device.cd_produce_time = serializer.data['cd_produce_time']
            device.cd_manufacturer = serializer.data['cd_manufacturer']
            device.cd_install_time = serializer.data['cd_install_time']
            device.cd_SN = serializer.data['cd_SN']
            device.cd_SIM = serializer.data['cd_SIM']
            device.cd_GPS = serializer.data['cd_GPS']
            device.cd_placed = serializer.data['cd_placed']

            device.save()

            response = {
                'message': ['设备创建成功。'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Collectdevicelist(GenericAPIView):
    '''
    查看采集设备信息列表，需公司管理员或运维人员操作,查看功能需要提供用户Id: user_id 项目Id: project_id
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get("user_id")
        project_id = request.GET.get("project_id")

        if not LoginUser.objects.filter(id=user_id).filter(is_active=1):
            response = {
                'message': ['用户不存在或已停用'],
                # 'token':token
                'code': ["999"]
            }
            return Response(response, status=200)

        if not LoginUser.objects.filter(id=user_id).filter(
                Q(u_type='公司管理员') | Q(u_type='设备管理员')):  # 如果用户不是公司管理员或设备管理员，需要他拥有后台人员身份
            if not LoginUser.objects.filter(id=user_id).filter(
                    Q(u_type='运营') | Q(u_type='运维顾问') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                response = {
                    'message': ['您无权进行此操作'],
                    # 'token':token
                    'code': ["996"]
                }
                return Response(response, status=200)

        # page = int(request.GET.get("page"))  # 第几页
        # per_page = int(request.GET.get("per_page", 10))  # 每页多少条

        devices = Collectdevice.objects.filter(cd_p_id_id=project_id)
        # paginator = Paginator(devices, per_page)

        # total_page = paginator.num_pages
        # total_data = paginator.count

        # page_object = paginator.page(page)
        objJson = serialize("json", devices)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr}

        return HttpResponse(json.dumps(response_data))


class Collectdevicelistv2(GenericAPIView):
    '''
    查看公司采集设备列表，需公司管理员或运维人员操作,查看功能需要提供用户Id: user_id 公司Id: company_id
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get("user_id")
        company_id = request.GET.get("company_id")
        print(company_id)
        if not LoginUser.objects.filter(id=user_id).filter(is_active=1):
            response = {
                'message': ['用户不存在或已停用'],
                # 'token':token
                'code': ["999"]
            }
            return Response(response, status=200)

        if not LoginUser.objects.filter(id=user_id).filter(
                Q(u_type='公司管理员') | Q(u_type='设备管理员')):  # 如果用户不是公司管理员或设备管理员，需要他拥有后台人员身份
            if not LoginUser.objects.filter(id=user_id).filter(
                    Q(u_type='运营') | Q(u_type='运维顾问') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                response = {
                    'message': ['您无权进行此操作'],
                    # 'token':token
                    'code': ["996"]
                }
                return Response(response, status=200)

        # page = int(request.GET.get("page"))  # 第几页
        # per_page = int(request.GET.get("per_page", 10))  # 每页多少条
        company = Company.objects.get(id=company_id)
        collectdevices = Collectdevice.objects.filter(cd_c_id=company)
        print(collectdevices)
        url = 'https://portal-apm-user1-eks004.hz.wise-paas.com.cn/api-apm/topo/node?nodeIds='
        for collectdevice in collectdevices:
            nodeid = collectdevice.cd_nodeid
            nodeid = str(nodeid)
            url = url + nodeid + ','
        url = url[:-1]
        print(url)
        response = {
            'message': ['设备查询成功。'],
            # 'token':token
            'code': ["200"],
            'url': [url]
        }
        return Response(response, status=200)


class Editcollectdevice(GenericAPIView):
    '''
    查看&修改采集设备信息，需公司管理员或运维人员操作, 查看功能需要提供用户Id: user_id 采集设备Id: collectdevice_id，查看时有选择的展示采集设备信息
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditcollectdeviceSerializer

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get("user_id")
        collectdevice_id = request.GET.get("cdevice_id")

        if not LoginUser.objects.filter(id=user_id).filter(is_active=1):
            response = {
                'message': ['用户不存在或已停用'],
                # 'token':token
                'code': ["999"]
            }
            return Response(response, status=200)

        if not LoginUser.objects.filter(id=user_id).filter(
                Q(u_type='公司管理员') | Q(u_type='设备管理员')):  # 如果用户不是公司管理员或设备管理员，需要他拥有后台人员身份
            if not LoginUser.objects.filter(id=user_id).filter(
                    Q(u_type='运营') | Q(u_type='运维顾问') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                response = {
                    'message': ['您无权进行此操作'],
                    # 'token':token
                    'code': ["996"]
                }
                return Response(response, status=200)
        objJson = serialize("json", Collectdevice.objects.filter(id=collectdevice_id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))

    def post(self, request, *args, **kwargs):
        serializer = EditcollectdeviceSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.data['cdevice_id']
            device = Collectdevice.objects.get(id=id)

            # device.cd_name = serializer.data['cd_name']
            # device.cd_series_number = serializer.data['cd_series_number']
            # device.cd_tunnel = serializer.data['cd_tunnel']
            # device.cd_status = serializer.data['cd_status']
            # device.cd_data_status = serializer.data['cd_data_status']
            # device.cd_last_contract_time = serializer.data['cd_last_contract_time']
            # device.cd_register_time = serializer.data['cd_register_time']
            # device.cd_nodeid = serializer.data['cd_nodeid']
            device.cd_name = serializer.data['cd_name']
            device.cd_produce_time = serializer.data['cd_produce_time']
            device.cd_manufacturer = serializer.data['cd_manufacturer']
            device.cd_install_time = serializer.data['cd_install_time']
            device.cd_SN = serializer.data['cd_SN']
            device.cd_SIM = serializer.data['cd_SIM']
            device.cd_GPS = serializer.data['cd_GPS']
            device.cd_placed = serializer.data['cd_placed']

            device.save()

            response = {
                'message': ['设备信息修改成功。'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Delcollectdevice(GenericAPIView):
    '''
    删除采集设备，需公司管理员或运维人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditcollectdeviceSerializerv2

    def post(self, request, *args, **kwargs):
        serializer = EditcollectdeviceSerializerv2(data=request.data)
        if serializer.is_valid():
            s = serializer.data['cdevice_id']
            device = Collectdevice.objects.get(id=s)
            device.delete()

            response = {
                'message': ['设备删除成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Collectdeviceatt(GenericAPIView):
    '''
    添加采集设备属性，需公司管理员或运维人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = CollectdeviceattSerializer

    def post(self, request, *args, **kwargs):
        serializer = CollectdeviceattSerializer(data=request.data)
        if serializer.is_valid():
            cdd_c_id = serializer.data["device_id"]  # 采集设备id

            data = Cdevicedata()
            device = Collectdevice.objects.get(id=cdd_c_id)
            data.cdd_c_id = device
            data.cdd_name = serializer.data["name"]
            data.cdd_data = serializer.data["cdd_data"]

            data.save()

            response = {
                'message': ['设备属性创建成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Editcollectdeviceatt(GenericAPIView):
    '''
    查看&修改采集设备属性，需公司管理员或运维人员操作, 查看get需要传值：user_id和采集设备id：collectdevice_id 修改需要一个属性一个属性修改
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditcollectdeviceattSerializer

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get("user_id")
        collectdevice_id = request.GET.get("cdevice_id")

        if not LoginUser.objects.filter(id=user_id).filter(is_active=1):
            response = {
                'message': ['用户不存在或已停用'],
                # 'token':token
                'code': ["999"]
            }
            return Response(response, status=200)

        if not LoginUser.objects.filter(id=user_id).filter(
                Q(u_type='公司管理员') | Q(u_type='设备管理员')):  # 如果用户不是公司管理员或设备管理员，需要他拥有后台人员身份
            if not LoginUser.objects.filter(id=user_id).filter(
                    Q(u_type='运营') | Q(u_type='运维顾问') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                response = {
                    'message': ['您无权进行此操作'],
                    # 'token':token
                    'code': ["996"]
                }
                return Response(response, status=200)
        objJson = serialize("json", Collectdevice.objects.filter(id=collectdevice_id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))

    def post(self, request, *args, **kwargs):
        serializer = EditcollectdeviceattSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.data["device_data_id"]  # 采集设备属性id

            data = Cdevicedata.objects.get(id=id)
            data.cdd_name = serializer.data["name"]
            data.cdd_data = serializer.data["cdd_data"]

            data.save()

            response = {
                'message': ['设备属性修改成功'],
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Delcollectdeviceatt(GenericAPIView):
    """
    删除采集设备属性，需公司管理员或运维人员操作
    """

    authentication_classes = []
    permission_classes = []
    serializer_class = EditcollectdeviceattSerializer

    def post(self, request, *args, **kwargs):
        serializer = EditcollectdeviceattSerializer(data=request.data)
        if serializer.is_valid():
            device = Cdevicedata.objects.get(serializer.data['device_data_id'])
            device.delete()

            response = {
                'message': ['设备属性删除成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 在项目中添加设备，需公司管理员操作
class Applydevice(GenericAPIView):
    """
    在项目中添加设备，需公司管理员操作
    """

    authentication_classes = []
    permission_classes = []
    serializer_class = ApplydeviceSerializer

    def post(self, request, *args, **kwargs):
        serializer = ApplydeviceSerializer(data=request.data)
        if serializer.is_valid():
            d_m_id = serializer.data["user_id"]  # 获取创建人ID
            d_p_id = serializer.data["project_id"]
            company_id = serializer.data["company_id"]
            cd_name = serializer.data["cd_name"]
            devices = Device.objects.filter(d_co_id=company_id).count()

            device = Device()
            user = LoginUser.objects.get(id=d_m_id)
            project = Project.objects.get(id=d_p_id)
            company = Company.objects.get(id=company_id)
            coll = Collectdevice.objects.get(cd_name=cd_name)
            device.d_m_id = user
            device.d_p_id = project
            device.d_c_id = coll
            device.d_co_id = company
            device.d_name = serializer.data["d_name"]
            device.d_GPS = serializer.data["d_GPS"]
            device.d_produce_time = serializer.data["d_produce_time"]
            device.d_manufacturer = serializer.data["d_manufacturer"]
            # device.d_data_status = serializer.data["d_data_status"]
            # device.d_last_contract_time = serializer.data["d_last_contract_time"]
            device.d_register_time = datetime.datetime.now()
            device.d_company_number = devices + 1
            device.save()

            response = {
                'message': ['设备创建成功。'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class viewdevice(GenericAPIView):
    '''
    在项目中添加设备，需公司管理员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        device_id = request.GET.get('d_id')
        device = Device.objects.filter(id=device_id)
        print(device)
        if not device:
            response_data = {'code': ["944"], 'message': ['机械设备不存在']}
            return Response(response_data, status=200)
        device = Device.objects.get(id=device_id)
        b = []
        deviceattt = []
        deviceatts = Devicedata.objects.filter(ddd_d_id=device)
        if deviceatts:
            for deviceatt in deviceatts:
                att = {'ID': '', 'name': '', 'detail': ''}
                att["name"] = deviceatt.ddd_name
                att["ID"] = deviceatt.id
                att['detail'] = deviceatt.ddd_detail
                deviceattt.append(att)
        data = {"devicename": device.d_name, 'ID': device.id, 'd_GPS': device.d_GPS,
                'd_manufacturer': device.d_manufacturer, 'd_status': device.d_status,
                'd_produce_time': device.d_produce_time, 'd_register_time': device.d_register_time, 'Boolean': True,
                'deviceatt': deviceattt}

        b.append(data)
        response = {
            'data': b,
            'code': ["200"]
        }
        return Response(response, status=200)


#
class Editdevice(GenericAPIView):
    '''
    get查看&&post修改设备信息,需要公司管理员或设备负责人操作或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditdeviceSerializer

    def post(self, request, *args, **kwargs):
        serializer = EditdeviceSerializer(data=request.data)
        if serializer.is_valid():
            device = Device.objects.get(id=serializer.data['device_id'])
            device.d_name = serializer.data['d_name']
            device.d_GPS = serializer.data["d_GPS"]
            device.d_produce_time = serializer.data["d_produce_time"]
            device.d_manufacturer = serializer.data["d_manufacturer"]
            device.save()

            response = {
                'message': ['修改成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 查看项目设备列表
class Devicelist(GenericAPIView):
    '''
    查看项目设备列表,需要用户为公司员工或公司管理人员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DevicelistSerializer

    def post(self, request, *args, **kwargs):
        serializer = DevicelistSerializer(data=request.data)
        if serializer.is_valid():
            objJson = serialize("json", Device.objects.filter(d_p_id=serializer.data['project_id']).filter(d_active=1))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


class PersonDevicelist(GenericAPIView):
    '''
    查看项目设备列表,需要用户为公司员工或公司管理人员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = PersonDevicelistSerializer

    def post(self, request, *args, **kwargs):
        serializer = PersonDevicelistSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])
            if user.u_type == '公司管理员':
                company = Company.objects.get(id=user.u_company_id)
                projects = Project.objects.filter(p_c_id=company.id)
                devices = []
                for project in projects:
                    d = Device.objects.filter(d_p_id=project).filter(d_active=1)
                    for dd in d:
                        dict = {'d_company_number': dd.d_company_number, 'project': project.p_name, 'deviceid': dd.id,
                                'devicename': dd.d_name,
                                'd_GPS': dd.d_GPS,
                                'd_manufacturer': dd.d_manufacturer, 'd_status': dd.d_status,
                                'd_produce_time': dd.d_produce_time, }
                        devices.append(dict)
                response_data = {'code': ["200"], 'data': devices}
                return Response(response_data)
            projects = user.project.all()
            devices = []
            for project in projects:

                d = Device.objects.filter(d_p_id=project).filter(d_active=1)
                for dd in d:
                    dict = {'d_company_number': dd.d_company_number, 'project': project.p_name, 'deviceid': '',
                            'devicename': '', 'd_GPS': '',
                            'd_manufacturer': '', 'd_status': '', 'd_produce_time': '', }
                    dict["deviceid"] = dd.id
                    dict["devicename"] = dd.d_name
                    dict["d_GPS"] = dd.d_GPS
                    dict["d_manufacturer"] = dd.d_manufacturer
                    dict["d_status"] = dd.d_status
                    dict["d_produce_time"] = dd.d_produce_time
                    devices.append(dict)

            # objJson = serialize("json", Device.objects.filter(d_p_id=serializer.data['project_id']).filter(d_active=1))
            # objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': devices}
            return Response(response_data)
        return Response(serializer.errors)


class DeleteDevice(GenericAPIView):
    '''
    删除机械设备
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DeleteDeviceSerializer

    def post(self, request, *args, **kwargs):
        serializer = DeleteDeviceSerializer(data=request.data)
        if serializer.is_valid():
            d = Device.objects.get(id=serializer.data['device_id'])
            d.delete()
            response_data = {'code': ["200"], 'message': ['机械设备删除成功']}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# 关联设备与公司员工
class Signdevice(GenericAPIView):
    '''
    关联设备与公司员工,需要用户为公司管理人员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = SigndeviceSerializer

    def post(self, request, *args, **kwargs):
        serializer = SigndeviceSerializer(data=request.data)
        if serializer.is_valid():
            device = Device.objects.get(id=serializer.data['device_id'])
            user_id = request.POST.get("operator_id")
            device.d_u_id = user_id
            device.save()
            response = {
                'message': ['关联成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 取消设备与公司员工关联
class Unsigndevice(GenericAPIView):
    '''
    取消设备与公司员工关联,需要用户为公司管理人员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = SigndeviceSerializer

    def post(self, request, *args, **kwargs):
        serializer = SigndeviceSerializer(data=request.data)
        if serializer.is_valid():
            device = Device.objects.get(id=serializer.data['device_id'])
            device.d_u_id = None
            device.save()
            response = {
                'message': ['取消关联成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class AdddeviceGroup(GenericAPIView):
    """
    添加机械组
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = AdddeviceattSerializer  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = AdddeviceattSerializer(data=request.data)
        if serializer.is_valid():
            device_data = DataGroup()
            device_data.dg_d_id = Device.objects.get(id=serializer.data['device_id'])
            device_data.dg_name = serializer.data['dg_name']
            device_data.dg_type = serializer.data['dg_type']
            device_data.save()
            response = {
                'message': ['机械设备组创建成功'],
                'code': ["200"]
            }
            return Response(response)
        return Response(serializer.errors)


class DeldeviceGroup(GenericAPIView):
    """
    删除机械组
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = DeldeviceSerializer  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = DeldeviceSerializer(data=request.data)
        if serializer.is_valid():
            d = DataGroup.objects.get(id=serializer.data['g_id'])
            d.delete()
            response = {
                'message': ['机械设备组删除成功'],
                'code': ["200"]
            }
            return Response(response)
        return Response(serializer.errors)


# 添加机械设备属性，需公司管理员操作
class Adddeviceatt(GenericAPIView):
    """添加机械设备属性"""
    authentication_classes = []
    permission_classes = []
    serializer_class = AdddeviceattSerializerv2  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = AdddeviceattSerializerv2(data=request.data)
        if serializer.is_valid():
            device_data = Devicedata()
            device_data.ddd_d_id = Device.objects.get(id=serializer.data['d_id'])
            device_data.ddd_name = serializer.data['ddd_name']
            device_data.ddd_detail = serializer.data['ddd_detail']
            device_data.save()
            response = {
                'message': ['添加机械设备属性成功'],
                'code': ["200"]
            }
            return Response(response)
        return Response(serializer.errors)


# 查看编辑设备属性 需公司管理员操作
class Editdeviceatt(GenericAPIView):
    """
    查看编辑设备属性
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = EditdeviceattSerializer  # 权限要求相同

    def get(self, request, *args, **kwargs):
        """
        查看设备属性
        """
        device_attribute = request.GET.get("device_attribute")
        objJson = serialize("json", Devicedata.objects.filter(ddd_name=device_attribute))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))

    def post(self, request, *args, **kwargs):
        """
        编辑设备属性
        """
        serializer = EditdeviceattSerializer(data=request.data)
        if serializer.is_valid():
            device_data = Devicedata.objects.get(ddd_name=serializer.data['device_attribute'])
            device_data.ddd_detail = serializer.data['device_data']
            device_data.save()
            response = {
                'message': ['编辑机械设备属性成功'],
                'code': ["200"]
            }
            return Response(response)
        return Response(serializer.errors)


# 删除机械设备属性，需公司管理员操作
class Deldeviceatt(GenericAPIView):
    """
    删除机械设备属性
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = DeldeviceattSerializer  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = DeldeviceattSerializer(data=request.data)
        if serializer.is_valid():
            device_data = Devicedata.objects.filter(id=serializer.data['ddevice_id'])
            device_data.delete()
            response = {
                'message': ['删除机械设备属性成功'],
                'code': ["200"]
            }
            return Response(response)
        return Response(serializer.errors)


class DeviceGrouplist(GenericAPIView):
    """
    删除机械设备属性
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = DeviceGrouplistSerializer  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = DeviceGrouplistSerializer(data=request.data)
        if serializer.is_valid():
            device_id = serializer.data['device_id']
            d = DataGroup.objects.filter(dg_d_id=device_id)
            if not d:
                response_data = {'code': ["942"], 'message': ['当前设备未设置参数']}
                return HttpResponse(json.dumps(response_data))
            threeinone4(device_id)
            objJson = serialize("json", d)
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# 为设备添加数据
class Adddata(GenericAPIView):
    '''
    为设备添加数据,需要用户为公司管理人员或设备负责人或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditdeviceSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = EditdeviceSerializer(data=request.data)
        if serializer.is_valid():
            data = Data()
            # d_d_id = serializer.data['device_id']
            data.d_d_id = Device.objects.get(id=serializer.data['device_id'])
            data.d_name = request.POST.get('d_name')
            data.d_data = request.POST.get('d_data')  # 暂定
            data.save()
            response = {
                'message': ['数据添加成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 查看设备数据
class Viewdata(GenericAPIView):
    '''
    查看设备数据,需要用户为公司管理人员或设备负责人或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ViewdataSerializer

    def post(self, request, *args, **kwargs):
        serializer = ViewdataSerializer(data=request.data)
        if serializer.is_valid():
            g_id = serializer.data['g_id']
            objJson1 = serialize("json", Data.objects.filter(d_cd_id=serializer.data['cd_id'], d_g_id=g_id))
            objStr1 = json.loads(objJson1)
            objJson = serialize("json", Data.objects.filter(d_cd_id=serializer.data['cd_id']))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr, 'selected': objStr1}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


class DeviceAddData(GenericAPIView):
    '''
    查看设备数据,需要用户为公司管理人员或设备负责人或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def post(self, request, *args, **kwargs):
        response = request.body.decode()
        r_str = json.loads(response)
        paras = jsonpath(r_str, '$.data_id[*]')
        group_id = jsonpath(r_str, '$.g_id')
        group = DataGroup.objects.get(id=group_id[0])  # 组
        datas = Data.objects.filter(d_g_id=group)
        for data in datas:
            data.d_g_id = None
            data.save()
        for d in paras:
            id = d['parameter_id']
            data = Data.objects.get(id=id)
            data.d_g_id = group
            data.d_d_id_id = group.dg_d_id
            data.save()
            group.has_data = 1
            group.save()

        response_data = {'code': ["200"], 'message': ['参数添加成功']}
        return HttpResponse(json.dumps(response_data))


class SearchData(GenericAPIView):
    '''
    查看设备数据,需要用户为公司管理人员或设备负责人或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        name = request.GET.get('key')
        cd_id = request.GET.get('cd_id')
        data = Data.objects.filter(d_cd_id=cd_id).filter(Q(d_name_icontains=name) | Q(d_description__icontains=name))
        objJson = serialize("json", data)
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))


# 删除设备数据
class Deletedata(GenericAPIView):
    '''
    删除设备数据,需要用户为公司管理人员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DataSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = DataSerializer(data=request.data)
        if serializer.is_valid():
            data = Data.objects.get(id=serializer.data['data_id'])
            group = data.d_g_id
            data.delete()

            data = Data.objects.filter(d_g_id=group.id)
            if not data:
                group.has_data = 0
                group.save()
            response = {
                'message': ['数据删除成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 为数据添加告警规则
class Addalert(GenericAPIView):
    '''
    为数据添加告警规则,需要用户为公司管理人员或设备负责人或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AddAlertSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = AddAlertSerializer(data=request.data)
        if serializer.is_valid():
            device = DataGroup.objects.get(id=serializer.data['dg_id'])
            device.has_alert = 1

            device.save()
            device_id = device.dg_d_id_id
            c_id = device.dg_d_id.d_c_id_id
            p_id = device.dg_d_id.d_c_id.cd_p_id_id
            company_id = device.dg_d_id.d_co_id_id
            alert = Alert()
            alert.a_company_id = Company.objects.get(id=company_id)
            alert.a_project_id = Project.objects.get(id=p_id)
            alert.a_c_id = Collectdevice.objects.get(id=c_id)
            alert.a_device_id = Device.objects.get(id=device_id)
            alert.a_datagroup_id = device

            alert.a_highest_line = serializer.data['a_highest_line']
            alert.a_highest_level = serializer.data['a_highest_level']
            alert.a_highest_tip = serializer.data['a_highest_tip']
            alert.a_high_line = serializer.data['a_high_line']
            alert.a_high_level = serializer.data['a_high_level']
            alert.a_high_tip = serializer.data['a_high_tip']
            alert.a_low_line = serializer.data['a_low_line']
            alert.a_low_level = serializer.data['a_low_level']
            alert.a_low_tip = serializer.data['a_low_tip']
            alert.a_lowest_line = serializer.data['a_lowest_line']
            alert.a_lowest_level = serializer.data['a_lowest_level']
            alert.a_lowest_tip = serializer.data['a_lowest_tip']
            alert.save()
            device.alert_id = alert.id
            device.save()
            response = {
                'message': ['数据告警规则添加成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 编辑数据告警规则
class Editalert(GenericAPIView):
    '''
    编辑数据告警规则,需要用户为公司管理人员或设备负责人或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AlertSerializer  # 权限判断相同

    def get(self, request, *args, **kwargs):
        alert_id = request.GET.get('alert_id')
        print(alert_id)
        objJson = serialize("json", Alert.objects.filter(id=alert_id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))

    def post(self, request, *args, **kwargs):
        serializer = EditAlertSerializer(data=request.data)
        if serializer.is_valid():
            alert = Alert.objects.get(id=serializer.data['alert_id'])
            alert.a_highest_line = serializer.data['a_highest_line']
            alert.a_highest_level = serializer.data['a_highest_level']
            alert.a_highest_tip = serializer.data['a_highest_tip']
            alert.a_high_line = serializer.data['a_high_line']
            alert.a_high_level = serializer.data['a_high_level']
            alert.a_high_tip = serializer.data['a_high_tip']
            alert.a_low_line = serializer.data['a_low_line']
            alert.a_low_level = serializer.data['a_low_level']
            alert.a_low_tip = serializer.data['a_low_tip']
            alert.a_lowest_line = serializer.data['a_lowest_line']
            alert.a_lowest_level = serializer.data['a_lowest_level']
            alert.a_lowest_tip = serializer.data['a_lowest_tip']
            alert.save()
            response = {
                'message': ['数据告警规则修改成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 删除数据规则
class Deletealert(GenericAPIView):
    '''
    删除数据告警规则,需要用户为公司管理人员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AlertSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = AlertSerializer(data=request.data)
        if serializer.is_valid():
            alert = Alert.objects.get(id=serializer.data['alert_id'])
            dg_id = alert.a_datagroup_id_id
            devicegroup = DataGroup.objects.get(id=dg_id)

            alert.delete()
            devicegroup.has_alert = 0
            devicegroup.alert_id = None
            devicegroup.save()
            response = {
                'message': ['告警规则删除成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class AlarmLogList(GenericAPIView):
    '''
    删除数据告警规则,需要用户为公司管理人员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AlarmlistSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = AlarmlistSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])
            company_id = user.u_company_id
            typelist = ['公司管理员', '设备管理员', '员工']
            if user.u_type in typelist:
                alert = AlarmLog.objects.filter(log_company_id=company_id).values('id', 'log_name',
                                                                                  'log_alarm_type',
                                                                                  'log_alarm_data',
                                                                                  'log_device__d_name',
                                                                                  'log_project__p_name',
                                                                                  'log_company__company_name',
                                                                                  'log_group_name',
                                                                                  'log_message',
                                                                                  'log_type',
                                                                                  'log_time').order_by('-log_time')[
                        :100]
                # objJson = serialize("json", alert)
                # objStr = json.loads(objJson)
                response_data = {'code': ['200'], 'data': alert}
                return Response(response_data)
            alert = AlarmLog.objects.all().values('id', 'log_name',
                                                  'log_alarm_type',
                                                  'log_alarm_data',
                                                  'log_device__d_name',
                                                  'log_project__p_name',
                                                  'log_company__company_name',
                                                  'log_group_name',
                                                  'log_message',
                                                  'log_type',
                                                  'log_time').order_by('-log_time')[:100]
            # objJson = serialize("json", alert)
            # objStr = json.loads(objJson)
            response_data = {'code': ['200'], 'data': alert}
            return Response(response_data)
        return Response(serializer.errors)


class SearchAlarmLog(GenericAPIView):
    '''
    删除数据告警规则,需要用户为公司管理人员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []  # 权限判断相同

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        d_name = request.GET.get('d_name')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        user = LoginUser.objects.get(id=user_id)
        company_id = user.u_company_id
        typelist = ['公司管理员', '设备管理员', '员工']
        if user.u_type in typelist:
            if d_name and start_time:
                alert = AlarmLog.objects.filter(log_company_id=company_id, log_device__d_name__icontains=d_name,
                                                log_time__range=(start_time, end_time)).values('id', 'log_name',
                                                                                               'log_alarm_type',
                                                                                               'log_alarm_data',
                                                                                               'log_device__d_name',
                                                                                               'log_project__p_name',
                                                                                               'log_company__company_name',
                                                                                               'log_group_name',
                                                                                               'log_message',
                                                                                               'log_type',
                                                                                               'log_time').order_by(
                    '-log_time')[:100]
                # objJson = serialize("json", alert)
                # objStr = json.loads(objJson)
                response_data = {'code': ['200'], 'data': alert}
                return Response(response_data)
            if start_time:
                alert = AlarmLog.objects.filter(log_company_id=company_id,
                                                log_time__range=(start_time, end_time)).values('id', 'log_name',
                                                                                               'log_alarm_type',
                                                                                               'log_alarm_data',
                                                                                               'log_device__d_name',
                                                                                               'log_project__p_name',
                                                                                               'log_company__company_name',
                                                                                               'log_group_name',
                                                                                               'log_message',
                                                                                               'log_type',
                                                                                               'log_time').order_by(
                    '-log_time')[:100]
                # objJson = serialize("json", alert)
                # objStr = json.loads(objJson)
                response_data = {'code': ['200'], 'data': alert}
                return Response(response_data)
            alert = AlarmLog.objects.filter(log_company_id=company_id, log_device__d_name__icontains=d_name).values(
                'id', 'log_name',
                'log_alarm_type',
                'log_alarm_data',
                'log_device__d_name',
                'log_project__p_name',
                'log_company__company_name',
                'log_group_name',
                'log_message',
                'log_type',
                'log_time').order_by(
                '-log_time')[:100]
            # objJson = serialize("json", alert)
            # objStr = json.loads(objJson)
            response_data = {'code': ['200'], 'data': alert}
            return Response(response_data)
        if d_name and start_time:
            alert = AlarmLog.objects.filter(log_device__d_name__icontains=d_name,
                                            log_time__range=(start_time, end_time)).values('id', 'log_name',
                                                                                           'log_alarm_type',
                                                                                           'log_alarm_data',
                                                                                           'log_device__d_name',
                                                                                           'log_project__p_name',
                                                                                           'log_company__company_name',
                                                                                           'log_group_name',
                                                                                           'log_message',
                                                                                           'log_type',
                                                                                           'log_time').order_by(
                '-log_time')[:100]
            # objJson = serialize("json", alert)
            # objStr = json.loads(objJson)
            response_data = {'code': ['200'], 'data': alert}
            return Response(response_data)
        if start_time:
            alert = AlarmLog.objects.filter(log_time__range=(start_time, end_time)).values('id', 'log_name',
                                                                                           'log_alarm_type',
                                                                                           'log_alarm_data',
                                                                                           'log_device__d_name',
                                                                                           'log_project__p_name',
                                                                                           'log_company__company_name',
                                                                                           'log_group_name',
                                                                                           'log_message',
                                                                                           'log_type',
                                                                                           'log_time').order_by(
                '-log_time')[:100]
            # objJson = serialize("json", alert)
            # objStr = json.loads(objJson)
            response_data = {'code': ['200'], 'data': alert}
            return Response(response_data)
        alert = AlarmLog.objects.filter(log_device__d_name__icontains=d_name).values('id',
                                                                                     'log_name',
                                                                                     'log_alarm_type',
                                                                                     'log_alarm_data',
                                                                                     'log_device__d_name',
                                                                                     'log_project__p_name',
                                                                                     'log_company__company_name',
                                                                                     'log_group_name',
                                                                                     'log_message',
                                                                                     'log_type',
                                                                                     'log_time').order_by('-log_time')[
                :100]
        # objJson = serialize("json", alert)
        # objStr = json.loads(objJson)
        response_data = {'code': ['200'], 'data': alert}
        return Response(response_data)


class SolveAlarm(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = []  # 权限判断相同

    def get(self, request, *args, **kwargs):
        alarm_id = request.GET.get('alarm_id')
        alarmlog = AlarmLog.objects.filter(id=alarm_id)
        if alarmlog:
            alarmlog = AlarmLog.objects.get(id=alarm_id)
            if alarmlog.log_type == "已解决":
                response = {
                    'message': ['报警已解决'],
                    'code': ["935"],
                }
                return Response(response, status=200)
            alarmlog.log_type = '已解决'
            alarmlog.save()
        response = {
            'message': ['操作成功'],
            'code': ["200"],
        }
        return Response(response, status=200)


# 用户创建投诉记录
class CreateUserComplain(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = UserComplainSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = UserComplainSerializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.data["user_id"]
            employee_id = serializer.data["employee_id"]
            complainrecord = Complainrecord()

            complainrecord.cr_u_id = LoginUser.objects.get(id=serializer.data["user_id"])
            complainrecord.cr_e_id = LoginUser.objects.get(id=serializer.data["employee_id"])
            complainrecord.cr_detail = serializer.data["context"]
            complainrecord.cr_date = datetime.datetime.now()
            complainrecord.cr_type = "未解决"
            complainrecord.save()
            response = {
                'message': ['创建投诉记录成功'],
                'code': ["200"],
                "userid": user_id,
                "employee_id": employee_id,
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 用户删除投诉记录
class DeleteUserComplain(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = UserDeleteComplainSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = UserDeleteComplainSerializer(data=request.data)
        if serializer.is_valid():
            usercomplain = Complainrecord.objects.get(id=serializer.data['complain_id'])
            usercomplain.delete()
            response = {
                'message': ['删除投诉记录成功'],
                'code': ["200"],
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 客户查看自己投诉记录列表
class SelectMyComplain(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = SelectMyComplainSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = SelectMyComplainSerializer(data=request.data)
        # page = CurrentPagination
        if serializer.is_valid():
            usercomplains = Complainrecord.objects.filter(cr_u_id=serializer.data['user_id'])
            if not usercomplains:
                response_data = {'code': ["923"], 'message': "目前不存在投诉记录"}
                return HttpResponse(json.dumps(response_data))
            objJson = serialize("json", usercomplains)
            objStr = json.loads(objJson)
            response_data = {'code': '200', 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# 客户查看自己投诉记录详情
class SelectComplainDetail(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = SelectComplainDetailSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = SelectComplainDetailSerializer(data=request.data)
        if serializer.is_valid():
            objJson = serialize("json", Complainrecord.objects.filter(id=serializer.data['complain_id']))
            objStr = json.loads(objJson)
            response_data = {'code': '200', 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# 客户编辑投诉记录状态
class ChangeMyComplain(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = ChangeMyComplainSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = ChangeMyComplainSerializer(data=request.data)
        if serializer.is_valid():
            complain = Complainrecord.objects.get(id=serializer.data['complain_id'])
            complain.cr_type = "已解决"
            complain.save()
            response = {
                'message': ['投诉状态修改成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 客服查看自己投诉记录列表
class SelectEmployeeComplain(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = SelectEmployeeComplainSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = SelectEmployeeComplainSerializer(data=request.data)
        if serializer.is_valid():
            employee_complains = Complainrecord.objects.filter(cr_e_id=serializer.data['employee_id'])
            objJson = serialize("json", employee_complains)
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
        return Response(serializer.errors)


# 客服查看自己投诉记录详情
class SelectEmployeeComplainDetail(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = SelectEmployeeComplainDetailSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = SelectEmployeeComplainDetailSerializer(data=request.data)
        if serializer.is_valid():
            complain = Complainrecord.objects.get(id=serializer.data['complain_id'])
            objJson = serialize("json", complain)
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return Response(json.dumps(response_data))
        return Response(serializer.errors)


# 客服查看自己未解决的投诉记录列表
class SelectEmployeeUnresolve(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = SelectEmployeeComplainSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = SelectEmployeeComplainSerializer(data=request.data)
        if serializer.is_valid():
            employee_complains = Complainrecord.objects.filter(cr_e_id=serializer.data['employee_id']).filter(
                cr_type='未解决')
            objJson = serialize("json", employee_complains)
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return Response(json.dumps(response_data))
        return Response(serializer.errors)


# 新公司申请权限审批
# 通过审批
class Activatecompany(GenericAPIView):
    '''
    通过新公司申请审批,需要后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ActivatecompanySerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = ActivatecompanySerializer(data=request.data)
        if serializer.is_valid():
            company = Company.objects.get(id=serializer.data['company_id'])
            company.active = 1
            company.save()
            response = {
                'message': ['公司通过审核'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 新设备申请权限审批
# 搜索所有未激活状态的设备
class Deactivedevicelist(GenericAPIView):
    '''
    搜索所有未激活状态的设备,需要后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DeactivedevicelistSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = DeactivedevicelistSerializer(data=request.data)
        if serializer.is_valid():
            devices = Device.objects.filter(d_active=0)
            response = {
                'message': ['查询成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)  # return render locals()  问题：除设备信息外是否需要显示公司、项目等信息
        return Response(serializer.errors)


# 激活设备
class Activatedevice(GenericAPIView):
    '''
    激活设备,需要后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ActivatedeviceSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = ActivatedeviceSerializer(data=request.data)
        if serializer.is_valid():
            device = Device.objects.get(id=serializer.data['device_id'])
            device.d_active = 1
            device.save()
            response = {
                'message': ['设备激活成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Addmaintainrecord(GenericAPIView):
    '''
    运维创建设备维修记录 or 设备负责人创建设备维修记录,需要身份验证
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AddmaintainrecordSerializer

    def post(self, request, *args, **kwargs):
        serializer = AddmaintainrecordSerializer(data=request.data)
        if serializer.is_valid():
            maintainrecord = Devicemaintainrecord()
            maintainrecord.dm_d_id = Device.objects.get(id=serializer.data['d_id'])
            maintainrecord.dm_o_id = LoginUser.objects.get(id=serializer.data['user_id'])
            maintainrecord.dmo_name = maintainrecord.dm_o_id.username
            maintainrecord.dm_d_detail = serializer.data['dm_d_detail']
            maintainrecord.dm_name = serializer.data['dm_name']
            maintainrecord.dm_time = datetime.datetime.now()
            maintainrecord.save()
            response = {
                'message': ['设备维修记录创建成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)

class Maintainrecordlist(GenericAPIView):
    '''
    查看设备所有维修记录,需要身份验证
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = MaintainrecordSerializer  # 权限验证相同

    def get(self, request, *args, **kwargs):
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条
        id = request.GET.get("dm_d_id")
        records = Devicemaintainrecord.objects.filter(dm_d_id=id).order_by('id')
        if not records:
            response_data = {'code': ["924"], 'message': "目前设备不存在维修记录"}
            return HttpResponse(json.dumps(response_data))

        paginator = Paginator(records, per_page)
        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        # objJson1 = serialize("json", paginator.page_range)

        objStr = json.loads(objJson)
        # objStr1 = json.loads(objJson1)
        response_data = {'code': '200', 'data': objStr, 'max_page': total_page, 'datacount': total_data}

        return HttpResponse(json.dumps(response_data))


# class CompanyMaintainrecordlistV1(GenericAPIView):
#     '''
#     查看设备所有维修记录,需要身份验证
#     '''
#     authentication_classes = []
#     permission_classes = []
#     serializer_class = CompanyMaintainrecordSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = CompanyMaintainrecordSerializer(data=request.data)
#         if serializer.is_valid():
#             page = int(serializer.data['page'])
#             per_page = int(serializer.data['per_page'])
#             company_id = serializer.data['company_id']
#             records = Devicemaintainrecord.objects.filter(dm_d_id__d_co_id=company_id).order_by('-dm_time')
#
#             paginator = Paginator(records, per_page)
#             total_page = paginator.num_pages
#             total_data = paginator.count
#
#             page_object = paginator.page(page)
#             objJson = serialize("json", page_object)
#             objStr = json.loads(objJson)
#             response_data = {'code': ["200"], 'data': objStr, 'max_page': total_page, 'datacount': total_data}
#
#             return HttpResponse(json.dumps(response_data))
#
#         return Response(serializer.errors)


class CompanyMaintainrecordlist(GenericAPIView):
    '''
    查看设备所有维修记录,需要身份验证
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = CompanyMaintainrecordSerializer

    def post(self, request, *args, **kwargs):
        serializer = CompanyMaintainrecordSerializer(data=request.data)
        if serializer.is_valid():
            company_id = serializer.data['company_id']
            records = Devicemaintainrecord.objects.filter(dm_d_id__d_co_id=company_id).values('id', 'dmo_name',
                                                                                              'dm_d_id__d_p_id__p_name',
                                                                                              'dm_d_id__d_name',
                                                                                              'dm_d_id__d_p_id__p_name',
                                                                                              'dm_name',
                                                                                              'dm_time').order_by(
                '-dm_time')
            # records = Devicemaintainrecord.objects.filter(dm_d_id__d_co_id=company_id)

            response_data = {'code': ["200"], 'data': records}
            return Response(response_data)
        return Response(serializer.errors)


class CompanyMaintainrecordlistV1(GenericAPIView):
    '''
    查看设备所有维修记录,需要身份验证
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = CompanyMaintainrecordSerializer

    def post(self, request, *args, **kwargs):
        serializer = CompanyMaintainrecordSerializer(data=request.data)
        if serializer.is_valid():
            # page = int(serializer.data['page'])
            # per_page = int(serializer.data['per_page'])
            company_id = serializer.data['company_id']
            # records = Devicemaintainrecord.objects.extra(
            #                 select={
            #                     'dmo_name':'dmo_name',
            #                     'dm_d_detail':'dm_d_detail',
            #                     'dm_time':'dm_time',
            #                     'dm_name':'dm_name',
            #                     'p_name':'one_project.p_name',
            #                     'd_name':'one_device.d_name',
            #                 },
            #                 tables=['one_device','one_project'],
            #                 where=["dm_d_id = one_device.id AND one_device.d_p_id = one_project.id"],
            #             )
            #               ds = Devicemaintainrecord.objects.raw("select * from faps_scores where kh=%s", ['10110103'])
            records = Devicemaintainrecord.objects.raw(
                'select dd.id as "id",dd.dmo_name as "dmo_name", dd.dm_d_detail as "dm_d_detail", dd.dm_time as "dm_time", dd.dm_name as "dm_name", p.p_name as "p_name" , d.d_name as "d_name" from one_devicemaintainrecord as dd LEFT JOIN one_device as d ON dd.dm_d_id = d.id LEFT JOIN one_project as p ON d.d_p_id = p.id AND d.d_name =%s AND d.d_co_id=%s',
                ['测试1', company_id])
            dd = []
            for r in records:
                data = {}
                data["dmo_name"] = r.dmo_name
                data["dm_name"] = r.dm_name
                data["dm_d_detail"] = r.dm_d_detail
                data["dm_time"] = r.dm_time
                data["d_name"] = r.d_name
                data["p_name"] = r.p_name
                dd.append(data)
            print(dd)
            # records = serialize('json',records)
            # print(records)
            # # print(records)
            # records = json.loads(records)
            # records = []
            # cursor = connection.cursor()
            # devicename = '测试1'
            # sql_and_params = 'select dd.id as "id",dd.dmo_name as "dmo_name", dd.dm_d_detail as "dm_d_detail", dd.dm_time as "dm_time", dd.dm_name as "dm_name", p.p_name as "p_name" , d.d_name as "d_name" from one_devicemaintainrecord as dd LEFT JOIN one_device as d ON dd.dm_d_id = d.id LEFT JOIN one_project as p ON d.d_p_id = p.id AND d.d_name = (%s) AND d.d_co_id= (%s)', devicename, company_id
            # cursor.execute(sql_and_params[0],sql_and_params[1:])
            # raw = cursor.fetchall()
            # print(raw)
            # raw = cursor.fetchone()  # 返回结果行游标直读向前，读取一条
            # for r in raw:
            #     records.append(r)
            # paginator = Paginator(records, per_page)
            # total_page = paginator.num_pages
            # total_data = paginator.count
            #
            # page_object = paginator.page(page)
            # objJson = json.dumps(page_object)
            # objStr = json.loads(objJson)
            # response_data = {'code': ["200"], 'data': objStr}
            # records = Devicemaintainrecord.objects.filter(dm_d_id__d_co_id=company_id).values('id','dmo_name', 'dm_d_id__d_p_id__p_name', 'dm_d_id__d_name', 'dm_d_id__d_p_id__p_name', 'dm_name', 'dm_time').order_by('-dm_time')
            # print(records)
            # paginator = Paginator(records, per_page)
            # total_page = paginator.num_pages
            # total_data = paginator.count

            # page_object = paginator.page(page)
            # objJson = serialize("json", records)
            # objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': dd}

            return Response(response_data)
            # return Response(response_data)

        return Response(serializer.errors)


class ViewMaintainrecord(GenericAPIView):
    '''
    查看维修记录详情,需要身份验证
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = MaintainrecorddetailSerializer  # 权限验证相同

    def post(self, request, *args, **kwargs):
        serializer = MaintainrecorddetailSerializer(data=request.data)
        if serializer.is_valid():
            record = Devicemaintainrecord.objects.filter(id=serializer.data['id'])
            objJson = serialize("json", record)
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


class DeleteMaintainrecord(GenericAPIView):
    '''
    删除设备维修记录,需要身份验证
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = MaintainrecorddetailSerializer  # 权限验证相同

    def post(self, request, *args, **kwargs):
        serializer = MaintainrecorddetailSerializer(data=request.data)
        if serializer.is_valid():
            record = Devicemaintainrecord.objects.get(id=serializer.data['id'])
            record.delete()
            response = {
                'message': ['设备维修记录删除成功'],
                # 'token':token
                'code': ["200"]
            }
            # return render('ss.html',locals())
            return Response(response, status=200)
        return Response(serializer.errors)


class SearchRecords(GenericAPIView):
    '''
    搜索设备维修记录
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []  # 权限验证相同

    def get(self, request, *args, **kwargs):
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        d_id = request.GET.get('d_id')
        if not start_time:
            objJson = serialize("json",
                                Devicemaintainrecord.objects.filter(dm_d_id_id=d_id, ))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))

        objJson = serialize("json",
                            Devicemaintainrecord.objects.filter(dm_d_id_id=d_id, dm_time__range=(start_time, end_time)))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))


class SearchRecordsV1(GenericAPIView):
    '''
    搜索设备维修记录
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []  # 权限验证相同

    def get(self, request, *args, **kwargs):
        d_id = request.GET.get('d_id')
        dm_name = request.GET.get('dm_name')
        records = Devicemaintainrecord.objects.filter(dm_d_id_id=d_id, dm_name__icontains=dm_name)
        objJson = serialize("json", records)
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))


# 添加工单
class Addworksheet(GenericAPIView):
    '''
    添加工单,需后台工作人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AddworksheetSerializer

    def post(self, request, *args, **kwargs):
        serializer = AddworksheetSerializer(data=request.data)
        if serializer.is_valid():
            worksheet = Worksheet()
            worksheet.w_e_id = LoginUser.objects.get(id=serializer.data['user_id'])
            worksheet.w_name = serializer.data['w_name']
            worksheet.w_type = serializer.data['w_type']
            worksheet.w_content = serializer.data['w_content']
            worksheet.w_u_phone = serializer.data['w_u_phone']
            worksheet.w_wechat = False
            worksheet.w_status = '进行中'
            worksheet.w_time = datetime.datetime.now()
            worksheet.save()
            # user.u_icon = u_icon
            files = request.FILES.getlist('image')
            # dirs = settings.MEDIA_ROOT + '/wmedia/%Y%m%d'
            for file in files:
                worksheetmedia = Worksheetmedia()
                worksheetmedia.wm_w_id = Worksheet.objects.get(id=worksheet.id)
                worksheetmedia.wm_w_image = file
                worksheetmedia.wm_date = datetime.datetime.now()
                worksheetmedia.save()
            response = {
                'message': ['工单创建成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class AddworksheetDraft(GenericAPIView):
    '''
    添加工单,需后台工作人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AddworksheetSerializer

    def post(self, request, *args, **kwargs):
        serializer = AddworksheetSerializer(data=request.data)
        if serializer.is_valid():
            worksheet = Worksheet()
            worksheet.w_e_id = LoginUser.objects.get(id=serializer.data['user_id'])
            worksheet.w_name = serializer.data['w_name']
            worksheet.w_type = serializer.data['w_type']
            worksheet.w_content = serializer.data['w_content']
            worksheet.w_u_phone = serializer.data['w_u_phone']
            worksheet.w_wechat = False
            worksheet.w_status = '未完成'
            worksheet.w_time = datetime.datetime.now()
            worksheet.save()
            # user.u_icon = u_icon
            files = request.FILES.getlist('image')
            # dirs = settings.MEDIA_ROOT + '/wmedia/%Y%m%d'
            for file in files:
                worksheetmedia = Worksheetmedia()
                worksheetmedia.wm_w_id = Worksheet.objects.get(id=worksheet.id)
                worksheetmedia.wm_w_image = file
                worksheetmedia.wm_date = datetime.datetime.now()
                worksheetmedia.save()
            response = {
                'message': ['工单创建成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 微信创建工单
class Createworksheet(GenericAPIView):
    '''
    微信创建工单,需后台工作人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AddworksheetSerializer

    def post(self, request, *args, **kwargs):
        serializer = AddworksheetSerializer(data=request.data)
        if serializer.is_valid():
            worksheet = Worksheet()
            worksheet.w_e_id = LoginUser.objects.get(id=serializer.data['user_id'])
            worksheet.w_name = serializer.data['w_name']
            worksheet.w_type = serializer.data['w_type']
            worksheet.w_content = serializer.data['w_content']
            worksheet.w_u_phone = serializer.data['w_u_phone']
            worksheet.w_wechat = True
            worksheet.w_status = '未完成'
            worksheet.w_time = datetime.datetime.now()
            worksheet.save()
            # user.u_icon = u_icon
            files = request.FILES.getlist('image')
            # dirs = settings.MEDIA_ROOT + '/wmedia/%Y%m%d'
            for file in files:
                worksheetmedia = Worksheetmedia()
                worksheetmedia.wm_w_id = Worksheet.objects.get(id=worksheet.id)
                worksheetmedia.wm_w_image = file
                worksheetmedia.wm_date = datetime.datetime.now()
                worksheetmedia.save()
            response = {
                'message': ['工单创建成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 查看全部工单列表
class Viewworksheets(GenericAPIView):
    '''
    查看全部工单列表,需后台工作人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ViewworksheetsSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = ViewworksheetsSerializer(data=request.data)
        if serializer.is_valid():
            # objJson = serialize("json", Worksheet.objects.filter(Q(w_status='未完成') | Q(w_status='进行中')))
            if not Worksheet.objects.all():
                response_data = {'code': ["925"], 'message': "目前不存在工单信息"}
                return HttpResponse(json.dumps(response_data))
            objJson = serialize("json", Worksheet.objects.all())
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


class SearchworksheetsV1(GenericAPIView):
    '''
    查看全部工单列表,需后台工作人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = SearhworksheetsSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = SearhworksheetsSerializer(data=request.data)
        if serializer.is_valid():
            # objJson = serialize("json", Worksheet.objects.filter(Q(w_status='未完成') | Q(w_status='进行中')))
            status = serializer.data["w_status"]
            w = Worksheet.objects.filter(w_status='进行中')
            w1 = Worksheet.objects.filter(w_status='未完成')
            w2 = Worksheet.objects.filter(w_status='已解决')
            c = w.count()
            c1 = w1.count()
            c2 = w2.count()
            print(c)
            objJson = serialize("json", Worksheet.objects.filter(w_status=status))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr, 'processing': c, 'notfinished': c1, 'finished': c2}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# class Viewworksheets1(GenericAPIView):
#     '''
#     查看全部工单列表,需后台工作人员身份
#     '''
#     authentication_classes = []
#     permission_classes = []
#     serializer_class = ViewworksheetsSerializer  # 权限判断相同
#
#     def post(self, request, *args, **kwargs):
#         serializer = ViewworksheetsSerializer(data=request.data)
#         if serializer.is_valid():
#             # objJson = serialize("json", Worksheet.objects.filter(Q(w_status='未完成') | Q(w_status='进行中')))
#             user_id = serializer.data["user_id"]
#             user = LoginUser.objects.get(id=user_id)
#             if user.u_type == "超级管理员":
#                 objJson = serialize("json", Worksheet.objects.all())
#                 objStr = json.loads(objJson)
#                 response_data = {'code': ["200"], 'data': objStr}
#                 return HttpResponse(json.dumps(response_data))
#             objJson = serialize("json", Worksheet.objects.filter())
#             objStr = json.loads(objJson)
#             response_data = {'code': ["200"], 'data': objStr}
#             return HttpResponse(json.dumps(response_data))
#         return Response(serializer.errors)

# 查看我的工单列表
class Viewmyworksheets(GenericAPIView):
    '''
    查看我的工单列表,需后台工作人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ViewworksheetsSerializer  # 权限判断相同

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        if not LoginUser.objects.filter(id=user_id).filter(is_active=1):
            response = {
                'message': ['用户不存在或已停用'],
                # 'token':token
                'code': ["999"]
            }
            return Response(response, status=200)
        if not LoginUser.objects.filter(id=user_id).filter(Q(u_type='运维顾问') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            response1 = {
                'message': ['您无权进行此操作'],
                # 'token':token
                'code': ["996"]
            }
            return Response(response1, status=200)

        if not Worksheet.objects.filter(w_e_id_id=user_id):
            response_data = {'code': ["925"], 'message': "目前不存在工单信息"}
            return HttpResponse(json.dumps(response_data))

        objJson = serialize("json", Worksheet.objects.filter(w_e_id_id=user_id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))


class Searchworksheets(GenericAPIView):
    '''
    搜索工单（根据名称、时间段）,需后台工作人员身份  需要传参：w_name工单名称，start_time和end_time起止时间选填
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        name = request.GET.get('w_name')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        # worksheets = Worksheet.objects.filter(Q(w_name=name) | Q(w_time__gt=start_time) |Q(w_time__lt=end_time))
        if start_time and name:
            objJson = serialize("json",
                                Worksheet.objects.filter(w_name__icontains=name).filter(w_time__gte=start_time).filter(
                                    w_time__lte=end_time))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))

        if start_time:
            objJson = serialize("json", Worksheet.objects.filter(w_time__gte=start_time).filter(
                w_time__lte=end_time))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))

        objJson = serialize("json", Worksheet.objects.filter(w_name__icontains=name))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))


class Editworksheet(GenericAPIView):
    '''
    查看工单详情&&编辑工单，需要后台人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditworksheetSerializer

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        loginuser = LoginUser.objects.filter(id=user_id).filter(is_active=1)
        if not loginuser:
            response0 = {
                'message': ['用户不存在或已停用'],
                # 'token':token
                'code': ["999"]

            }
            return Response(response0, status=200)
        loginuser = LoginUser.objects.get(id=user_id)
        name = loginuser.username

        worksheets = Worksheet.objects.filter(id=request.GET.get('w_id'))
        if not worksheets:
            response1 = {
                'message': ['工单不存在'],
                # 'token':token
                'code': ["972"]
            }
            return Response(response1, status=200)

        objJson = serialize("json", Worksheet.objects.filter(id=request.GET.get('w_id')))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))

    def post(self, request, *args, **kwargs):
        serializer = EditworksheetSerializer(data=request.data)
        if serializer.is_valid():
            worksheet = Worksheet.objects.get(id=serializer.data['w_id'])
            print(worksheet)
            worksheet.w_name = serializer.data['w_name']
            worksheet.w_type = serializer.data['w_type']
            worksheet.w_content = serializer.data['w_content']
            worksheet.w_u_phone = serializer.data['w_u_phone']
            worksheet.w_wechat = False
            worksheet.w_status = '进行中'
            worksheet.save()
            response = {
                'message': ['工单修改成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Addknowledge(GenericAPIView):
    '''
    添加知识库/行业资讯，需后台人员操作，类型k_type需限制为：知识库或行业资讯
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AddknowledgeSerializer

    def post(self, request, *args, **kwargs):
        serializer = AddknowledgeSerializer(data=request.data)
        if serializer.is_valid():
            knowledge = Knowledge()
            knowledge.k_user_id = serializer.data['user_id']
            user_id = serializer.data['user_id']
            user = LoginUser.objects.get(id=user_id)
            knowledge.k_user_name = user.username
            # knowledge.k_user_id = serializer.data['user_id']
            knowledge.k_title = serializer.data['k_title']
            knowledge.k_type = serializer.data['k_type']
            knowledge.k_content = serializer.data['k_content']
            # knowledge.k_tag = serializer.data['k_tag']
            knowledge.k_condition = serializer.data['k_condition']
            knowledge.k_date = datetime.datetime.now()
            knowledge.k_date = datetime.datetime.now()

            knowledge.save()
            k_id = knowledge.id
            print(k_id)
            files = request.FILES.getlist('image')
            # dirs = settings.MEDIA_ROOT + '/wmedia/%Y%m%d'
            for file in files:
                knowledgemediastore = KnowledgeMediaStore()
                knowledgemediastore.m_k_id = Knowledge.objects.get(id=knowledge.id)
                knowledgemediastore.m_k_filepath = file
                knowledgemediastore.m_type = "图片"
                knowledgemediastore.m_date = datetime.datetime.now()
                knowledgemediastore.save()
            response = {
                'message': ['创建成功'],
                # 'token':token
                'code': ["200"],
                'k_id': k_id
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class AddknowledgeDraft(GenericAPIView):
    '''
    添加知识库/行业资讯，需后台人员操作，类型k_type需限制为：知识库或行业资讯
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AddknowledgeSerializer

    def post(self, request, *args, **kwargs):
        serializer = AddknowledgeSerializer(data=request.data)
        if serializer.is_valid():
            knowledge = Knowledge()
            knowledge.k_user_id = serializer.data['user_id']
            user_id = serializer.data['user_id']
            user = LoginUser.objects.get(id=user_id)
            knowledge.k_user_name = user.username
            # knowledge.k_user_id = serializer.data['user_id']
            knowledge.k_title = serializer.data['k_title']
            knowledge.k_type = serializer.data['k_type']
            knowledge.k_content = serializer.data['k_content']
            # knowledge.k_tag = serializer.data['k_tag']
            knowledge.k_condition = serializer.data['k_condition']
            knowledge.k_date = datetime.datetime.now()
            knowledge.k_date = datetime.datetime.now()
            knowledge.k_draft = 1
            knowledge.save()
            k_id = knowledge.id
            print(k_id)
            files = request.FILES.getlist('image')
            # dirs = settings.MEDIA_ROOT + '/wmedia/%Y%m%d'
            for file in files:
                knowledgemediastore = KnowledgeMediaStore()
                knowledgemediastore.m_k_id = Knowledge.objects.get(id=knowledge.id)
                knowledgemediastore.m_k_filepath = file
                knowledgemediastore.m_type = "图片"
                knowledgemediastore.m_date = datetime.datetime.now()
                knowledgemediastore.save()
            response = {
                'message': ['创建成功'],
                # 'token':token
                'code': ["200"],
                'k_id': k_id
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Addenterprise(GenericAPIView):
    '''
    运维添加企业动态，需后台人员操作，类型k_type需限制为：知识库或行业资讯
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AddenterpriseSerializer

    def post(self, request, *args, **kwargs):
        serializer = AddenterpriseSerializer(data=request.data)
        if serializer.is_valid():
            file = request.FILES.get('e_image')
            enterprise = Enterprise()
            enterprise.e_user_id = serializer.data['user_id']
            user_id = serializer.data['user_id']
            user = LoginUser.objects.get(id=user_id)
            enterprise.e_user_name = user.username
            enterprise.e_title = serializer.data['e_title']
            enterprise.e_content = serializer.data['e_content']
            enterprise.e_image = file

            enterprise.e_date = datetime.datetime.now()
            enterprise.save()

            # dirs = settings.MEDIA_ROOT + '/wmedia/%Y%m%d'
            # for file in files:
            #     knowledgemediastore = KnowledgeMediaStore()
            #     knowledgemediastore.m_k_id = Knowledge.objects.get(id=enterprise.id)
            #     knowledgemediastore.m_k_filepath = file
            #     knowledgemediastore.m_type = "图片"
            #     knowledgemediastore.m_date = datetime.datetime.now()
            #     knowledgemediastore.save()
            response = {
                'message': ['创建成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Enterpriselist(GenericAPIView):
    '''
    查询企业动态列表,页数：page 每页条数：per_page
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条

        enterprises = Enterprise.objects.all().order_by('id')
        if not enterprises:
            response_data = {'code': ["926"], 'message': "目前不存在企业动态信息"}
            return HttpResponse(json.dumps(response_data))
        paginator = Paginator(enterprises, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data}

        return HttpResponse(json.dumps(response_data))



class Viewenterprise(GenericAPIView):
    '''
    查询知识库/行业资讯详情&&编辑知识库/行业资讯, 编辑功能post需后台人员身份  GET功能需传值知识库/行业资讯id： k_id
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditenterpriseSerializer()  # 权限相同

    def get(self, request, *args, **kwargs):
        id = request.GET.get('k_id')
        enterprise = Enterprise.objects.filter(id=id)
        if not enterprise:
            response0 = {
                'message': ['数据不存在'],
                'code': ["988"]
            }
            return Response(response0, status=200)
        objJson = serialize("json", Enterprise.objects.filter(id=id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))

    def post(self, request, *args, **kwargs):
        serializer = EditenterpriseSerializer(data=request.data)
        if serializer.is_valid():
            enterprise = Enterprise.objects.get(id=serializer.data['k_id'])

            enterprise.e_title = serializer.data['e_title']
            user_id = serializer.data['user_id']
            user = LoginUser.objects.get(id=user_id)
            enterprise.e_user_name = user.username
            enterprise.e_content = serializer.data['e_content']
            # enterprise.e_title = serializer.data['e_title']
            image = request.FILES.get('e_image')
            if image:
                instance = enterprise
                sender = enterprise.e_image
                enterprise_delete(sender, instance, **kwargs)
                enterprise.e_image = request.FILES.get('e_image')
                enterprise.e_date = datetime.datetime.now()
                enterprise.save()
            enterprise.e_date = datetime.datetime.now()
            enterprise.save()

            # files = request.FILES.getlist('image')
            # # dirs = settings.MEDIA_ROOT + '/wmedia/%Y%m%d'
            # for file in files:
            #     knowledgemediastore = KnowledgeMediaStore()
            #     knowledgemediastore.m_k_id = Knowledge.objects.get(id=knowledge.id)
            #     knowledgemediastore.m_k_filepath = file
            #     knowledgemediastore.m_type = "图片"
            #     knowledgemediastore.m_date = datetime.datetime.now()
            #     knowledgemediastore.save()
            response = {
                'message': ['修改成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Deleteenterprise(GenericAPIView):
    '''
    删除知识库/行业资讯，需后台人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditenterpriseSerializer

    def post(self, request, *args, **kwargs):
        serializer = EditenterpriseSerializer(data=request.data)
        if serializer.is_valid():
            enterprise = Enterprise.objects.get(id=serializer.data['k_id'])
            instance = enterprise
            sender = enterprise.e_image
            enterprise_delete(sender, instance, **kwargs)
            enterprise.delete()

            response = {
                'message': ['删除成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Uploadtech(GenericAPIView):
    '''
    工单上传技术方案.docx
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DocSerializer

    def post(self, request, *args, **kwargs):
        serializer = DocSerializer(data=request.data)
        if serializer.is_valid():
            file = request.FILES.get('tech')
            # print(file)
            userid = serializer.data['user_id']
            w_id = serializer.data['w_id']
            # print(userid)
            # print(w_id)
            tech = Doc()
            tech.docfile = file
            tech.doc_user_id = userid
            tech.w_id = w_id
            tech.doc_f_ip = localip + '/static/upload/'
            tech.doc_is_active = False
            tech.save()
            worksheet = Worksheet.objects.get(id=w_id)
            worksheet.w_doc_id = tech.id
            worksheet.save()
            doc = Doc.objects.get(doc_user_id=userid, w_id=w_id)
            # objJson = serialize("json", doc)
            # objStr = json.loads(objJson)
            # ip = doc.doc_f_ip
            # knowledgemediastore.m_k_ip = 'http://192.168.43.56:8000/static/upload/'
            # knowledgemediastore.m_k_ip = 'http://47.104.81.202:8002/static/upload/'
            # knowledgemediastore.m_type = "图片"
            # knowledgemediastore.m_date = datetime.datetime.now()
            # knowledgemediastore.save()
            #
            # id = knowledgemediastore.id
            # image = KnowledgeMediaStore.objects.get(id=id)

            ip_path = str(doc.doc_f_ip)
            file_path = str(doc.docfile)
            print(ip_path)
            print(file_path)
            response_data = {'code': ["200"], 'file_path': file_path}

            return Response(response_data)
        return Response(serializer.errors)


class Deletetech(GenericAPIView):
    '''
    删除技术方案
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DeleteDocSerializer

    def post(self, request, *args, **kwargs):
        serializer = DeleteDocSerializer(data=request.data)
        if serializer.is_valid():
            w_id = serializer.data['w_id']
            tech = Doc.objects.get(w_id=w_id)
            doc = tech.docfile
            if doc:
                instance = tech
                sender = tech.docfile
                doc_delete(sender, instance, **kwargs)
                # tech.docfile = None
                tech.save()
            tech.delete()
            worksheet = Worksheet.objects.get(id=w_id)
            worksheet.w_doc_id = None
            worksheet.w_status = '进行中'
            worksheet.save()
            response_data = {'code': ["200"], 'message': ['删除成功！']}

            return Response(response_data)
        return Response(serializer.errors)


class Unactivetechlist(GenericAPIView):
    '''
    删除技术方案
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = UnactivetechlistSerializer

    def post(self, request, *args, **kwargs):
        serializer = UnactivetechlistSerializer(data=request.data)
        if serializer.is_valid():
            tech = Doc.objects.filter(doc_is_active=False)
            print(tech)
            response_data = {'code': ["200"], 'message': ['删除成功！']}

            return Response(response_data)
        return Response(serializer.errors)


class Activetech(GenericAPIView):
    '''
    删除技术方案
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ActiveDocSerializer

    def post(self, request, *args, **kwargs):
        serializer = ActiveDocSerializer(data=request.data)
        if serializer.is_valid():
            w_id = serializer.data['w_id']
            tech = Doc.objects.get(w_id=w_id)
            tech.doc_is_active = True
            tech.save()
            worksheet = Worksheet.objects.get(id=w_id)
            worksheet.w_status = '已解决'
            worksheet.save()
            response_data = {'code': ["200"], 'message': ['审核通过']}

            return Response(response_data)
        return Response(serializer.errors)


def viewdoc(request):
    # print(BASE_DIR)
    w_id = request.GET.get('w_id')
    user_id = request.GET.get('user_id')
    print(w_id)
    if not w_id:
        response_data = {'code': ["966"], 'message': '工单不存在'}
        return HttpResponse(json.dumps(response_data))
    user = LoginUser.objects.filter(id=user_id)
    if not user:
        response_data = {'code': ["999"], 'message': '用户不存在或已停用'}
        return HttpResponse(json.dumps(response_data))
    user = LoginUser.objects.get(id=user_id)
    tech = Doc.objects.get(w_id=w_id)
    if user.u_type == "超级管理员" or user.id == tech.doc_user_id:
        sys = localip
        sys = str(sys)
        file_path = tech.docfile
        file_path = str(file_path)
        file_path = sys + '/static/upload/' + file_path
        response_data = {'code': ["200"], 'data': file_path}

        return HttpResponse(json.dumps(response_data))
    return render(request, '../static/docerror.html')


# def viewdoc(request):
#     # print(BASE_DIR)
#     w_id = request.GET.get('w_id')
#     user_id = request.GET.get('user_id')
#     print(w_id)
#     if not w_id:
#         response_data = {'code': ["966"], 'message': '工单不存在'}
#         return HttpResponse(json.dumps(response_data))
#     user = LoginUser.objects.filter(id=user_id)
#     if not user:
#         response_data = {'code': ["999"], 'message': '用户不存在或已停用'}
#         return HttpResponse(json.dumps(response_data))
#     user = LoginUser.objects.get(id=user_id)
#     tech = Doc.objects.get(w_id=w_id)
#     if user.u_type == "超级管理员" or user.id == tech.doc_user_id:
#         sys = str(Path(BASE_DIR))
#         print(sys)
#         file_path = tech.docfile
#         file_path = str(file_path)
#
#         print(file_path)
#         file_path = sys + '/static/upload/' + file_path
#         print(file_path)
#         load_html = PyDocX.to_html(file_path)
#         # print(load_html)
#         f = open("static/doc.html", 'w', encoding="utf-8")
#         # print(f)
#         f.write(load_html)
#         f.close()
#         return render(request, '../static/doc.html')
#     return render(request, '../static/docerror.html')


class Uploadimage(GenericAPIView):
    '''
    富文本编辑上传图片
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('image')
        knowledgemediastore = KnowledgeMediaStore()
        knowledgemediastore.m_k_filepath = file
        # knowledgemediastore.m_k_ip = 'http://192.168.43.56:8000/static/upload/'
        knowledgemediastore.m_k_ip = localip + '/static/upload/'
        knowledgemediastore.m_type = "图片"
        knowledgemediastore.m_date = datetime.datetime.now()
        knowledgemediastore.save()

        id = knowledgemediastore.id
        image = KnowledgeMediaStore.objects.get(id=id)

        ip_path = str(image.m_k_ip)
        file_path = str(image.m_k_filepath)

        response_data = {'errno': 0, 'ip': ip_path, 'data': [file_path]}

        return Response(response_data)

class Knowledgelist(GenericAPIView):
    '''
    查询知识库列表,需前端传值 type = '知识库' 或者 '行业资讯',页数：page 每页条数：per_page
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "知识库"
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条

        knowledges = Knowledge.objects.filter(k_type=type).order_by('k_thumbs_up').order_by('k_visit').order_by(
            '-k_date')
        if not knowledges:
            response_data = {'code': ["928"], 'message': "目前不存在知识库信息"}
            return HttpResponse(json.dumps(response_data))

        paginator = Paginator(knowledges, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data}

        return HttpResponse(json.dumps(response_data))

class MyKnowledgelist(GenericAPIView):
    '''
    查询知识库列表,需前端传值 type = '知识库' 或者 '行业资讯',页数：page 每页条数：per_page
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "知识库"
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条
        user_id = request.GET.get('user_id')
        knowledges = Knowledge.objects.filter(k_type=type, k_draft=0, k_user_id=user_id).order_by(
            'k_thumbs_up').order_by(
            'k_visit').order_by(
            '-k_date')
        paginator = Paginator(knowledges, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data,
                         'Mine': True}

        return HttpResponse(json.dumps(response_data))


class MyKnowledgeDraftlist(GenericAPIView):
    '''
    查询知识库列表,需前端传值 type = '知识库' 或者 '行业资讯',页数：page 每页条数：per_page
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "知识库"
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条
        user_id = request.GET.get('user_id')
        knowledges = Knowledge.objects.filter(k_type=type, k_draft=1, k_user_id=user_id).order_by(
            'k_thumbs_up').order_by(
            'k_visit').order_by(
            '-k_date')
        paginator = Paginator(knowledges, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data,
                         'Mine': True}

        return HttpResponse(json.dumps(response_data))


class KnowledgelistV2(GenericAPIView):
    '''
    查询行业资讯列表,需前端传值 type = '知识库' 或者 '行业资讯',页数：page 每页条数：per_page
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "行业资讯"
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条

        knowledges = Knowledge.objects.filter(k_type=type, k_draft=0).order_by('k_thumbs_up').order_by(
            'k_visit').order_by(
            '-k_date')
        paginator = Paginator(knowledges, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data,
                         'Mine': False}

        return HttpResponse(json.dumps(response_data))


class MyKnowledgelistV1(GenericAPIView):
    '''
    查询行业资讯列表,需前端传值 type = '知识库' 或者 '行业资讯',页数：page 每页条数：per_page
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "行业资讯"
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条
        user_id = request.GET.get('user_id')
        print(user_id)
        knowledges = Knowledge.objects.filter(k_type=type, k_draft=0, k_user_id=user_id).order_by(
            'k_thumbs_up').order_by(
            'k_visit').order_by(
            '-k_date')
        paginator = Paginator(knowledges, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data,
                         'Mine': True}

        return HttpResponse(json.dumps(response_data))


class MyKnowledgeDraftlistV1(GenericAPIView):
    '''
    查询行业资讯列表,需前端传值 type = '知识库' 或者 '行业资讯',页数：page 每页条数：per_page
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "行业资讯"
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条
        user_id = request.GET.get('user_id')
        knowledges = Knowledge.objects.filter(k_type=type, k_draft=1, k_user_id=user_id).order_by(
            'k_thumbs_up').order_by(
            'k_visit').order_by(
            '-k_date')
        paginator = Paginator(knowledges, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data}

        return HttpResponse(json.dumps(response_data))



class KnowledgelistV3(GenericAPIView):
    '''
    根据标签查询行业资讯列表,需前端传值标签k_tag  页数：page 每页条数：per_page
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "行业资讯"
        tag = request.GET.get('k_tag')
        # print(tag)
        tagg = Tag.objects.get(tag_name=tag)
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条

        knowledges = Knowledge.objects.filter(k_type=type).filter(k_verify=1).order_by('k_thumbs_up').order_by(
            'k_visit').order_by(
            '-k_date')
        if not knowledges:
            response_data = {'code': ["927"], 'message': "目前不存在行业资讯信息"}
            return HttpResponse(json.dumps(response_data))
        paginator = Paginator(knowledges, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data}

        return HttpResponse(json.dumps(response_data))


class KnowledgelistV4(GenericAPIView):
    '''
    查询最新的五条行业资讯
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "行业资讯"
        knowledges = Knowledge.objects.filter(k_type=type).filter(k_verify=1).order_by('-k_date')[:5]
        if not knowledges:
            response_data = {'code': ["927"], 'message': "目前不存在行业资讯信息"}
            return HttpResponse(json.dumps(response_data))
        objJson = serialize("json", knowledges)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr}

        return HttpResponse(json.dumps(response_data))


class KnowledgelistV5(GenericAPIView):
    '''
    查询最新的五条行业资讯
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "知识库"
        knowledges = Knowledge.objects.filter(k_type=type, k_draft=0).filter(k_verify=1).order_by('-k_date')[:5]
        objJson = serialize("json", knowledges)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr}

        return HttpResponse(json.dumps(response_data))


class Selectknoledgev1(GenericAPIView):
    '''
    查询知识库
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        key = request.GET.get('keywords')
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条
        type = "知识库"
        knowledges = Knowledge.objects.filter(k_type=type, k_draft=0).filter(k_title__icontains=key).filter(
            k_verify=1).order_by(
            '-k_date')
        if not knowledges:
            response_data = {'code': ["988"], 'message': ['数据不存在']}
            return HttpResponse(json.dumps(response_data))
        paginator = Paginator(knowledges, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data}

        return HttpResponse(json.dumps(response_data))


class Selectknoledgev2(GenericAPIView):
    '''
    查询知识库
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        key = request.GET.get('keywords')
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条
        type = "行业资讯"
        knowledges = Knowledge.objects.filter(k_type=type, k_draft=0).filter(k_title__icontains=key).filter(
            k_verify=1).order_by(
            '-k_date')
        if not knowledges:
            response_data = {'code': ["988"], 'message': ['数据不存在']}
            return HttpResponse(json.dumps(response_data))
        paginator = Paginator(knowledges, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data}

        return HttpResponse(json.dumps(response_data))


class Selectknoledgev3(GenericAPIView):
    '''
    小程序查询最热的三条知识库
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "知识库"
        knowledges = Knowledge.objects.filter(k_type=type, k_draft=0).filter(k_verify=1).order_by('-k_visit')[:3]
        objJson = serialize("json", knowledges)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr}

        return HttpResponse(json.dumps(response_data))


class Selectknoledgev4(GenericAPIView):
    '''
    小程序查询最热的三条行业资讯
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "行业资讯"
        knowledges = Knowledge.objects.filter(k_type=type, k_draft=0).filter(k_verify=1).order_by('-k_visit')[:3]
        objJson = serialize("json", knowledges)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr}

        return HttpResponse(json.dumps(response_data))


class Selectknoledgev5(GenericAPIView):
    '''
    小程序查询知识库列表
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        key = request.GET.get('keywords')
        type = "知识库"
        knowledges = Knowledge.objects.filter(k_type=type, k_draft=0).filter(k_title__icontains=key).filter(
            k_verify=1).order_by(
            '-k_date')
        if not knowledges:
            response_data = {'code': ["988"], 'message': ['数据不存在']}
            return HttpResponse(json.dumps(response_data))

        objJson = serialize("json", knowledges)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, }

        return HttpResponse(json.dumps(response_data))


def previousarticle(k_id, type):
    previous = Knowledge.objects.filter(id__lt=k_id, k_type=type, k_draft=0).order_by('id').first()
    if previous:
        previous = Knowledge.objects.filter(id__lt=k_id, k_type=type, k_draft=0).order_by('id').first()
        previous_id = previous.id
        return previous_id
    previous_id = None
    return previous_id


def nextarticle(k_id, type):
    next = Knowledge.objects.filter(id__gt=k_id, k_type=type, k_draft=0).order_by('id').first()
    if next:
        next = Knowledge.objects.filter(id__gt=k_id, k_type=type, k_draft=0).order_by('id').first()
        next_id = next.id
        return next_id
    next_id = None
    return next_id


class KnowledgelistFront(GenericAPIView):
    '''
    查询知识库列表,需前端传值 type = '知识库' 或者 '行业资讯',页数：page 每页条数：per_page
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "知识库"
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条
        print(page)
        print(per_page)
        knowledges = Knowledge.objects.filter(k_type=type, k_draft=0).filter(k_verify=1).order_by(
            'k_thumbs_up').order_by(
            'k_visit').order_by(
            '-k_date')
        print(knowledges)
        paginator = Paginator(knowledges, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data}

        return HttpResponse(json.dumps(response_data))


class KnowledgelistV2Front(GenericAPIView):
    '''
    查询行业资讯列表,需前端传值 type = '知识库' 或者 '行业资讯',页数：page 每页条数：per_page
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        type = "行业资讯"
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条

        knowledges = Knowledge.objects.filter(k_type=type, k_draft=0).filter(k_verify=1).order_by(
            'k_thumbs_up').order_by(
            'k_visit').order_by(
            '-k_date')
        paginator = Paginator(knowledges, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data}

        return HttpResponse(json.dumps(response_data))


class Viewknowledge(GenericAPIView):
    '''
    查询知识库与解决方案, GET功能需传值知识库/行业资讯id： k_id
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []  # 权限相同

    def get(self, request, *args, **kwargs):
        k_id = request.GET.get('k_id')
        user_id = request.GET.get('user_id')
        knowledge = Knowledge.objects.filter(id=k_id)
        if not knowledge:
            response0 = {
                'message': ['数据不存在'],
                'code': ["988"]
            }
            return Response(response0, status=200)
        knowledge = Knowledge.objects.get(id=k_id)
        type = knowledge.k_type
        knowledge.k_visit = knowledge.k_visit + 1
        knowledge.save()
        k = knowledge
        tag = k.tag.all()
        tagset = []
        for t in tag:
            tagset.append(t.tag_name)
        objJson = serialize("json", Knowledge.objects.filter(id=k_id))
        objStr = json.loads(objJson)
        objJson1 = serialize("json", Solution.objects.filter(s_k_id_id=k_id))
        objStr1 = json.loads(objJson1)

        previous = []
        next = []
        n = None
        dict1 = {'id': n, 'title': '没有上一篇文章'}
        dict2 = {'id': n, 'title': '没有下一篇文章'}
        previous_id = previousarticle(k_id, '知识库')
        if previous_id:
            dict1["id"] = previous_id
            previous_k = Knowledge.objects.get(id=previous_id)
            previous_k_title = previous_k.k_title
            dict1["title"] = previous_k_title
        previous.append(dict1)

        next_id = nextarticle(k_id, '知识库')
        if next_id:
            dict2["id"] = next_id
            next_k = Knowledge.objects.get(id=next_id)
            next_k_title = next_k.k_title
            dict2["title"] = next_k_title
        next.append(dict2)

        th = False
        thumb = Thumbs.objects.filter(thu_user_id=user_id, thu_k_id=k_id)
        if thumb:
            th = True
        co = False
        collect = knowledge.loginuser_set.filter(id=user_id, knowledge=knowledge)
        if collect:
            co = True
        response_data = {'code': ["200"], 'knowledge': objStr, 'solution': objStr1, 'thumbs': th, 'collect': co,
                         'next': next, 'previous': previous, 'tagset': tagset}
        return HttpResponse(json.dumps(response_data))


class Viewknowledge1(GenericAPIView):
    '''
    查询知识库与解决方案, GET功能需传值知识库/行业资讯id： k_id
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []  # 权限相同

    def get(self, request, *args, **kwargs):
        k_id = request.GET.get('k_id')
        user_id = request.GET.get('user_id')
        knowledge = Knowledge.objects.filter(id=k_id)
        if not knowledge:
            response0 = {
                'message': ['数据不存在'],
                'code': ["988"]
            }
            return Response(response0, status=200)
        knowledge = Knowledge.objects.get(id=k_id)
        knowledge.k_visit = knowledge.k_visit + 1
        knowledge.save()
        k = knowledge
        tag = k.tag.all()
        tagset = []
        for t in tag:
            tagset.append(t.tag_name)
        objJson = serialize("json", Knowledge.objects.filter(id=k_id))
        objStr = json.loads(objJson)

        previous = []
        next = []
        n = None
        dict1 = {'id': n, 'title': '没有上一篇文章'}
        dict2 = {'id': n, 'title': '没有下一篇文章'}
        previous_id = previousarticle(k_id, '行业资讯')
        if previous_id:
            dict1["id"] = previous_id
            previous_k = Knowledge.objects.get(id=previous_id)
            previous_k_title = previous_k.k_title
            dict1["title"] = previous_k_title
        previous.append(dict1)

        next_id = nextarticle(k_id, '行业资讯')
        if next_id:
            dict2["id"] = next_id
            next_k = Knowledge.objects.get(id=next_id)
            next_k_title = next_k.k_title
            dict2["title"] = next_k_title
        next.append(dict2)

        th = False
        thumb = Thumbs.objects.filter(thu_user_id=user_id, thu_k_id=k_id)
        if thumb:
            th = True
        co = False
        collect = knowledge.loginuser_set.filter(id=user_id, knowledge=knowledge)
        if collect:
            co = True
        response_data = {'code': ["200"], 'knowledge': objStr, 'thumbs': th, 'collect': co, 'next': next,
                         'previous': previous, 'tagset': tagset}
        return HttpResponse(json.dumps(response_data))


class Collectknowledge(GenericAPIView):
    '''
    收藏知识库与解决方案
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = CollectknowledgeSerializer()

    def post(self, request, *args, **kwargs):
        serializer = CollectknowledgeSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['user_id']
            k_id = serializer.data['k_id']
            user = LoginUser.objects.get(id=user_id)
            user.knowledge.add(Knowledge.objects.get(id=k_id))

            response = {
                'message': ['收藏成功！'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class UnCollectknowledge(GenericAPIView):
    '''
    取消收藏知识库与解决方案
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = UnCollectknowledgeSerializer()

    def post(self, request, *args, **kwargs):
        serializer = UnCollectknowledgeSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['user_id']
            k_id = serializer.data['k_id']
            user = LoginUser.objects.get(id=user_id)
            user.knowledge.remove(Knowledge.objects.get(id=k_id))

            response = {
                'message': ['取消收藏成功！'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class ViewCollection(GenericAPIView):
    '''
    查看收藏知识库/行业资讯列表
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ViewCollectionSerializer()

    def post(self, request, *args, **kwargs):
        serializer = ViewCollectionSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['user_id']
            # k_id = serializer.data['k_id']
            user = LoginUser.objects.get(id=user_id)
            collection = user.knowledge.all()

            print(collection)
            objJson = serialize("json", collection)
            objStr = json.loads(objJson)
            response = {
                'code': ["200"],
                'data': objStr,
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class ViewCollectionV1(GenericAPIView):
    '''
    知识库/行业资讯收藏夹
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ViewCollectionSerializerv1()

    def post(self, request, *args, **kwargs):
        serializer = ViewCollectionSerializerv1(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['user_id']
            key = serializer.data['key']
            # k_id = serializer.data['k_id']
            user = LoginUser.objects.get(id=user_id)
            collection1 = user.knowledge.filter(k_type=key)
            # collection2 = user.knowledge.filter(k_type='行业资讯')

            print(collection1)
            objJson = serialize("json", collection1)
            objStr = json.loads(objJson)
            response = {
                'code': ["200"],
                'knowledge': objStr,
                # 'knowledge1': objStr1,
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Thumbknowledge(GenericAPIView):
    '''
    点赞知识库与解决方案
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ThumbknowledgeSerializer()

    def post(self, request, *args, **kwargs):
        serializer = ThumbknowledgeSerializer(data=request.data)
        if serializer.is_valid():
            thumb = Thumbs()
            thumb.thu_user_id = serializer.data['user_id']
            k_id = serializer.data['k_id']
            k = Knowledge.objects.get(id=k_id)
            thumb.thu_k_id = k
            thumb.save()
            # knowledge = Knowledge.objects.get(id=serializer.data['k_id'])
            k.k_thumbs_up = k.k_thumbs_up + 1

            k.save()

            response = {
                'message': ['操作成功！'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Editknowledge(GenericAPIView):
    '''
    查询知识库/行业资讯详情&&编辑知识库/行业资讯, 编辑功能post需后台人员身份  GET功能需传值知识库/行业资讯id： k_id
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditknowledgeSerializer()  # 权限相同

    def get(self, request, *args, **kwargs):
        k_id = request.GET.get('k_id')
        user_id = request.GET.get('user_id')
        knowledge = Knowledge.objects.filter(id=k_id)
        if not knowledge:
            response0 = {
                'message': ['数据不存在'],
                'code': ["988"]
            }
            return Response(response0, status=200)
        knowledge = Knowledge.objects.get(id=k_id)
        knowledge.k_visit = knowledge.k_visit + 1
        knowledge.save()
        th = False
        thumb = Thumbs.objects.filter(thu_user_id=user_id, thu_k_id=k_id)
        if thumb:
            th = True
        co = False
        collect = knowledge.loginuser_set.filter(id=user_id, knowledge=knowledge)
        if collect:
            co = True
        objJson = serialize("json", Knowledge.objects.filter(id=k_id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr, 'thumbs': th, 'collect': co}
        return HttpResponse(json.dumps(response_data))

    def post(self, request, *args, **kwargs):
        serializer = EditknowledgeSerializer(data=request.data)
        if serializer.is_valid():
            knowledge = Knowledge.objects.get(id=serializer.data['k_id'])

            knowledge.k_title = serializer.data['k_title']
            user_id = serializer.data['user_id']
            user = LoginUser.objects.get(id=user_id)
            knowledge.k_user_name = user.username
            knowledge.k_content = serializer.data['k_content']
            knowledge.k_draft = 0
            # knowledge.k_tag = serializer.data['k_tag']
            knowledge.k_date = datetime.datetime.now()
            knowledge.save()

            files = request.FILES.getlist('image')
            # dirs = settings.MEDIA_ROOT + '/wmedia/%Y%m%d'
            for file in files:
                knowledgemediastore = KnowledgeMediaStore()
                knowledgemediastore.m_k_id = Knowledge.objects.get(id=knowledge.id)
                knowledgemediastore.m_k_filepath = file
                knowledgemediastore.m_type = "图片"
                knowledgemediastore.m_date = datetime.datetime.now()
                knowledgemediastore.save()
            response = {
                'message': ['修改成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Deleteknowledge(GenericAPIView):
    '''
    删除知识库/行业资讯，需后台人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditknowledgeSerializer

    def post(self, request, *args, **kwargs):
        serializer = EditknowledgeSerializer(data=request.data)
        if serializer.is_valid():
            knowledge = Knowledge.objects.get(id=serializer.data['k_id'])
            knowledge.delete()

            response = {
                'message': ['删除成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Verfiy(GenericAPIView):
    '''
    审核知识库/行业资讯，需后台人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = VerfiySerializer

    def post(self, request, *args, **kwargs):
        serializer = VerfiySerializer(data=request.data)
        if serializer.is_valid():
            knowledge = Knowledge.objects.get(id=serializer.data['k_id'])
            knowledge.k_verify = serializer.data['k_verify']
            knowledge.save()

            response = {
                'message': ['审核成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Addsolution(GenericAPIView):
    '''
    添加知识库/行业资讯解决方案，需后台人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AddsolutionSerializer

    def post(self, request, *args, **kwargs):
        serializer = AddsolutionSerializer(data=request.data)
        if serializer.is_valid():
            solution = Solution()
            solution.s_user_id = LoginUser.objects.get(id=serializer.data['user_id'])
            solution.s_k_id = Knowledge.objects.get(id=serializer.data['s_k_id'])
            user_id = serializer.data['user_id']
            user = LoginUser.objects.get(id=user_id)
            solution.s_user_name = user.username
            solution.s_title = serializer.data['s_title']
            solution.s_type = serializer.data['s_type']
            solution.s_content = serializer.data['s_content']
            solution.s_date = datetime.datetime.now()
            solution.save()
            k = Knowledge.objects.get(id=serializer.data['s_k_id'])
            k.k_status = "True"
            k.save()
            response = {
                'message': ['解决方案创建成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Viewsolution(GenericAPIView):
    '''
    查看知识库/行业资讯解决方案&&编辑知识库/行业资讯解决方案,需要后台人员操作,GET 需要传值：知识库id s_k_id
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditsolutionSerializer  # 权限要求相同

    def get(self, request, *args, **kwargs):
        s_k_id = request.GET.get('s_k_id')
        print(s_k_id)
        # solution = Solution.objects.filter(id=s_k_id)
        solution = Solution.objects.filter(s_k_id_id=s_k_id)
        if not solution:
            response1 = {
                'message': ['数据不存在'],
                'code': ["988"]
            }
            return Response(response1, status=200)
        objJson = serialize("json", Solution.objects.filter(s_k_id_id=s_k_id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))

    def post(self, request, *args, **kwargs):
        serializer = EditsolutionSerializer(data=request.data)
        if serializer.is_valid():
            solution = Solution.objects.get(id=serializer.data['s_id'])
            solution.s_user_id = LoginUser.objects.get(id=serializer.data['user_id'])
            solution.s_k_id = Knowledge.objects.get(id=serializer.data['s_k_id'])
            user_id = serializer.data['user_id']
            user = LoginUser.objects.get(id=user_id)
            solution.s_user_name = user.username
            solution.s_title = serializer.data['s_title']
            solution.s_type = serializer.data['s_type']
            solution.s_content = serializer.data['s_content']
            solution.s_date = datetime.datetime.now()
            solution.save()

            response = {
                'message': ['解决方案修改成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Deletesolution(GenericAPIView):
    '''
    添加知识库/行业资讯解决方案，需后台人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AddsolutionSerializer  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = AddsolutionSerializer(data=request.data)
        if serializer.is_valid():
            solution = Solution.objects.get(id=serializer.data['s_id'])
            solution.delete()
            k = Knowledge.objects.get(id=serializer.data['s_k_id'])
            k.k_status = "False"
            k.save()
            response = {
                'message': ['解决方案删除成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Employeelist(GenericAPIView):
    '''
    展示后台全部员工，需要admin操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EmployeelistSerializer  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = EmployeelistSerializer(data=request.data)
        if serializer.is_valid():
            objJson = serialize("json",
                                LoginUser.objects.filter(
                                    Q(u_type='运营') | Q(u_type='运维顾问') | Q(u_type='客服运营') | Q(u_type='超级管理员')).filter(
                                    is_active=1).order_by('u_type'))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


class test(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = []  # 权限要求相同

    def get(self, request, *args, **kwargs):
        s_k_id = 6
        print(s_k_id)
        # solution = Solution.objects.filter(id=s_k_id)
        solution = Solution.objects.filter(s_k_id_id=s_k_id)
        if not solution:
            response1 = {
                'message': ['数据不存在'],
                'code': ["988"]
            }
            return Response(response1, status=200)
        objJson = serialize("json", Solution.objects.filter(s_k_id_id=s_k_id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))


# def login1(request):
#     return render(request, 'post.html')


def do_login(request):
    files = request.FILES.getlist('image')
    for file in files:
        print(file)
        media = Test()
        media.t = file
        media.save()
    response = HttpResponse("asdh")

    return response


class Wisepasstoken(GenericAPIView):
    """
    查看当前研华token，需要登录后操作
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = WisepasstokenSerializer  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = WisepasstokenSerializer(data=request.data)
        if serializer.is_valid():
            objJson = serialize("json", WisePassToken.objects.get(id=1))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# class Editwisepasstoken(GenericAPIView):
#     '''
#     更新研华token，需要后台人员操作
#     '''
#     authentication_classes = []
#     permission_classes = []
#     serializer_class = WisepasstokenSerializerV2  # 权限要求相同
#
#     def post(self, request, *args, **kwargs):
#         serializer = WisepasstokenSerializerV2(data=request.data)
#         if serializer.is_valid():
#             w = WisePassToken.objects.get(id=1)
#             w.token = serializer.data['token']
#             w.save()
#             response = {
#                 'code': ['200'],
#                 'message': ['更新成功']
#             }
#         return Response(serializer.errors)


def getnoneuser(request):
    users = LoginUser.objects.filter(u_type='待分配')
    # if not users:
    #     response = {
    #         'message': ['当前无用户'],
    #         'code': ["961"]
    #     }
    #
    #     return HttpResponse(response, status=200)

    objJson = serialize("json", users)
    objStr = json.loads(objJson)
    response_data = {'code': ["200"], 'data': objStr}
    return HttpResponse(json.dumps(response_data))


class ManagerCreateCompany(GenericAPIView):
    '''
    超级管理员创建公司
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = CreatecompanySerializerv2

    def post(self, request, *args, **kwargs):
        serializer = CreatecompanySerializerv2(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data["user_id"]  # 获取创建1人ID
            company_name = serializer.data['company_name']
            company_address = serializer.data['company_address']
            company_mailbox = serializer.data['company_mailbox']
            company_zip_code = serializer.data['company_zip_code']
            company_content = serializer.data['company_content']
            company_icon = request.FILES.get("company_icon")
            company_register_number = serializer.data['company_register_number']
            company_license = request.FILES.get('company_license')
            company_begin_date = serializer.data["company_begin_date"]
            company_office_number = serializer.data["company_office_number"]
            # company_boss_ID_card = request.FILES.get("company_boss_ID_card")
            company_business_range = serializer.data["company_business_range"]
            company_register_money = serializer.data["company_register_money"]
            # company_organize_code = serializer.data["company_organize_code"]

            company = Company()
            # users = LoginUser()
            user = LoginUser.objects.get(id=user_id)
            company.c_u_id = user  # 外键指向的是一个对象 不是属性
            company.company_name = company_name
            company.company_mailbox = company_mailbox
            company.company_address = company_address
            company.company_zip_code = company_zip_code
            company.company_content = company_content
            company.company_register_number = company_register_number
            company.company_license = company_license
            company.company_icon = company_icon
            company.active = 0
            company.company_begin_date = company_begin_date
            company.company_office_number = company_office_number
            # company.company_boss_ID_card = company_boss_ID_card
            company.company_business_range = company_business_range
            company.company_register_money = company_register_money
            # company.company_organize_code = company_organize_code

            company.save()

            user.u_company_id = company.id  # 添加公司id到用户表
            user.is_staff = 1
            user.u_type = "公司管理员"
            user.save()
            response = {
                'message': ['公司创建成功，等待平台审核。'],
                # 'token':token
                'code': ["200"]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


# 用户和知识库通过标签匹配
class UKMactchTag(GenericAPIView):
    '''
    用户和知识库通过标签匹配
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def post(self, request, *args, **kwargs):
        serializer = UKMactchTagSerializer(data=request.data)
        if serializer.is_valid():
            # 1 找用户
            page = serializer.data['page']  # 第几页
            page = int(page)
            per_page = serializer.data['per_page']
            per_page = int(per_page)  # 每页多少条
            user_id = serializer.data['user_id']
            if user_id:
                # user_id = serializer.data["user_id"]
                loginuser = LoginUser.objects.get(id=user_id)
                # 2 找用户的标签
                a = Tag.objects.filter(loginuser=loginuser)
                if not a:
                    response_data = {'code': ["956"], 'message': ["您尚未设置关注标签"]}

                    return HttpResponse(json.dumps(response_data))
                # 3 for 找到所有标签的知识库

                knowledges = Knowledge.objects.filter(tag__in=a, k_type='知识库', k_draft=0).filter(
                    k_verify=1).distinct().order_by(
                    'k_thumbs_up').order_by('k_visit').order_by('-k_date')
                # print(knowledges)
                if not knowledges:
                    response_data = {'code': ["957"], 'message': ["您关注的标签下尚未存在知识库"]}

                    return HttpResponse(json.dumps(response_data))
                paginator = Paginator(knowledges, per_page)

                total_page = paginator.num_pages
                total_data = paginator.count

                page_object = paginator.page(page)
                objJson = serialize("json", page_object)
                objStr = json.loads(objJson)
                # 4 返回所有的知识库给用户
                # objJson = serialize("json", knowledges)
                # objStr = json.loads(objJson)
                response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data}
                return HttpResponse(json.dumps(response_data))

        return Response(serializer.errors)


# 用户和行业资讯通过标签匹配
class UKMactchTag2(GenericAPIView):
    '''
    用户和行业资讯通过标签匹配
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def post(self, request, *args, **kwargs):
        serializer = UKMactchTagSerializer(data=request.data)
        if serializer.is_valid():
            # 1 找用户
            page = serializer.data['page']  # 第几页
            page = int(page)
            per_page = serializer.data['per_page']
            per_page = int(per_page)  # 每页多少条
            user_id = serializer.data['user_id']
            if user_id:
                # user_id = serializer.data["user_id"]
                loginuser = LoginUser.objects.get(id=user_id)
                # 2 找用户的标签
                a = Tag.objects.filter(loginuser=loginuser)
                if not a:
                    response_data = {'code': ["956"], 'message': ["您尚未设置关注标签"]}

                    return HttpResponse(json.dumps(response_data))

                knowledges = Knowledge.objects.filter(tag__in=a, k_type='行业资讯', k_draft=0).filter(
                    k_verify=1).distinct().order_by(
                    'k_thumbs_up').order_by('k_visit').order_by('-k_date')
                if not knowledges:
                    # knowledges = Knowledge.objects.filter(k_type='知识库').order_by('k_thumbs_up').order_by(
                    #     'k_visit').order_by(
                    #     '-k_date')
                    # paginator = Paginator(knowledges, per_page)
                    #
                    # total_page = paginator.num_pages
                    # total_data = paginator.count
                    #
                    # page_object = paginator.page(page)
                    # objJson = serialize("json", page_object)
                    # objStr = json.loads(objJson)

                    response_data = {'code': ["957"], 'message': ["您关注的标签下尚未存在行业资讯"]}

                    return HttpResponse(json.dumps(response_data))
                paginator = Paginator(knowledges, per_page)

                total_page = paginator.num_pages
                total_data = paginator.count

                page_object = paginator.page(page)
                objJson = serialize("json", page_object)
                objStr = json.loads(objJson)
                # 4 返回所有的知识库给用户
                # objJson = serialize("json", knowledges)
                # objStr = json.loads(objJson)
                response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data}
                return HttpResponse(json.dumps(response_data))
            # print(1)
            # knowledges = Knowledge.objects.filter(k_type='知识库').order_by('k_thumbs_up').order_by('k_visit').order_by(
            #     '-k_date')
            # paginator = Paginator(knowledges, per_page)
            #
            # total_page = paginator.num_pages
            # total_data = paginator.count
            #
            # page_object = paginator.page(page)
            # objJson = serialize("json", page_object)
            # objStr = json.loads(objJson)

        return Response(serializer.errors)


class KAddTag(APIView):
    """
    知识库/行业资讯加标签
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def post(self, request, *args, **kwargs):
        response = request.body.decode()
        r_str = json.loads(response)
        tags = jsonpath(r_str, '$.tags[*]')
        knowledge_id = jsonpath(r_str, '$.knowledge_id')

        knowledge_id = str(knowledge_id)
        knowledge_id = knowledge_id.replace('[', '')
        knowledge_id = knowledge_id.replace(']', '')
        knowledge_id = knowledge_id.replace(']', '')

        length = len(tags)
        i = 0
        for i in range(length):
            knowledge = Knowledge.objects.get(id=knowledge_id)
            knowledge.tag.add(Tag.objects.get(tag_name=tags[i]))
        response = {
            'message': ['添加成功'],
            'code': ["200"]
        }
        return Response(response)


ip = 'http://124.164.247.45:4694/'


# 为项目导入采集设备
def getdevice(request):
    """
    为项目导入采集设备数据
    :param request: 项目ID p_id, 采集设备在webaccess中的名称 device_name
    :return:
    """
    url = ip + 'WaWebService/JSON/DeviceDetail/'
    p_id = request.GET.get('p_id')
    print(p_id)
    device = request.GET.get('device_name')
    p = Project.objects.filter(id=p_id).filter(p_active=1)
    c0 = Collectdevice.objects.filter(cd_name=device)
    if c0:
        response = {
            'message': ['采集设备已被占用'],
            'code': ["947"]
        }
        return HttpResponse(json.dumps(response))
    if not p:
        response_data = {'code': ["995"], 'message': ["项目不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    p = Project.objects.get(id=p_id, p_active=1)
    c = p.p_c_id
    print(c)
    node_name = 'Node1'
    project_name = 'test'
    comport = '1'
    device = device
    url_child = url + project_name + '/' + node_name + '/' + comport + '/' + device
    print(url_child)
    resp = requests.get(url_child, auth=HTTPBasicAuth('admin', '12345678'), timeout=20)
    response = resp.content.decode()  # str
    print(response)

    r_str = json.loads(response)  # dict
    DeviceName = jsonpath(r_str, '$.Device.DeviceName')  # 设备名

    DeviceName = DeviceName[0]  # 设备名
    print(DeviceName)
    if DeviceName is None:
        response = {
            'message': ['采集设备不存在'],
            'code': ["946"]
        }
        return HttpResponse(json.dumps(response))
    PortNumber = jsonpath(r_str, '$.Device.PortNumber')  # 设备端口
    PortNumber = PortNumber[0]
    Description = jsonpath(r_str, '$.Device.Description')  # 设备描述
    Description = Description[0]  # 设备名
    UnitNumber = jsonpath(r_str, '$.Device.UnitNumber')  # 设备小组
    UnitNumber = UnitNumber[0]  # 设备名
    DeviceType = jsonpath(r_str, '$.Device.DeviceType')  # 设备类型
    DeviceType = DeviceType[0]  # 设备名
    Primary_IPAddress = jsonpath(r_str, '$..Primary.IPAddress')  # 主通讯IP
    Primary_IPAddress = Primary_IPAddress[0]  # 设备名
    Primary_PortNumber = jsonpath(r_str, '$..Primary.PortNumber')  # 主通讯端口
    Primary_PortNumber = Primary_PortNumber[0]  # 设备名
    Primary_DeviceAddress = jsonpath(r_str, '$..Primary.DeviceAddress')  # 主通讯设备地址
    Primary_DeviceAddress = Primary_DeviceAddress[0]  # 设备名
    Seconday_IPAddress = jsonpath(r_str, '$..Secondary.IPAddress')  # 副通讯IP
    Seconday_IPAddress = Seconday_IPAddress[0]  # 设备名
    Seconday_PortNumber = jsonpath(r_str, '$..Secondary.PortNumber')  # 副通讯端口
    Seconday_PortNumber = Seconday_PortNumber[0]  # 设备名
    Seconday_DeviceAddress = jsonpath(r_str, '$..Secondary.DeviceAddress')  # 副通讯设备地址
    Seconday_DeviceAddress = Seconday_DeviceAddress[0]  # 设备名
    collectdevice = Collectdevice()
    collectdevice.cd_p_id = p
    collectdevice.cd_c_id = c
    collectdevice.cd_name = DeviceName
    collectdevice.cd_port_number = PortNumber
    collectdevice.cd_description = Description
    collectdevice.cd_unit_number = UnitNumber
    collectdevice.cd_device_type = DeviceType
    collectdevice.cd_primary_ip = Primary_IPAddress
    collectdevice.cd_primary_port = Primary_PortNumber
    collectdevice.cd_primary_address = Primary_DeviceAddress
    collectdevice.cd_secondary_ip = Seconday_IPAddress
    collectdevice.cd_secondary_port = Seconday_PortNumber
    collectdevice.cd_secondary_address = Seconday_DeviceAddress
    collectdevice.save()
    c = Collectdevice.objects.filter(cd_name=DeviceName)
    if not c:
        response = {
            'message': ['添加采集设备失败成功'],
            'code': ["948"]
        }
        return HttpResponse(json.dumps(response))
    objJson = serialize("json", c)
    objStr = json.loads(objJson)
    response_data = {'code': ["200"], 'data': objStr}
    return HttpResponse(json.dumps(response_data))


def gettags(request):
    """
    为机械设备导入机械设备参数
    :param request: 机械设备ID d_id, 采集设备在webaccess中的名称 device_name
    :return:
    """
    url = ip + 'WaWebService/JSON/TagList/'
    now = datetime.datetime.now()
    now = str(now)
    print('进行中' + now)
    # time.sleep(10)
    # ports = Port.objects.all()
    # cd_id = request.GET.get('cd_id')
    cd_name = request.GET.get('cd_name')
    d = Collectdevice.objects.filter(cd_name=cd_name)
    if not d:
        response_data = {'code': ["946"], 'message': ["采集设备不存在"]}
        return HttpResponse(json.dumps(response_data))
    d = Collectdevice.objects.get(cd_name=cd_name)  # 机械设备
    # device = Device.objects.get(d_c_id=d.id)
    # deviceid = device.id
    device = d.cd_name
    # c = p.p_c_id
    # print(c)
    # devices = Device.objects.filter(d_p_id_id=p_id)
    node_name = 'Node1'
    project_name = 'test'
    comport = '1'
    device = cd_name
    url_child = url + project_name + '/' + node_name + '/' + comport + '/' + device
    print(url_child)
    resp = requests.get(url_child, auth=HTTPBasicAuth('admin', '12345678'), timeout=20)
    response = resp.content.decode()  # str

    print(response)
    r_str = json.loads(response)  # dict
    r = jsonpath(r_str, '$.Tags.*')  # 设备名
    print(r)
    for m in r:
        tag = Data.objects.filter(d_name=m['Name'])
        if not tag:
            tag = Data()
            tag.d_name = m['Name']
            # print(m['Name'])
            tag.d_description = m['Description']
            # tag.d_unit_number = m['UnitNumber']
            tag.d_cd_id = d
            # tag.d_d_id_id = deviceid
            tag.save()
    now = datetime.datetime.now()
    now = str(now)
    print('完成' + now)
    response = {
        'message': ['参数添加成功'],
        'code': ["200"]
    }
    return HttpResponse(json.dumps(response))


def threeinone(request):
    """
    对某设备的所有参数组 进行单独的webaccess数据获取，并将三个数据进行判断取其一返回前端
    :param request: 机械设备ID d_id
    :return:
    """
    now = datetime.datetime.now()
    print(now)
    url = ip + 'WaWebService/JSON/GetDataLog/'
    # ports = Port.objects.all()
    d_id = request.GET.get('d_id')
    d = Device.objects.filter(id=d_id)
    if not d:
        response_data = {'code': ["995"], 'message': ["项目不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    d = Device.objects.get(id=d_id)
    headers = {"Content-Type": "application/json"}

    time = timedelta(sign='n', value=-1, dt=now)
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    # print(time)
    # print(time)
    groups = DataGroup.objects.filter(dg_d_id=d)
    a = []
    for group in groups:
        StartTime = time
        IntervalType = 'H'
        Interval = '1'
        Records = '1'
        DataType = '3'
        node_name = 'Node1'
        project_name = 'test'
        url_child = url + project_name + '/' + node_name
        Name = data.d_name
        data = json.dumps({
            "StartTime": StartTime,
            "IntervalType": IntervalType,
            "Interval": Interval,
            "Records": Records,
            "Tags": [{
                "Name": Name,
                "DataType": DataType
            }]
        })
        print(url_child)
        resp = requests.post(url_child, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'), timeout=20)
        response = resp.content.decode()  # str
        # print(response)
        r_str = json.loads(response)  # dict
        r = jsonpath(r_str, '$..Values.[0]')  # 设备名
        # print(r)
        r = str(r)
        r = r.replace("['", "")
        r = r.replace("']", "")
        a.append(r)
    now = datetime.datetime.now()
    print(now)
    print(a)
    b = dict(Counter(a))
    print(b)
    c = [key for key, value in b.items() if value > 1]
    c = int(c)
    now = datetime.datetime.now()
    print(now)

    response = {
        'message': ['添加成功'],
        'code': ["200"]
    }
    return HttpResponse(json.dumps(response))


def threeinone2(request):
    """
    对某设备的所有参数组 进行单独的webaccess数据获取，并将三个数据进行判断取其一返回前端
    :param request: 机械设备ID d_id
    :return:
    """
    i = 0
    datas = Data.objects.filter(d_nickname=1)
    for date in datas:
        i += 1
    i = str(i)
    now = datetime.datetime.now()
    print(now)
    ProjectName = 'test'
    url = ip + 'WaWebService/Json/SubscribeRealTimeTag' + '/' + ProjectName
    headers = {"Content-Type": "application/json"}
    # request数据格式,Total指有几个tag
    format_header0 = '{"Interval":1,"Records":1,"Total":'
    format_header0 = format_header0 + i
    format_header = format_header0 + ',"Tags": '
    format_tail = '}'
    taglist = []
    for data in datas:
        name = data.d_name
        taglistchild = {"Name": str(name)}
        taglist.append(taglistchild)
    format_body = str(taglist)
    format = format_header + format_body + format_tail
    format = str(format)
    format = format.replace("'", '"')  # request里必须使用双引号
    data = json.loads(format)  # 必须先将str变成Json
    data = json.dumps(data)  # 再将Json变成str，这样才能被requests模块正确使用
    # 发送带身份验证的post请求
    resp = requests.post(url, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'), timeout=10)
    response = resp.content.decode()  # str
    r_str = json.loads(response)  # dict
    v = jsonpath(r_str, '$.SubscriptionID')  # list
    v = str(v)  # 获取到id
    v = v.replace("[", '')
    v = v.replace("]", '')

    # 开始获取实时值
    data1 = json.dumps({
        "SubscriptionID": v
    })
    print(v)
    a = []
    url1 = ip + 'WaWebService/Json/GetRealTimeTagValue' + '/' + ProjectName
    resp1 = requests.post(url1, headers=headers, data=data1, auth=HTTPBasicAuth('admin', '12345678'), timeout=10)
    response1 = resp1.content.decode()  # str
    r_str1 = json.loads(response1)  # dict
    realtimevalue = jsonpath(r_str1, '$..Values.*')  # list
    realtimetag = jsonpath(r_str1, '$.RealTimeTagValue..Name')
    now = datetime.datetime.now()
    print(now)
    for r in realtimevalue:
        r = str(r)
        r = r.replace("['", "")
        r = r.replace("']", "")
        r = 1
        a.append(r)
    print(r)
    print(realtimetag)
    # tests = list(zip(realtimetag, realtimevalue))
    b = dict(Counter(a))
    print(b)
    c = [key for key, value in b.items() if value > 1]
    c = c[0]

    c = int(c)
    print(c)
    now = datetime.datetime.now()
    print(now)

    data2 = json.dumps({
        "UnsubscriptionID": 15
    })
    # print(v)
    url2 = ip + 'WaWebService/Json/UnsubscribeRealTimeTag' + '/' + ProjectName
    resp1 = requests.post(url2, headers=headers, data=data2, auth=HTTPBasicAuth('admin', '12345678'), timeout=10)
    now = datetime.datetime.now()
    print(now)
    response = {
        'message': ['添加成功'],
        'code': ["200"]
    }
    return HttpResponse(json.dumps(response))


def threeinone3(device_id):
    """
    对某设备的所有参数组 进行单独的webaccess数据获取，并将三个数据进行判断取其一返回前端
    :param request: 机械设备ID device_id
    :return:
    """
    i = 0
    datas = Data.objects.filter(d_d_id_id=device_id)
    print(datas)
    for data in datas:
        i += 1
    i = str(i)
    now = datetime.datetime.now()
    time = now.strftime('%Y-%m-%d %H:%M:%S')
    ProjectName = 'test'
    url = ip + 'WaWebService/Json/SubscribeRealTimeTag' + '/' + ProjectName
    headers = {"Content-Type": "application/json"}
    # request数据格式,Total指有几个tag
    format_header0 = '{"Interval":1,"Records":1,"Total":'
    format_header0 = format_header0 + i
    format_header = format_header0 + ',"Tags": '
    format_tail = '}'

    taglist = []
    for data in datas:
        name = data.d_name
        taglistchild = {"Name": str(name)}
        taglist.append(taglistchild)
    format_body = str(taglist)
    http_format = format_header + format_body + format_tail
    http_format = str(http_format)
    http_format = http_format.replace("'", '"')  # request里必须使用双引号
    data = json.loads(http_format)  # 必须先将str变成Json
    data = json.dumps(data)  # 再将Json变成str，这样才能被requests模块正确使用
    print(data)
    # 发送带身份验证的post请求
    resp = requests.post(url, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'), timeout=60)
    response = resp.content.decode()  # str
    r_str = json.loads(response)  # dict
    v = jsonpath(r_str, '$.SubscriptionID')  # list
    v = str(v)  # 获取到id
    v = v.replace("[", '')
    v = v.replace("]", '')

    # 开始获取实时值
    data1 = json.dumps({
        "SubscriptionID": v
    })
    # print(v)
    # print(data1)
    try:
        url1 = ip + 'WaWebService/Json/GetRealTimeTagValue' + '/' + ProjectName
        # print(url1)
        resp1 = requests.post(url1, headers=headers, data=data1, auth=HTTPBasicAuth('admin', '12345678'), timeout=60)
        # print(resp1)
        response1 = resp1.content.decode()  # str
        r_str1 = json.loads(response1)  # dict
        # print(r_str1)
        realtimevalue = jsonpath(r_str1, '$..Values.*')  # list
        realtimetag = jsonpath(r_str1, '$.RealTimeTagValue..Name')
        print(realtimevalue)
        # tests = list(zip(realtimetag, realtimevalue))
        # print(tests[0][0])

        groups = DataGroup.objects.filter(dg_d_id=device_id)  # 设备下所有组
        print(groups)
        data1 = []
        for group in groups:  # 每个组
            groupname = group.dg_name
            dict1 = {'name': groupname, 'value': 0}
            data = Data.objects.filter(d_g_id=group.id)
            print(data)
            if not data:  # 设备未设置参数
                print('设备未设置参数')
                group.realtimevalue = '#'
                group.save()
                break
            valuelist = []
            a = []
            for d in data:  # 三个值
                if d.d_name in realtimetag:
                    b = realtimetag.index(d.d_name)
                    value = realtimevalue[b]
                    print(value)
                    if value == '#':
                        value = 0
                    valuelist.append(value)
                    print(valuelist)
                else:
                    pass
            for r in valuelist:
                r = str(r)
                r = r.replace("['", "")
                r = r.replace("']", "")
                r = float(r)
                r = round(r, 2)
                # r = '#'
                a.append(r)
            print(a)
            # print('------------------------------------------------')
            b = dict(Counter(a))
            print(b)
            c = [key for key, value in b.items() if value >= 1]
            print(c)
            ii = 0
            i = len(c)
            if i > 1:
                cc = c[0]
                for ii in range(i):
                    if cc == 0:
                        ii += 1
                        cc = c[ii]
                        print(c)
                        continue
                    else:
                        break
            else:
                cc = c[0]
            dict1["value"] = cc
            print(cc)
            # print(dict1)
            datagroup = DataGroup.objects.get(dg_name=groupname)
            print(datagroup)
            # print('--------------------------------------------------')
            datagroup.realtimevalue = cc
            datagroup.realtime = time
            datagroup.save()
            print(dict1)
    except Exception as e:
        print("获取实时值失败")

    data2 = json.dumps({
        "UnsubscriptionID": v
    })
    url2 = ip + 'WaWebService/Json/UnsubscribeRealTimeTag' + '/' + ProjectName
    resp1 = requests.post(url2, headers=headers, data=data2, auth=HTTPBasicAuth('admin', '12345678'), timeout=60)

    return True


def threeinone4(device_id):
    """
    对某设备的所有参数组 进行单独的webaccess数据获取，并将三个数据进行判断取其一返回前端
    :param request: 机械设备ID device_id
    :return:
    """
    i = 0
    datas = Data.objects.filter(d_d_id_id=device_id)
    print(datas)
    now = datetime.datetime.now()
    time = now.strftime('%Y-%m-%d %H:%M:%S')
    ProjectName = 'test'
    url = ip + 'WaWebService/Json/GetDataLog' + '/' + ProjectName + '/' + 'node1'
    headers = {"Content-Type": "application/json"}
    # request数据格式,Total指有几个tag
    format_header0 = '{"StartTime":"'
    format_header0 = format_header0 + str(time)
    format_header1 = '","IntervalType":"S","Interval":1,"Records":1'
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
    print(http_format)
    data = json.loads(http_format)  # 必须先将str变成Json
    data = json.dumps(data)  # 再将Json变成str，这样才能被requests模块正确使用
    print(data)
    # 发送带身份验证的post请求
    resp = requests.post(url, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'), timeout=60)
    response = resp.content.decode()  # str
    r_str = json.loads(response)  # dict
    # try:
    realtimevalue = jsonpath(r_str, '$.DataLog..Values[0]')
    realtimetag = jsonpath(r_str, '$.DataLog..Name')
    print(realtimevalue)
    # tests = list(zip(realtimetag, realtimevalue))
    # print(tests[0][0])

    groups = DataGroup.objects.filter(dg_d_id=device_id)  # 设备下所有组
    print(groups)
    data1 = []
    for group in groups:  # 每个组
        groupname = group.dg_name
        print(groupname)
        dict1 = {'name': groupname, 'value': 0}
        data = Data.objects.filter(d_g_id=group.id)
        # print(data)
        if not data:  # 设备未设置参数
            print('设备未设置参数')
            group.realtimevalue = '#'
            group.save()
            break
        valuelist = []
        a = []
        for d in data:  # 三个值
            if d.d_name in realtimetag:
                b = realtimetag.index(d.d_name)
                value = realtimevalue[b]
                print(value)
                if value == '#':
                    value = 0
                valuelist.append(value)
                print(valuelist)
            else:
                pass
        for r in valuelist:
            r = str(r)
            r = r.replace("['", "")
            r = r.replace("']", "")
            r = float(r)
            r = round(r, 2)
            # r = '#'
            a.append(r)
        print(a)
        # print('------------------------------------------------')
        b = dict(Counter(a))
        print(b)
        c = [key for key, value in b.items() if value >= 1]
        print(c)
        ii = 0
        i = len(c)
        if i > 1:
            cc = c[0]
            for ii in range(i):
                if cc == 0:
                    ii += 1
                    cc = c[ii]
                    print(c)
                    continue
                else:
                    break
        else:
            cc = c[0]
        dict1["value"] = cc
        print(cc)
        # print(dict1)
        datagroup = DataGroup.objects.get(dg_name=groupname,dg_d_id=device_id)
        # print(datagroup)
        # print('--------------------------------------------------')
        datagroup.realtimevalue = cc
        datagroup.realtime = time
        datagroup.save()
        print(dict1)
    # except Exception as e:
    #     print("获取实时值失败")

    return True


def my_notifications(request):
    context = {}
    return render(request, 'my_notifications.html', context)


def onemonth0(request):
    now = datetime.datetime.now()
    url = ip + 'WaWebService/JSON/GetDataLog/'
    d_id = request.GET.get('d_id')
    d = Device.objects.filter(id=d_id)
    if not d:
        response_data = {'code': ["995"], 'message': ["设备不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    d = Device.objects.get(id=d_id)
    headers = {"Content-Type": "application/json"}

    time = timedelta(sign='d', value=-1, dt=now)
    time = timedelta(sign='n', value=-10, dt=time)
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    groups = DataGroup.objects.filter(dg_d_id=d)
    results = []
    # 每一组
    for group in groups:
        time1 = timedelta(sign='m', value=-1, dt=now)
        datas = Data.objects.filter(d_g_id=group)
        i = 0
        total = datas.count()
        print('组中共有参数：')
        print(total)
        a = []
        b = []
        c = []
        d = []
        # 每个点位
        for data in datas:
            StartTime = time
            IntervalType = 'D'
            Interval = '1'
            Records = '31'
            DataType = '3'
            node_name = 'Node1'
            project_name = 'test'
            url_child = url + project_name + '/' + node_name
            Name = data.d_name
            data = json.dumps({
                "StartTime": StartTime,
                "IntervalType": IntervalType,
                "Interval": Interval,
                "Records": Records,
                "Tags": [{
                    "Name": Name,
                    "DataType": DataType
                }]
            })
            resp = requests.post(url_child, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'),
                                 timeout=20)
            response = resp.content.decode()  # str
            r_str = json.loads(response)  # dict
            r = jsonpath(r_str, '$..Values.*')  # 设备名
            if i == 0:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r1 = float(rr)
                    a.append(r1)
                i += 1
                print('第一组')
                continue
            if i == 1:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r2 = float(rr)
                    b.append(r2)
                i += 1
                print('第二组')
                continue
            if i == 2:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r3 = float(rr)
                    c.append(r3)
                i += 1
                print('第三组')
                continue
            if i == 3:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r4 = float(rr)
                    d.append(r4)
                i += 1
                print('第四组')
                continue
        if all([a, b, c, d]):
            e = list(zip(a, b, c, d))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value > 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='d', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                f.append(dict)
            drawresult = drawline(f)
            results.append(drawresult)

        if all([a, b, c]):
            e = list(zip(a, b, c))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='d', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                f.append(dict)
            drawresult = drawline(f)
            results.append(drawresult)

        if all([a, b]) and not c:
            e = list(zip(a, b))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                cc = h[0]
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='d', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                f.append(dict)
            drawresult = drawline(f)
            results.append(drawresult)

        if a and not b:
            e = list(a)
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = ee
                dict['name'] = group.dg_name
                dict['value'] = g
                time1 = timedelta(sign='d', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                f.append(dict)
            drawresult = drawline(f)
            results.append(drawresult)
    print(results)

    response = {
        'message': ['添加成功'],
        'code': ["200"],
        'data': results
    }
    return HttpResponse(json.dumps(response))


def oneweek0(request):
    now = datetime.datetime.now()
    url = ip + 'WaWebService/JSON/GetDataLog/'
    d_id = request.GET.get('d_id')
    d = Device.objects.filter(id=d_id)
    if not d:
        response_data = {'code': ["995"], 'message': ["设备不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    d = Device.objects.get(id=d_id)
    headers = {"Content-Type": "application/json"}

    time = timedelta(sign='d', value=-7, dt=now)
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    groups = DataGroup.objects.filter(dg_d_id=d)
    results = []
    # 每一组
    for group in groups:
        time1 = timedelta(sign='d', value=-7, dt=now)
        datas = Data.objects.filter(d_g_id=group)
        i = 0
        total = datas.count()
        print('组中共有参数：')
        print(total)
        a = []
        b = []
        c = []
        d = []
        # 每个点位
        for data in datas:
            StartTime = time
            IntervalType = 'H'
            Interval = '1'
            Records = '168'
            DataType = '3'
            node_name = 'Node1'
            project_name = 'test'
            url_child = url + project_name + '/' + node_name
            Name = data.d_name
            data = json.dumps({
                "StartTime": StartTime,
                "IntervalType": IntervalType,
                "Interval": Interval,
                "Records": Records,
                "Tags": [{
                    "Name": Name,
                    "DataType": DataType
                }]
            })
            resp = requests.post(url_child, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'),
                                 timeout=20)
            response = resp.content.decode()  # str
            r_str = json.loads(response)  # dict
            r = jsonpath(r_str, '$..Values.*')  # 设备名
            if i == 0:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r1 = float(rr)
                    a.append(r1)
                i += 1
                print('第一组')
                continue
            if i == 1:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r2 = float(rr)
                    b.append(r2)
                i += 1
                print('第二组')
                continue
            if i == 2:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r3 = float(rr)
                    c.append(r3)
                i += 1
                print('第三组')
                continue
            if i == 3:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r4 = float(rr)
                    d.append(r4)
                i += 1
                print('第四组')
                continue
        if all([a, b, c, d]):
            e = list(zip(a, b, c, d))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value > 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='h', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                f.append(dict)
            drawresult = drawline(f)
            results.append(drawresult)

        if all([a, b, c]):
            e = list(zip(a, b, c))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='h', value=1, dt=time1)
                print(time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                f.append(dict)
            drawresult = drawline(f)
            results.append(drawresult)

        if all([a, b]) and not c:
            e = list(zip(a, b))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='h', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                f.append(dict)
            drawresult = drawline(f)
            results.append(drawresult)

        if a and not b:
            e = list(a)
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = ee
                dict['name'] = group.dg_name
                dict['value'] = g
                time1 = timedelta(sign='h', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                f.append(dict)
            drawresult = drawline(f)
            results.append(drawresult)

    response = {
        'message': ['添加成功'],
        'code': ["200"],
        'data': results
    }
    return HttpResponse(json.dumps(response))


def testtttt(request):
    now = datetime.datetime.now()
    url = ip + 'WaWebService/JSON/GetDataLog/'
    d_id = request.GET.get('d_id')
    d = Device.objects.filter(id=d_id)
    if not d:
        response_data = {'code': ["995"], 'message': ["设备不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    d = Device.objects.get(id=d_id)
    headers = {"Content-Type": "application/json"}

    time = timedelta(sign='d', value=-1, dt=now)
    time = timedelta(sign='n', value=-10, dt=time)
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    groups = DataGroup.objects.filter(dg_d_id=d)
    print(groups)
    results = []
    # 每一组
    for group in groups:
        time1 = timedelta(sign='d', value=-1, dt=now)
        datas = Data.objects.filter(d_g_id=group)
        i = 0
        total = datas.count()
        print('组中共有参数：')
        print(total)
        a = []
        b = []
        c = []
        d = []
        # 每个点位
        for data in datas:
            StartTime = time
            IntervalType = 'M'
            Interval = '10'
            Records = '144'
            DataType = '3'
            node_name = 'Node1'
            project_name = 'test'
            url_child = url + project_name + '/' + node_name
            Name = data.d_name
            data = json.dumps({
                "StartTime": StartTime,
                "IntervalType": IntervalType,
                "Interval": Interval,
                "Records": Records,
                "Tags": [{
                    "Name": Name,
                    "DataType": DataType
                }]
            })
            resp = requests.post(url_child, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'),
                                 timeout=20)
            response = resp.content.decode()  # str
            r_str = json.loads(response)  # dict
            r = jsonpath(r_str, '$..Values.*')  # 设备名
            if i == 0:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r1 = float(rr)
                    a.append(r1)
                i += 1
                print('第一组')
                continue
            if i == 1:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r2 = float(rr)
                    b.append(r2)
                i += 1
                print('第二组')
                continue
            if i == 2:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r3 = float(rr)
                    c.append(r3)
                i += 1
                print('第三组')
                continue
            if i == 3:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r4 = float(rr)
                    d.append(r4)
                i += 1
                print('第四组')
                continue
        if all([a, b, c, d]):
            e = list(zip(a, b, c, d))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value > 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                f.append(dict)
            drawresult = drawline(f)
            results.append(drawresult)

        if all([a, b, c]):
            e = list(zip(a, b, c))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                f.append(dict)
            drawresult = drawline(f)
            results.append(drawresult)

        if all([a, b]) and not c:
            e = list(zip(a, b))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                f.append(dict)
            drawresult = drawline(f)
            results.append(drawresult)

        if a and not b:
            e = list(a)
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = ee
                dict['name'] = group.dg_name
                dict['value'] = g
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                f.append(dict)
            drawresult = drawline(f)
            results.append(drawresult)
    # print(results)

    response = {
        'message': ['返回成功'],
        'code': ["200"],
        'data': results
    }
    return HttpResponse(json.dumps(response))


def yestaday(request):
    now = datetime.datetime.now()
    url = ip + 'WaWebService/JSON/GetDataLog/'
    d_id = request.GET.get('d_id')
    d = Device.objects.filter(id=d_id)
    if not d:
        response_data = {'code': ["995"], 'message': ["设备不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    d = Device.objects.get(id=d_id)
    headers = {"Content-Type": "application/json"}

    time = timedelta(sign='d', value=-1, dt=now)
    time = timedelta(sign='n', value=-10, dt=time)
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    groups = DataGroup.objects.filter(dg_d_id=d)
    print(groups)
    results = []
    presssresults = []
    temresults = []
    speresults = []
    movresults = []
    freresults = []
    floresults = []
    elsresults = []
    namelist = []
    presssnamelist = []
    temnamelist = []
    spenamelist = []
    movnamelist = []
    frenamelist = []
    flonamelist = []
    elsnamelist = []
    selected = {}
    pressselected = {}
    temselected = {}
    speselected = {}
    movselected = {}
    freselected = {}
    floselected = {}
    elsselected = {}
    date = []
    dateflag = 0
    # 每一组
    for group in groups:
        time1 = timedelta(sign='d', value=-1, dt=now)
        datas = Data.objects.filter(d_g_id=group)
        i = 0
        total = datas.count()
        print('组中共有参数：')
        print(total)
        a = []
        b = []
        c = []
        d = []
        # 每个点位
        for data in datas:
            StartTime = time
            IntervalType = 'M'
            Interval = '10'
            Records = '144'
            DataType = '3'
            node_name = 'Node1'
            project_name = 'test'
            url_child = url + project_name + '/' + node_name
            Name = data.d_name
            data = json.dumps({
                "StartTime": StartTime,
                "IntervalType": IntervalType,
                "Interval": Interval,
                "Records": Records,
                "Tags": [{
                    "Name": Name,
                    "DataType": DataType
                }]
            })
            resp = requests.post(url_child, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'),
                                 timeout=20)
            response = resp.content.decode()  # str
            r_str = json.loads(response)  # dict
            r = jsonpath(r_str, '$..Values.*')  # 设备名
            if i == 0:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r1 = float(rr)
                    a.append(r1)
                i += 1
                # print('第一组')
                continue
            if i == 1:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r2 = float(rr)
                    b.append(r2)
                i += 1
                # print('第二组')
                continue
            if i == 2:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r3 = float(rr)
                    c.append(r3)
                i += 1
                # print('第三组')
                continue
            if i == 3:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r4 = float(rr)
                    d.append(r4)
                i += 1
                # print('第四组')
                continue
        if all([a, b, c, d]):
            e = list(zip(a, b, c, d))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value > 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            # print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]

                # namelist.append(group.dg_name)
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                if dateflag == 0:
                    date.append(time1.strftime('%Y-%m-%d %H:%M:%S'))
                f.append(dict)
            print(selected)

            dateflag = 1
            # if len(namelist) % 3 == 0 and len(namelist) != 0:
            #     namelist.append('')
            #     namelist.append(group.dg_name)
            # if len(namelist) % 3 != 0 and len(namelist) != 0:
            #     namelist.append(group.dg_name)
            #
            # if len(namelist) == 0:
            #     namelist.append(group.dg_name)
            grouptype = group.dg_type
            if grouptype == '压力':
                if pressselected:
                    key = group.dg_name
                    value = False
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
                if not pressselected:
                    key = group.dg_name
                    value = True
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
            if grouptype == '温度':
                if temselected:
                    key = group.dg_name
                    value = False
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
                if not temselected:
                    key = group.dg_name
                    value = True
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
            if grouptype == '转速':
                if speselected:
                    key = group.dg_name
                    value = False
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
                if not speselected:
                    key = group.dg_name
                    value = True
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
            if grouptype == '位移':
                if movselected:
                    key = group.dg_name
                    value = False
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
                if not movselected:
                    key = group.dg_name
                    value = True
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
            if grouptype == '频率':
                if freselected:
                    key = group.dg_name
                    value = False
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
                if not freselected:
                    key = group.dg_name
                    value = True
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
            if grouptype == '流量':
                if floselected:
                    key = group.dg_name
                    value = False
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
                if not floselected:
                    key = group.dg_name
                    value = True
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
            if grouptype == '其他':
                if elsselected:
                    key = group.dg_name
                    value = False
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
                if not elsselected:
                    key = group.dg_name
                    value = True
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
            # if selected:
            #     key = group.dg_name
            #     value = False
            #     selected[key] = value
            # if not selected:
            #     key = group.dg_name
            #     value = True
            #     selected[key] = value



        if all([a, b, c]):
            e = list(zip(a, b, c))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            # print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                # namelist.append(group.dg_name)
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                if dateflag == 0:
                    date.append(time1.strftime('%Y-%m-%d %H:%M:%S'))
                f.append(dict)
            print(selected)
            dateflag = 1
            # if len(namelist) % 3 == 0 and len(namelist) != 0:
            #     namelist.append('')
            #     namelist.append(group.dg_name)
            # if len(namelist) % 3 != 0 and len(namelist) != 0:
            #     namelist.append(group.dg_name)
            #
            # if len(namelist) == 0:
            #     namelist.append(group.dg_name)
            grouptype = group.dg_type
            if grouptype == '压力':
                if pressselected:
                    key = group.dg_name
                    value = False
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
                if not pressselected:
                    key = group.dg_name
                    value = True
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
            if grouptype == '温度':
                if temselected:
                    key = group.dg_name
                    value = False
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
                if not temselected:
                    key = group.dg_name
                    value = True
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
            if grouptype == '转速':
                if speselected:
                    key = group.dg_name
                    value = False
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
                if not speselected:
                    key = group.dg_name
                    value = True
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
            if grouptype == '位移':
                if movselected:
                    key = group.dg_name
                    value = False
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
                if not movselected:
                    key = group.dg_name
                    value = True
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
            if grouptype == '频率':
                if freselected:
                    key = group.dg_name
                    value = False
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
                if not freselected:
                    key = group.dg_name
                    value = True
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
            if grouptype == '流量':
                if floselected:
                    key = group.dg_name
                    value = False
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
                if not floselected:
                    key = group.dg_name
                    value = True
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
            if grouptype == '其他':
                if elsselected:
                    key = group.dg_name
                    value = False
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
                if not elsselected:
                    key = group.dg_name
                    value = True
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
            # namelist.append(group.dg_name)
            # if selected:
            #     key = group.dg_name
            #     value = False
            #     selected[key] = value
            # if not selected:
            #     key = group.dg_name
            #     value = True
            #     selected[key] = value
            drawresult = drawline2(f)
            results.append(drawresult)

        if all([a, b]) and not c:
            e = list(zip(a, b))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            # print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                # namelist.append(group.dg_name)
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                if dateflag == 0:
                    date.append(time1.strftime('%Y-%m-%d %H:%M:%S'))
                f.append(dict)
            print(selected)
            # if len(namelist) % 3 == 0 and len(namelist) != 0:
            #     namelist.append('')
            #     namelist.append(group.dg_name)
            # if len(namelist) % 3 != 0 and len(namelist) != 0:
            #     namelist.append(group.dg_name)
            #
            # if len(namelist) == 0:
            #     namelist.append(group.dg_name)
            dateflag = 1
            grouptype = group.dg_type
            if grouptype == '压力':
                if pressselected:
                    key = group.dg_name
                    value = False
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
                if not pressselected:
                    key = group.dg_name
                    value = True
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
            if grouptype == '温度':
                if temselected:
                    key = group.dg_name
                    value = False
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
                if not temselected:
                    key = group.dg_name
                    value = True
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
            if grouptype == '转速':
                if speselected:
                    key = group.dg_name
                    value = False
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
                if not speselected:
                    key = group.dg_name
                    value = True
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
            if grouptype == '位移':
                if movselected:
                    key = group.dg_name
                    value = False
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
                if not movselected:
                    key = group.dg_name
                    value = True
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
            if grouptype == '频率':
                if freselected:
                    key = group.dg_name
                    value = False
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
                if not freselected:
                    key = group.dg_name
                    value = True
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
            if grouptype == '流量':
                if floselected:
                    key = group.dg_name
                    value = False
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
                if not floselected:
                    key = group.dg_name
                    value = True
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
            if grouptype == '其他':
                if elsselected:
                    key = group.dg_name
                    value = False
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
                if not elsselected:
                    key = group.dg_name
                    value = True
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
            # namelist.append(group.dg_name)
            # if selected:
            #     key = group.dg_name
            #     value = False
            #     selected[key] = value
            # if not selected:
            #     key = group.dg_name
            #     value = True
            #     selected[key] = value
            drawresult = drawline2(f)
            results.append(drawresult)

        if a and not b:
            e = list(a)
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = ee
                # namelist.append(group.dg_name)
                dict['name'] = group.dg_name
                dict['value'] = g
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                if dateflag == 0:
                    date.append(time1.strftime('%Y-%m-%d %H:%M:%S'))
                f.append(dict)
            # if len(namelist) % 3 == 0 and len(namelist) !=0:
            #     namelist.append('')
            #     namelist.append(group.dg_name)
            # if len(namelist) % 3 != 0 and len(namelist) !=0:
            #     namelist.append(group.dg_name)
            #
            # if len(namelist) == 0:
            #     namelist.append(group.dg_name)

            dateflag = 1
            grouptype = group.dg_type
            if grouptype == '压力':
                if pressselected:
                    key = group.dg_name
                    value = False
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
                if not pressselected:
                    key = group.dg_name
                    value = True
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
            if grouptype == '温度':
                if temselected:
                    key = group.dg_name
                    value = False
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
                if not temselected:
                    key = group.dg_name
                    value = True
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
            if grouptype == '转速':
                if speselected:
                    key = group.dg_name
                    value = False
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
                if not speselected:
                    key = group.dg_name
                    value = True
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
            if grouptype == '位移':
                if movselected:
                    key = group.dg_name
                    value = False
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
                if not movselected:
                    key = group.dg_name
                    value = True
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
            if grouptype == '频率':
                if freselected:
                    key = group.dg_name
                    value = False
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
                if not freselected:
                    key = group.dg_name
                    value = True
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
            if grouptype == '流量':
                if floselected:
                    key = group.dg_name
                    value = False
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
                if not floselected:
                    key = group.dg_name
                    value = True
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
            if grouptype == '其他':
                if elsselected:
                    key = group.dg_name
                    value = False
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
                if not elsselected:
                    key = group.dg_name
                    value = True
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
            # namelist.append(group.dg_name)
            # if selected:
            #     key = group.dg_name
            #     value = False
            #     selected[key] = value
            # if not selected:
            #     key = group.dg_name
            #     value = True
            #     selected[key] = value

    # print(results)
    presstitle = {'text': '压力'}
    presslegend = {'x': 'center', 'y': 'top', 'data': presssnamelist, 'selected': pressselected}
    temtitle = {'text': '温度'}
    temlegend = {'x': 'center', 'y': 'top', 'data': temnamelist, 'selected': temselected}
    spetitle = {'text': '转速'}
    spelegend = {'x': 'center', 'y': 'top', 'data': spenamelist, 'selected': speselected}
    movtitle = {'text': '位移'}
    movlegend = {'x': 'center', 'y': 'top', 'data': movnamelist, 'selected': movselected}
    fretitle = {'text': '频率'}
    frelegend = {'x': 'center', 'y': 'top', 'data': frenamelist, 'selected': freselected}
    flotitle = {'text': '流量'}
    flolegend = {'x': 'center', 'y': 'top', 'data': flonamelist, 'selected': floselected}
    elstitle = {'text': '流量'}
    elslegend = {'x': 'center', 'y': 'top', 'data': elsnamelist, 'selected': elsselected}
    yAxis = {"type": 'value'}
    tooltip = {'trigger': 'axis'}
    xAxis = {'type': 'category', 'boundaryGap': False, 'data': date}
    finalresult = []
    press = {'title1': presstitle, 'tooltip': tooltip, 'legend': presslegend, 'xAxis': xAxis, 'yAxis': yAxis,
              'series': presssresults}
    tem = {'title1': temtitle, 'tooltip': tooltip, 'legend': temlegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': temresults}
    spe = {'title1': spetitle, 'tooltip': tooltip, 'legend': spelegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': speresults}
    mov = {'title1': movtitle, 'tooltip': tooltip, 'legend': movlegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': movresults}
    fre = {'title1': fretitle, 'tooltip': tooltip, 'legend': frelegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': freresults}
    flo = {'title1': flotitle, 'tooltip': tooltip, 'legend': flolegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': floresults}
    els = {'title1': elstitle, 'tooltip': tooltip, 'legend': elslegend, 'xAxis': xAxis, 'yAxis': yAxis,
           'series': elsresults}
    finalresult.append(press)
    finalresult.append(tem)
    finalresult.append(spe)
    finalresult.append(mov)
    finalresult.append(fre)
    finalresult.append(flo)
    finalresult.append(els)
    # print(selected)
    # print(namelist)
    # print(date)
    response = {
        'message': ['返回成功'],
        'code': ["200"],
        'data': finalresult
    }
    return HttpResponse(json.dumps(response))

def oneweek(request):
    now = datetime.datetime.now()
    url = ip + 'WaWebService/JSON/GetDataLog/'
    d_id = request.GET.get('d_id')
    d = Device.objects.filter(id=d_id)
    if not d:
        response_data = {'code': ["995"], 'message': ["设备不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    d = Device.objects.get(id=d_id)
    headers = {"Content-Type": "application/json"}

    time = timedelta(sign='d', value=-1, dt=now)
    time = timedelta(sign='n', value=-10, dt=time)
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    groups = DataGroup.objects.filter(dg_d_id=d)
    print(groups)
    results = []
    presssresults = []
    temresults = []
    speresults = []
    movresults = []
    freresults = []
    floresults = []
    elsresults = []
    namelist = []
    presssnamelist = []
    temnamelist = []
    spenamelist = []
    movnamelist = []
    frenamelist = []
    flonamelist = []
    elsnamelist = []
    selected = {}
    pressselected = {}
    temselected = {}
    speselected = {}
    movselected = {}
    freselected = {}
    floselected = {}
    elsselected = {}
    date = []
    dateflag = 0
    # 每一组
    for group in groups:
        time1 = timedelta(sign='d', value=-7, dt=now)
        datas = Data.objects.filter(d_g_id=group)
        i = 0
        total = datas.count()
        print('组中共有参数：')
        print(total)
        a = []
        b = []
        c = []
        d = []
        # 每个点位
        for data in datas:
            StartTime = time
            IntervalType = 'H'
            Interval = '1'
            Records = '168'
            DataType = '3'
            node_name = 'Node1'
            project_name = 'test'
            url_child = url + project_name + '/' + node_name
            Name = data.d_name
            data = json.dumps({
                "StartTime": StartTime,
                "IntervalType": IntervalType,
                "Interval": Interval,
                "Records": Records,
                "Tags": [{
                    "Name": Name,
                    "DataType": DataType
                }]
            })
            resp = requests.post(url_child, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'),
                                 timeout=20)
            response = resp.content.decode()  # str
            r_str = json.loads(response)  # dict
            r = jsonpath(r_str, '$..Values.*')  # 设备名
            if i == 0:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r1 = float(rr)
                    a.append(r1)
                i += 1
                # print('第一组')
                continue
            if i == 1:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r2 = float(rr)
                    b.append(r2)
                i += 1
                # print('第二组')
                continue
            if i == 2:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r3 = float(rr)
                    c.append(r3)
                i += 1
                # print('第三组')
                continue
            if i == 3:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r4 = float(rr)
                    d.append(r4)
                i += 1
                # print('第四组')
                continue
        if all([a, b, c, d]):
            e = list(zip(a, b, c, d))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value > 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            # print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]

                # namelist.append(group.dg_name)
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='h', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                if dateflag == 0:
                    date.append(time1.strftime('%Y-%m-%d %H:%M:%S'))
                f.append(dict)
            print(selected)

            dateflag = 1
            # if len(namelist) % 3 == 0 and len(namelist) != 0:
            #     namelist.append('')
            #     namelist.append(group.dg_name)
            # if len(namelist) % 3 != 0 and len(namelist) != 0:
            #     namelist.append(group.dg_name)
            #
            # if len(namelist) == 0:
            #     namelist.append(group.dg_name)
            grouptype = group.dg_type
            if grouptype == '压力':
                if pressselected:
                    key = group.dg_name
                    value = False
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
                if not pressselected:
                    key = group.dg_name
                    value = True
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
            if grouptype == '温度':
                if temselected:
                    key = group.dg_name
                    value = False
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
                if not temselected:
                    key = group.dg_name
                    value = True
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
            if grouptype == '转速':
                if speselected:
                    key = group.dg_name
                    value = False
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
                if not speselected:
                    key = group.dg_name
                    value = True
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
            if grouptype == '位移':
                if movselected:
                    key = group.dg_name
                    value = False
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
                if not movselected:
                    key = group.dg_name
                    value = True
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
            if grouptype == '频率':
                if freselected:
                    key = group.dg_name
                    value = False
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
                if not freselected:
                    key = group.dg_name
                    value = True
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
            if grouptype == '流量':
                if floselected:
                    key = group.dg_name
                    value = False
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
                if not floselected:
                    key = group.dg_name
                    value = True
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
            if grouptype == '其他':
                if elsselected:
                    key = group.dg_name
                    value = False
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
                if not elsselected:
                    key = group.dg_name
                    value = True
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
            # if selected:
            #     key = group.dg_name
            #     value = False
            #     selected[key] = value
            # if not selected:
            #     key = group.dg_name
            #     value = True
            #     selected[key] = value



        if all([a, b, c]):
            e = list(zip(a, b, c))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            # print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                # namelist.append(group.dg_name)
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='h', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                if dateflag == 0:
                    date.append(time1.strftime('%Y-%m-%d %H:%M:%S'))
                f.append(dict)
            print(selected)
            dateflag = 1
            # if len(namelist) % 3 == 0 and len(namelist) != 0:
            #     namelist.append('')
            #     namelist.append(group.dg_name)
            # if len(namelist) % 3 != 0 and len(namelist) != 0:
            #     namelist.append(group.dg_name)
            #
            # if len(namelist) == 0:
            #     namelist.append(group.dg_name)
            grouptype = group.dg_type
            if grouptype == '压力':
                if pressselected:
                    key = group.dg_name
                    value = False
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
                if not pressselected:
                    key = group.dg_name
                    value = True
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
            if grouptype == '温度':
                if temselected:
                    key = group.dg_name
                    value = False
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
                if not temselected:
                    key = group.dg_name
                    value = True
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
            if grouptype == '转速':
                if speselected:
                    key = group.dg_name
                    value = False
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
                if not speselected:
                    key = group.dg_name
                    value = True
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
            if grouptype == '位移':
                if movselected:
                    key = group.dg_name
                    value = False
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
                if not movselected:
                    key = group.dg_name
                    value = True
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
            if grouptype == '频率':
                if freselected:
                    key = group.dg_name
                    value = False
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
                if not freselected:
                    key = group.dg_name
                    value = True
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
            if grouptype == '流量':
                if floselected:
                    key = group.dg_name
                    value = False
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
                if not floselected:
                    key = group.dg_name
                    value = True
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
            if grouptype == '其他':
                if elsselected:
                    key = group.dg_name
                    value = False
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
                if not elsselected:
                    key = group.dg_name
                    value = True
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
            # namelist.append(group.dg_name)
            # if selected:
            #     key = group.dg_name
            #     value = False
            #     selected[key] = value
            # if not selected:
            #     key = group.dg_name
            #     value = True
            #     selected[key] = value
            drawresult = drawline2(f)
            results.append(drawresult)

        if all([a, b]) and not c:
            e = list(zip(a, b))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            # print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                # namelist.append(group.dg_name)
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='h', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                if dateflag == 0:
                    date.append(time1.strftime('%Y-%m-%d %H:%M:%S'))
                f.append(dict)
            print(selected)
            # if len(namelist) % 3 == 0 and len(namelist) != 0:
            #     namelist.append('')
            #     namelist.append(group.dg_name)
            # if len(namelist) % 3 != 0 and len(namelist) != 0:
            #     namelist.append(group.dg_name)
            #
            # if len(namelist) == 0:
            #     namelist.append(group.dg_name)
            dateflag = 1
            grouptype = group.dg_type
            if grouptype == '压力':
                if pressselected:
                    key = group.dg_name
                    value = False
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
                if not pressselected:
                    key = group.dg_name
                    value = True
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
            if grouptype == '温度':
                if temselected:
                    key = group.dg_name
                    value = False
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
                if not temselected:
                    key = group.dg_name
                    value = True
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
            if grouptype == '转速':
                if speselected:
                    key = group.dg_name
                    value = False
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
                if not speselected:
                    key = group.dg_name
                    value = True
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
            if grouptype == '位移':
                if movselected:
                    key = group.dg_name
                    value = False
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
                if not movselected:
                    key = group.dg_name
                    value = True
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
            if grouptype == '频率':
                if freselected:
                    key = group.dg_name
                    value = False
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
                if not freselected:
                    key = group.dg_name
                    value = True
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
            if grouptype == '流量':
                if floselected:
                    key = group.dg_name
                    value = False
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
                if not floselected:
                    key = group.dg_name
                    value = True
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
            if grouptype == '其他':
                if elsselected:
                    key = group.dg_name
                    value = False
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
                if not elsselected:
                    key = group.dg_name
                    value = True
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
            # namelist.append(group.dg_name)
            # if selected:
            #     key = group.dg_name
            #     value = False
            #     selected[key] = value
            # if not selected:
            #     key = group.dg_name
            #     value = True
            #     selected[key] = value
            drawresult = drawline2(f)
            results.append(drawresult)

        if a and not b:
            e = list(a)
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = ee
                # namelist.append(group.dg_name)
                dict['name'] = group.dg_name
                dict['value'] = g
                time1 = timedelta(sign='h', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                if dateflag == 0:
                    date.append(time1.strftime('%Y-%m-%d %H:%M:%S'))
                f.append(dict)
            # if len(namelist) % 3 == 0 and len(namelist) !=0:
            #     namelist.append('')
            #     namelist.append(group.dg_name)
            # if len(namelist) % 3 != 0 and len(namelist) !=0:
            #     namelist.append(group.dg_name)
            #
            # if len(namelist) == 0:
            #     namelist.append(group.dg_name)

            dateflag = 1
            grouptype = group.dg_type
            if grouptype == '压力':
                if pressselected:
                    key = group.dg_name
                    value = False
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
                if not pressselected:
                    key = group.dg_name
                    value = True
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
            if grouptype == '温度':
                if temselected:
                    key = group.dg_name
                    value = False
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
                if not temselected:
                    key = group.dg_name
                    value = True
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
            if grouptype == '转速':
                if speselected:
                    key = group.dg_name
                    value = False
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
                if not speselected:
                    key = group.dg_name
                    value = True
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
            if grouptype == '位移':
                if movselected:
                    key = group.dg_name
                    value = False
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
                if not movselected:
                    key = group.dg_name
                    value = True
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
            if grouptype == '频率':
                if freselected:
                    key = group.dg_name
                    value = False
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
                if not freselected:
                    key = group.dg_name
                    value = True
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
            if grouptype == '流量':
                if floselected:
                    key = group.dg_name
                    value = False
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
                if not floselected:
                    key = group.dg_name
                    value = True
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
            if grouptype == '其他':
                if elsselected:
                    key = group.dg_name
                    value = False
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
                if not elsselected:
                    key = group.dg_name
                    value = True
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
            # namelist.append(group.dg_name)
            # if selected:
            #     key = group.dg_name
            #     value = False
            #     selected[key] = value
            # if not selected:
            #     key = group.dg_name
            #     value = True
            #     selected[key] = value

    # print(results)
    presstitle = {'text': '压力'}
    presslegend = {'x': 'center', 'y': 'top', 'data': presssnamelist, 'selected': pressselected}
    temtitle = {'text': '温度'}
    temlegend = {'x': 'center', 'y': 'top', 'data': temnamelist, 'selected': temselected}
    spetitle = {'text': '转速'}
    spelegend = {'x': 'center', 'y': 'top', 'data': spenamelist, 'selected': speselected}
    movtitle = {'text': '位移'}
    movlegend = {'x': 'center', 'y': 'top', 'data': movnamelist, 'selected': movselected}
    fretitle = {'text': '频率'}
    frelegend = {'x': 'center', 'y': 'top', 'data': frenamelist, 'selected': freselected}
    flotitle = {'text': '流量'}
    flolegend = {'x': 'center', 'y': 'top', 'data': flonamelist, 'selected': floselected}
    elstitle = {'text': '流量'}
    elslegend = {'x': 'center', 'y': 'top', 'data': elsnamelist, 'selected': elsselected}
    yAxis = {"type": 'value'}
    tooltip = {'trigger': 'axis'}
    xAxis = {'type': 'category', 'boundaryGap': False, 'data': date}
    finalresult = []
    press = {'title1': presstitle, 'tooltip': tooltip, 'legend': presslegend, 'xAxis': xAxis, 'yAxis': yAxis,
              'series': presssresults}
    tem = {'title1': temtitle, 'tooltip': tooltip, 'legend': temlegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': temresults}
    spe = {'title1': spetitle, 'tooltip': tooltip, 'legend': spelegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': speresults}
    mov = {'title1': movtitle, 'tooltip': tooltip, 'legend': movlegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': movresults}
    fre = {'title1': fretitle, 'tooltip': tooltip, 'legend': frelegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': freresults}
    flo = {'title1': flotitle, 'tooltip': tooltip, 'legend': flolegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': floresults}
    els = {'title1': elstitle, 'tooltip': tooltip, 'legend': elslegend, 'xAxis': xAxis, 'yAxis': yAxis,
           'series': elsresults}
    finalresult.append(press)
    finalresult.append(tem)
    finalresult.append(spe)
    finalresult.append(mov)
    finalresult.append(fre)
    finalresult.append(flo)
    finalresult.append(els)
    # print(selected)
    # print(namelist)
    # print(date)
    response = {
        'message': ['返回成功'],
        'code': ["200"],
        'data': finalresult
    }
    return HttpResponse(json.dumps(response))


def onemonth(request):
    now = datetime.datetime.now()
    url = ip + 'WaWebService/JSON/GetDataLog/'
    d_id = request.GET.get('d_id')
    d = Device.objects.filter(id=d_id)
    if not d:
        response_data = {'code': ["995"], 'message': ["设备不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    d = Device.objects.get(id=d_id)
    headers = {"Content-Type": "application/json"}

    time = timedelta(sign='d', value=-31, dt=now)
    print(time)
    # time = timedelta(sign='n', value=-10, dt=time)
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    groups = DataGroup.objects.filter(dg_d_id=d)
    print(groups)
    results = []
    presssresults = []
    temresults = []
    speresults = []
    movresults = []
    freresults = []
    floresults = []
    elsresults = []
    namelist = []
    presssnamelist = []
    temnamelist = []
    spenamelist = []
    movnamelist = []
    frenamelist = []
    flonamelist = []
    elsnamelist = []
    selected = {}
    pressselected = {}
    temselected = {}
    speselected = {}
    movselected = {}
    freselected = {}
    floselected = {}
    elsselected = {}
    date = []
    dateflag = 0
    # 每一组
    for group in groups:
        time1 = timedelta(sign='d', value=-31, dt=now)
        datas = Data.objects.filter(d_g_id=group)
        i = 0
        total = datas.count()
        print('组中共有参数：')
        print(total)
        a = []
        b = []
        c = []
        d = []
        # 每个点位
        for data in datas:
            StartTime = time
            IntervalType = 'D'
            Interval = '1'
            Records = '31'
            DataType = '3'
            node_name = 'Node1'
            project_name = 'test'
            url_child = url + project_name + '/' + node_name
            Name = data.d_name
            data = json.dumps({
                "StartTime": StartTime,
                "IntervalType": IntervalType,
                "Interval": Interval,
                "Records": Records,
                "Tags": [{
                    "Name": Name,
                    "DataType": DataType
                }]
            })
            resp = requests.post(url_child, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'),
                                 timeout=20)
            response = resp.content.decode()  # str
            r_str = json.loads(response)  # dict
            r = jsonpath(r_str, '$..Values.*')  # 设备名
            if i == 0:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r1 = float(rr)
                    a.append(r1)
                i += 1
                # print('第一组')
                continue
            if i == 1:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r2 = float(rr)
                    b.append(r2)
                i += 1
                # print('第二组')
                continue
            if i == 2:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r3 = float(rr)
                    c.append(r3)
                i += 1
                # print('第三组')
                continue
            if i == 3:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r4 = float(rr)
                    d.append(r4)
                i += 1
                # print('第四组')
                continue
        if all([a, b, c, d]):
            e = list(zip(a, b, c, d))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value > 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            # print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]

                # namelist.append(group.dg_name)
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='d', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                if dateflag == 0:
                    date.append(time1.strftime('%Y-%m-%d %H:%M:%S'))
                f.append(dict)
            print(selected)

            dateflag = 1
            # if len(namelist) % 3 == 0 and len(namelist) != 0:
            #     namelist.append('')
            #     namelist.append(group.dg_name)
            # if len(namelist) % 3 != 0 and len(namelist) != 0:
            #     namelist.append(group.dg_name)
            #
            # if len(namelist) == 0:
            #     namelist.append(group.dg_name)
            grouptype = group.dg_type
            if grouptype == '压力':
                if pressselected:
                    key = group.dg_name
                    value = False
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
                if not pressselected:
                    key = group.dg_name
                    value = True
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
            if grouptype == '温度':
                if temselected:
                    key = group.dg_name
                    value = False
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
                if not temselected:
                    key = group.dg_name
                    value = True
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
            if grouptype == '转速':
                if speselected:
                    key = group.dg_name
                    value = False
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
                if not speselected:
                    key = group.dg_name
                    value = True
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
            if grouptype == '位移':
                if movselected:
                    key = group.dg_name
                    value = False
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
                if not movselected:
                    key = group.dg_name
                    value = True
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
            if grouptype == '频率':
                if freselected:
                    key = group.dg_name
                    value = False
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
                if not freselected:
                    key = group.dg_name
                    value = True
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
            if grouptype == '流量':
                if floselected:
                    key = group.dg_name
                    value = False
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
                if not floselected:
                    key = group.dg_name
                    value = True
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
            if grouptype == '其他':
                if elsselected:
                    key = group.dg_name
                    value = False
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
                if not elsselected:
                    key = group.dg_name
                    value = True
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
            # if selected:
            #     key = group.dg_name
            #     value = False
            #     selected[key] = value
            # if not selected:
            #     key = group.dg_name
            #     value = True
            #     selected[key] = value



        if all([a, b, c]):
            e = list(zip(a, b, c))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            # print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                # namelist.append(group.dg_name)
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='d', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                if dateflag == 0:
                    date.append(time1.strftime('%Y-%m-%d %H:%M:%S'))
                f.append(dict)
            print(selected)
            dateflag = 1
            # if len(namelist) % 3 == 0 and len(namelist) != 0:
            #     namelist.append('')
            #     namelist.append(group.dg_name)
            # if len(namelist) % 3 != 0 and len(namelist) != 0:
            #     namelist.append(group.dg_name)
            #
            # if len(namelist) == 0:
            #     namelist.append(group.dg_name)
            grouptype = group.dg_type
            if grouptype == '压力':
                if pressselected:
                    key = group.dg_name
                    value = False
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
                if not pressselected:
                    key = group.dg_name
                    value = True
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
            if grouptype == '温度':
                if temselected:
                    key = group.dg_name
                    value = False
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
                if not temselected:
                    key = group.dg_name
                    value = True
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
            if grouptype == '转速':
                if speselected:
                    key = group.dg_name
                    value = False
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
                if not speselected:
                    key = group.dg_name
                    value = True
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
            if grouptype == '位移':
                if movselected:
                    key = group.dg_name
                    value = False
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
                if not movselected:
                    key = group.dg_name
                    value = True
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
            if grouptype == '频率':
                if freselected:
                    key = group.dg_name
                    value = False
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
                if not freselected:
                    key = group.dg_name
                    value = True
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
            if grouptype == '流量':
                if floselected:
                    key = group.dg_name
                    value = False
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
                if not floselected:
                    key = group.dg_name
                    value = True
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
            if grouptype == '其他':
                if elsselected:
                    key = group.dg_name
                    value = False
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
                if not elsselected:
                    key = group.dg_name
                    value = True
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
            # namelist.append(group.dg_name)
            # if selected:
            #     key = group.dg_name
            #     value = False
            #     selected[key] = value
            # if not selected:
            #     key = group.dg_name
            #     value = True
            #     selected[key] = value
            drawresult = drawline2(f)
            results.append(drawresult)

        if all([a, b]) and not c:
            e = list(zip(a, b))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            # print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                # namelist.append(group.dg_name)
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='d', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                if dateflag == 0:
                    date.append(time1.strftime('%Y-%m-%d %H:%M:%S'))
                f.append(dict)
            print(selected)
            # if len(namelist) % 3 == 0 and len(namelist) != 0:
            #     namelist.append('')
            #     namelist.append(group.dg_name)
            # if len(namelist) % 3 != 0 and len(namelist) != 0:
            #     namelist.append(group.dg_name)
            #
            # if len(namelist) == 0:
            #     namelist.append(group.dg_name)
            dateflag = 1
            grouptype = group.dg_type
            if grouptype == '压力':
                if pressselected:
                    key = group.dg_name
                    value = False
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
                if not pressselected:
                    key = group.dg_name
                    value = True
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
            if grouptype == '温度':
                if temselected:
                    key = group.dg_name
                    value = False
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
                if not temselected:
                    key = group.dg_name
                    value = True
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
            if grouptype == '转速':
                if speselected:
                    key = group.dg_name
                    value = False
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
                if not speselected:
                    key = group.dg_name
                    value = True
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
            if grouptype == '位移':
                if movselected:
                    key = group.dg_name
                    value = False
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
                if not movselected:
                    key = group.dg_name
                    value = True
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
            if grouptype == '频率':
                if freselected:
                    key = group.dg_name
                    value = False
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
                if not freselected:
                    key = group.dg_name
                    value = True
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
            if grouptype == '流量':
                if floselected:
                    key = group.dg_name
                    value = False
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
                if not floselected:
                    key = group.dg_name
                    value = True
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
            if grouptype == '其他':
                if elsselected:
                    key = group.dg_name
                    value = False
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
                if not elsselected:
                    key = group.dg_name
                    value = True
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
            # namelist.append(group.dg_name)
            # if selected:
            #     key = group.dg_name
            #     value = False
            #     selected[key] = value
            # if not selected:
            #     key = group.dg_name
            #     value = True
            #     selected[key] = value
            drawresult = drawline2(f)
            results.append(drawresult)

        if a and not b:
            e = list(a)
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = ee
                # namelist.append(group.dg_name)
                dict['name'] = group.dg_name
                dict['value'] = g
                time1 = timedelta(sign='d', value=1, dt=time1)
                dict['time'] = time1.strftime('%Y-%m-%d %H:%M:%S')
                if dateflag == 0:
                    date.append(time1.strftime('%Y-%m-%d %H:%M:%S'))
                f.append(dict)
            # if len(namelist) % 3 == 0 and len(namelist) !=0:
            #     namelist.append('')
            #     namelist.append(group.dg_name)
            # if len(namelist) % 3 != 0 and len(namelist) !=0:
            #     namelist.append(group.dg_name)
            #
            # if len(namelist) == 0:
            #     namelist.append(group.dg_name)

            dateflag = 1
            grouptype = group.dg_type
            if grouptype == '压力':
                if pressselected:
                    key = group.dg_name
                    value = False
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
                if not pressselected:
                    key = group.dg_name
                    value = True
                    pressselected[key] = value
                    presssnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    presssresults.append(drawresult)
            if grouptype == '温度':
                if temselected:
                    key = group.dg_name
                    value = False
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
                if not temselected:
                    key = group.dg_name
                    value = True
                    temselected[key] = value
                    temnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    temresults.append(drawresult)
            if grouptype == '转速':
                if speselected:
                    key = group.dg_name
                    value = False
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
                if not speselected:
                    key = group.dg_name
                    value = True
                    speselected[key] = value
                    spenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    speresults.append(drawresult)
            if grouptype == '位移':
                if movselected:
                    key = group.dg_name
                    value = False
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
                if not movselected:
                    key = group.dg_name
                    value = True
                    movselected[key] = value
                    movnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    movresults.append(drawresult)
            if grouptype == '频率':
                if freselected:
                    key = group.dg_name
                    value = False
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
                if not freselected:
                    key = group.dg_name
                    value = True
                    freselected[key] = value
                    frenamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    freresults.append(drawresult)
            if grouptype == '流量':
                if floselected:
                    key = group.dg_name
                    value = False
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
                if not floselected:
                    key = group.dg_name
                    value = True
                    floselected[key] = value
                    flonamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    floresults.append(drawresult)
            if grouptype == '其他':
                if elsselected:
                    key = group.dg_name
                    value = False
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
                if not elsselected:
                    key = group.dg_name
                    value = True
                    elsselected[key] = value
                    elsnamelist.append(group.dg_name)
                    drawresult = drawline2(f)
                    elsresults.append(drawresult)
            # namelist.append(group.dg_name)
            # if selected:
            #     key = group.dg_name
            #     value = False
            #     selected[key] = value
            # if not selected:
            #     key = group.dg_name
            #     value = True
            #     selected[key] = value

    # print(results)
    presstitle = {'text': '压力'}
    presslegend = {'x': 'center', 'y': 'top', 'data': presssnamelist, 'selected': pressselected}
    temtitle = {'text': '温度'}
    temlegend = {'x': 'center', 'y': 'top', 'data': temnamelist, 'selected': temselected}
    spetitle = {'text': '转速'}
    spelegend = {'x': 'center', 'y': 'top', 'data': spenamelist, 'selected': speselected}
    movtitle = {'text': '位移'}
    movlegend = {'x': 'center', 'y': 'top', 'data': movnamelist, 'selected': movselected}
    fretitle = {'text': '频率'}
    frelegend = {'x': 'center', 'y': 'top', 'data': frenamelist, 'selected': freselected}
    flotitle = {'text': '流量'}
    flolegend = {'x': 'center', 'y': 'top', 'data': flonamelist, 'selected': floselected}
    elstitle = {'text': '流量'}
    elslegend = {'x': 'center', 'y': 'top', 'data': elsnamelist, 'selected': elsselected}
    yAxis = {"type": 'value'}
    tooltip = {'trigger': 'axis'}
    xAxis = {'type': 'category', 'boundaryGap': False, 'data': date}
    finalresult = []
    press = {'title1': presstitle, 'tooltip': tooltip, 'legend': presslegend, 'xAxis': xAxis, 'yAxis': yAxis,
              'series': presssresults}
    tem = {'title1': temtitle, 'tooltip': tooltip, 'legend': temlegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': temresults}
    spe = {'title1': spetitle, 'tooltip': tooltip, 'legend': spelegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': speresults}
    mov = {'title1': movtitle, 'tooltip': tooltip, 'legend': movlegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': movresults}
    fre = {'title1': fretitle, 'tooltip': tooltip, 'legend': frelegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': freresults}
    flo = {'title1': flotitle, 'tooltip': tooltip, 'legend': flolegend, 'xAxis': xAxis, 'yAxis': yAxis,
             'series': floresults}
    els = {'title1': elstitle, 'tooltip': tooltip, 'legend': elslegend, 'xAxis': xAxis, 'yAxis': yAxis,
           'series': elsresults}
    finalresult.append(press)
    finalresult.append(tem)
    finalresult.append(spe)
    finalresult.append(mov)
    finalresult.append(fre)
    finalresult.append(flo)
    finalresult.append(els)
    # print(selected)
    # print(namelist)
    # print(date)
    response = {
        'message': ['返回成功'],
        'code': ["200"],
        'data': finalresult
    }
    return HttpResponse(json.dumps(response))

def drawline(f):
    timedata = []
    seriesdata = []
    name = f[0]["name"]
    for ff in f:
        time = ff["time"]
        timedata.append(time)
        value = ff["value"]
        value = float(value)
        value = round(value, 2)
        seriesdata.append(value)
    xAxis = {"type": 'category', 'data': timedata}
    yAxis = {"type": 'value'}
    series = []
    lineStyle = {'color': '#5470C6', 'width': 2}
    dict = {'data': seriesdata, 'type': 'line', 'smooth': True, 'symbol': 'none', 'lineStyle': lineStyle}
    series.append(dict)
    dict0 = {'xAxis': xAxis, 'yAxis': yAxis, 'series': series}
    dict = {'name': name, 'draw': dict0}
    return dict


def drawline2(f):
    timedata = []
    seriesdata = []
    name = f[0]["name"]
    for ff in f:
        time = ff["time"]
        timedata.append(time)
        value = ff["value"]
        value = float(value)
        value = round(value, 2)
        seriesdata.append(value)
    dict = {'name': name, 'type': 'line', 'symbol': 'none', 'data': seriesdata}
    return dict


def wechatline(request):
    user_id = request.GET.get('user_id')
    user = LoginUser.objects.get(id=user_id)
    if user.u_type == '公司管理员':
        company = Company.objects.get(id=user.u_company_id)
        a = Collectdevice.objects.filter(cd_c_id=company.id)
        dddd = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)

            for device in devices:
                data = {"devicename": device.d_name, "device_id": device.id}
                dddd.append(data)
    if user.u_type == '超级管理员':
        print('超级管理员')
        a = Collectdevice.objects.all()
        print(a)
        dddd = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)
            for device in devices:
                data = {"devicename": device.d_name, "device_id": device.id}
                dddd.append(data)
    typelist = ['超级管理员', '公司管理员']
    if user.u_type not in typelist:

        a = user.collectdevice.all()
        print(a)
        dddd = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)

            for device in devices:
                data = {"devicename": device.d_name, "device_id": device.id}
                dddd.append(data)
    if not len(dddd):
        response_data = {'code': ["963"], 'message': ["您当前没有关联的设备"]}
        return HttpResponse(json.dumps(response_data))
    devicename = dddd[0]["devicename"]
    print(devicename)
    now = datetime.datetime.now()
    url = ip + 'WaWebService/JSON/GetDataLog/'
    d = Device.objects.filter(d_name=devicename)
    if not d:
        response_data = {'code': ["995"], 'message': ["设备不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    d = Device.objects.get(d_name=devicename)
    headers = {"Content-Type": "application/json"}

    time = timedelta(sign='h', value=-1, dt=now)
    time = timedelta(sign='n', value=-10, dt=time)
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    groups = DataGroup.objects.filter(dg_d_id=d)
    print(groups)
    results = []
    # 每一组
    for group in groups:
        time1 = timedelta(sign='h', value=-1, dt=now)
        datas = Data.objects.filter(d_g_id=group)
        i = 0
        total = datas.count()
        print('组中共有参数：')
        print(total)
        a = []
        b = []
        c = []
        d = []
        # 每个点位
        for data in datas:
            StartTime = time
            IntervalType = 'M'
            Interval = '10'
            Records = '6'
            DataType = '3'
            node_name = 'Node1'
            project_name = 'test'
            url_child = url + project_name + '/' + node_name
            Name = data.d_name
            data = json.dumps({
                "StartTime": StartTime,
                "IntervalType": IntervalType,
                "Interval": Interval,
                "Records": Records,
                "Tags": [{
                    "Name": Name,
                    "DataType": DataType
                }]
            })
            resp = requests.post(url_child, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'),
                                 timeout=20)
            response = resp.content.decode()  # str
            r_str = json.loads(response)  # dict
            r = jsonpath(r_str, '$..Values.*')  # 设备名
            if i == 0:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r1 = float(rr)
                    a.append(r1)
                i += 1
                print('第一组')
                continue
            if i == 1:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r2 = float(rr)
                    b.append(r2)
                i += 1
                print('第二组')
                continue
            if i == 2:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r3 = float(rr)
                    c.append(r3)
                i += 1
                print('第三组')
                continue
            if i == 3:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r4 = float(rr)
                    d.append(r4)
                i += 1
                print('第四组')
                continue
        if all([a, b, c, d]):
            e = list(zip(a, b, c, d))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value > 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%H:%M:%S')
                g = random.randint(0, 10000)
                g = 'D' + str(g)
                f.append(dict)
            drawresult = drawline1(f, g)
            results.append(drawresult)

        if all([a, b, c]):
            e = list(zip(a, b, c))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%H:%M:%S')
                g = random.randint(0, 10000)
                g = 'D' + str(g)
                f.append(dict)
            drawresult = drawline1(f, g)
            results.append(drawresult)

        if all([a, b]) and not c:
            e = list(zip(a, b))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%H:%M:%S')
                g = random.randint(0, 10000)
                g = 'D' + str(g)
                f.append(dict)
            drawresult = drawline1(f, g)
            results.append(drawresult)

        if a and not b:
            e = list(a)
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = ee
                dict['name'] = group.dg_name
                dict['value'] = g
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%H:%M:%S')
                g = random.randint(0, 10000)
                g = 'D' + str(g)
                f.append(dict)
            drawresult = drawline1(f, g)
            results.append(drawresult)
    print(results)

    response = {
        'message': ['返回成功'],
        'code': ["200"],
        'data': results,
        'device': dddd,
        'present': dddd[0]
    }
    return HttpResponse(json.dumps(response))


def wechatlinev1(request):
    user_id = request.GET.get('user_id')
    device_id = request.GET.get('device_id')
    print(device_id)
    user = LoginUser.objects.get(id=user_id)
    if user.u_type == '公司管理员':
        company = Company.objects.get(id=user.u_company_id)
        a = Collectdevice.objects.filter(cd_c_id=company.id)
        dddd = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)

            for device in devices:
                data = {"devicename": device.d_name, "device_id": device.id}
                dddd.append(data)
    if user.u_type == '超级管理员':
        print('超级管理员')
        a = Collectdevice.objects.all()
        print(a)
        dddd = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)
            for device in devices:
                data = {"devicename": device.d_name, "device_id": device.id}
                dddd.append(data)
    typelist = ['超级管理员', '公司管理员']
    if user.u_type not in typelist:

        a = user.collectdevice.all()
        print(a)
        dddd = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)

            for device in devices:
                data = {"devicename": device.d_name, "device_id": device.id}
                dddd.append(data)
    if not len(dddd):
        response_data = {'code': ["963"], 'message': ["您当前没有关联的设备"]}
        return HttpResponse(json.dumps(response_data))

    now = datetime.datetime.now()
    url = ip + 'WaWebService/JSON/GetDataLog/'

    print(device_id)
    d = Device.objects.get(id=device_id)
    present = {"devicename": d.d_name, "device_id": d.id}
    if not d:
        response_data = {'code': ["995"], 'message': ["设备不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    d = Device.objects.get(id=device_id)
    headers = {"Content-Type": "application/json"}

    time = timedelta(sign='h', value=-1, dt=now)
    time = timedelta(sign='n', value=-10, dt=time)
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    groups = DataGroup.objects.filter(dg_d_id=d)
    if not groups:
        response_data = {'code': ["942"], 'message': ["当前设备未设置参数"]}
        return HttpResponse(json.dumps(response_data))
    results = []
    # 每一组
    for group in groups:
        time1 = timedelta(sign='h', value=-1, dt=now)
        datas = Data.objects.filter(d_g_id=group)
        i = 0
        total = datas.count()
        print('组中共有参数：')
        print(total)
        a = []
        b = []
        c = []
        d = []
        # 每个点位
        for data in datas:
            StartTime = time
            IntervalType = 'M'
            Interval = '10'
            Records = '6'
            DataType = '3'
            node_name = 'Node1'
            project_name = 'test'
            url_child = url + project_name + '/' + node_name
            Name = data.d_name
            data = json.dumps({
                "StartTime": StartTime,
                "IntervalType": IntervalType,
                "Interval": Interval,
                "Records": Records,
                "Tags": [{
                    "Name": Name,
                    "DataType": DataType
                }]
            })
            resp = requests.post(url_child, headers=headers, data=data, auth=HTTPBasicAuth('admin', '12345678'),
                                 timeout=20)
            response = resp.content.decode()  # str
            r_str = json.loads(response)  # dict
            r = jsonpath(r_str, '$..Values.*')  # 设备名
            if i == 0:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r1 = float(rr)
                    a.append(r1)
                i += 1
                print('第一组')
                continue
            if i == 1:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r2 = float(rr)
                    b.append(r2)
                i += 1
                print('第二组')
                continue
            if i == 2:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r3 = float(rr)
                    c.append(r3)
                i += 1
                print('第三组')
                continue
            if i == 3:
                for rr in r:
                    if rr == '#':
                        rr = 0
                    r4 = float(rr)
                    d.append(r4)
                i += 1
                print('第四组')
                continue
        if all([a, b, c, d]):
            e = list(zip(a, b, c, d))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value > 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%H:%M:%S')
                g = random.randint(0, 10000)
                g = 'D' + str(g)
                f.append(dict)
            drawresult = drawline1(f, g)
            results.append(drawresult)

        if all([a, b, c]):
            e = list(zip(a, b, c))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%H:%M:%S')
                g = random.randint(0, 10000)
                g = 'D' + str(g)
                f.append(dict)
            drawresult = drawline1(f, g)
            results.append(drawresult)

        if all([a, b]) and not c:
            e = list(zip(a, b))
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = Counter(ee)
                h = [key for key, value in g.items() if value >= 1]
                ii = 0
                i = len(h)
                if i > 1:
                    cc = h[0]
                    for ii in range(i):
                        if cc == 0:
                            ii += 1
                            cc = h[ii]
                            print(h)
                            continue
                        else:
                            break
                else:
                    cc = h[0]
                dict['name'] = group.dg_name
                dict['value'] = cc
                time1 = timedelta(sign='n', value=10, dt=time1)
                dict['time'] = time1.strftime('%H:%M:%S')
                g = random.randint(0, 10000)
                g = 'D' + str(g)
                f.append(dict)
            drawresult = drawline1(f, g)
            results.append(drawresult)

        if a and not b:
            e = list(a)
            f = []
            for ee in e:
                dict = {'name': '', 'value': '', 'time': ''}
                g = ee
                dict['name'] = group.dg_name
                dict['value'] = g
                time1 = timedelta(sign='n', value=5, dt=time1)
                dict['time'] = time1.strftime('%H:%M:%S')
                g = random.randint(0, 10000)
                g = 'D' + str(g)
                f.append(dict)
            drawresult = drawline1(f, g)
            results.append(drawresult)
    print(results)

    response = {
        'message': ['返回成功'],
        'code': ["200"],
        'data': results,
        'device': dddd,
        'present': present
    }
    return HttpResponse(json.dumps(response))


def devicehealth(request):
    user_id = request.GET.get('user_id')
    user = LoginUser.objects.get(id=user_id)
    today = 0
    total = 0
    if user.u_type == '公司管理员':
        company = Company.objects.get(id=user.u_company_id)
        a = Collectdevice.objects.filter(cd_c_id=company.id)
        dddd = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)
            for device in devices:
                data = {"devicename": device.d_name, "device_id": device.id}
                dddd.append(data)
    if user.u_type == '超级管理员':
        print('超级管理员')
        a = Collectdevice.objects.all()
        print(a)
        dddd = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)
            for device in devices:
                data = {"devicename": device.d_name, "device_id": device.id}
                dddd.append(data)
    typelist = ['超级管理员', '公司管理员']
    if user.u_type not in typelist:

        a = user.collectdevice.all()
        print(a)
        dddd = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)

            for device in devices:
                data = {"devicename": device.d_name, "device_id": device.id}
                dddd.append(data)
    if not len(dddd):
        response_data = {'code': ["963"], 'message': ["您当前没有关联的设备"]}
        return HttpResponse(json.dumps(response_data))
    devicename = dddd[0]["devicename"]
    print(devicename)
    now = datetime.datetime.now()
    d = Device.objects.filter(d_name=devicename)
    if not d:
        response_data = {'code': ["995"], 'message': ["设备不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    d = Device.objects.get(d_name=devicename)
    groups = DataGroup.objects.filter(dg_d_id=d, has_alert=1)
    print(groups)
    results = []
    # 每一组
    if not groups:
        response = {
            'message': ['设备未设置报警规则'],
            'code': ["200"],
            'data': results,
            'device': dddd,
            'present': dddd[0],
            'today': today,
            'status': ['无状态']
        }
        return HttpResponse(json.dumps(response))
    for group in groups:
        total += 1
        groupdict = {"status": '无数据', "name": '参数组名称', "value": '#', "range": ''}
        groupname = group.dg_name
        groupvalue = group.realtimevalue

        if groupvalue == '#':
            groupvalue = 0

        groupvalue = float(groupvalue)
        alert = Alert.objects.get(a_datagroup_id=group)
        high_line = alert.a_high_line
        low_line = alert.a_low_line
        range = str(low_line) + '-' + str(high_line)
        groupdict['range'] = range
        groupdict['name'] = groupname
        groupdict['value'] = groupvalue
        if groupvalue >= alert.a_highest_line and groupvalue != 0:
            groupdict['status'] = '过高'
            today += 1
        elif groupvalue >= high_line and groupvalue != 0:
            groupdict['status'] = '偏高'
            today += 1
        elif groupvalue <= alert.a_lowest_line and groupvalue != 0:
            groupdict['status'] = '过低'
            today += 1
        elif groupvalue < low_line and groupvalue != 0:
            groupdict['status'] = '偏低'
            today += 1
        elif groupvalue != 0:
            groupdict['status'] = '正常'
        results.append(groupdict)
    health = today / total
    if health < 0.6:
        status = '良好'
    if health < 0.8:
        status = '危险'
    else:
        status = '异常'
    response = {
        'message': ['返回成功'],
        'code': ["200"],
        'data': results,
        'device': dddd,
        'present': dddd[0],
        'today': today,
        'status': [status]
    }
    return HttpResponse(json.dumps(response))


def devicehealthv1(request):
    user_id = request.GET.get('user_id')
    device_id = request.GET.get('device_id')
    today = 0
    total = 0
    user = LoginUser.objects.get(id=user_id)
    if user.u_type == '公司管理员':
        company = Company.objects.get(id=user.u_company_id)
        a = Collectdevice.objects.filter(cd_c_id=company.id)
        dddd = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)
            for device in devices:
                data = {"devicename": device.d_name, "device_id": device.id}
                dddd.append(data)
    if user.u_type == '超级管理员':
        print('超级管理员')
        a = Collectdevice.objects.all()
        print(a)
        dddd = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)
            for device in devices:
                data = {"devicename": device.d_name, "device_id": device.id}
                dddd.append(data)
    typelist = ['超级管理员', '公司管理员']
    if user.u_type not in typelist:

        a = user.collectdevice.all()
        print(a)
        dddd = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)

            for device in devices:
                data = {"devicename": device.d_name, "device_id": device.id}
                dddd.append(data)
    if not len(dddd):
        response_data = {'code': ["963"], 'message': ["您当前没有关联的设备"]}
        return HttpResponse(json.dumps(response_data))
    now = datetime.datetime.now()
    print(device_id)
    d = Device.objects.filter(id=device_id)
    if not d:
        response_data = {'code': ["995"], 'message': ["设备不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    d = Device.objects.get(id=device_id)
    present = {"devicename": d.d_name, "device_id": d.id}
    print(d)

    groups = DataGroup.objects.filter(dg_d_id=d, has_alert=1)
    print(groups)
    results = []
    # 每一组
    if not groups:
        response = {
            'message': ['设备未设置报警规则'],
            'code': ["200"],
            'data': results,
            'device': dddd,
            'present': present,
            'today': today,
            'status': ['无状态']
        }
        return HttpResponse(json.dumps(response))
    for group in groups:
        total += 1
        groupdict = {"status": '无数据', "name": '参数组名称', "value": '', "range": ''}
        groupname = group.dg_name
        groupvalue = group.realtimevalue
        if groupvalue == '#':
            groupvalue = 0
        groupvalue = float(groupvalue)

        alert = Alert.objects.get(a_datagroup_id=group)
        high_line = alert.a_high_line
        low_line = alert.a_low_line
        range = str(low_line) + '-' + str(high_line)
        groupdict['range'] = range
        groupdict['name'] = groupname
        groupdict['value'] = groupvalue
        if groupvalue >= alert.a_highest_line and groupvalue != 0:
            groupdict['status'] = '过高'
            today += 1
        elif groupvalue >= high_line and groupvalue != 0:
            groupdict['status'] = '偏高'
            today += 1
        elif groupvalue <= alert.a_lowest_line and groupvalue != 0:
            groupdict['status'] = '过低'
            today += 1
        elif groupvalue < low_line and groupvalue != 0:
            groupdict['status'] = '偏低'
            today += 1
        elif groupvalue != 0:
            groupdict['status'] = '正常'
        results.append(groupdict)
    health = today / total
    if health < 0.6:
        status = '良好'
    if health < 0.8:
        status = '危险'
    else:
        status = '异常'
    response = {
        'message': ['返回成功'],
        'code': ["200"],
        'data': results,
        'device': dddd,
        'present': present,
        'today': today,
        'status': [status]
    }
    return HttpResponse(json.dumps(response))


def devicealarmlogs(request):
    device_id = request.GET.get('device_id')
    print(device_id)
    d = Device.objects.filter(id=device_id)
    if not d:
        response_data = {'code': ["995"], 'message': ["设备不存在或已被平台停用"]}
        return HttpResponse(json.dumps(response_data))
    d = Device.objects.get(id=device_id)
    present = {"devicename": d.d_name, "device_id": d.id}
    print(d)
    groups = DataGroup.objects.filter(dg_d_id=d, has_alert=1)
    print(groups)
    results = []
    # 每一组
    if not groups:
        response = {
            'message': ['设备未设置报警规则'],
            'code': ["200"]
        }
        return HttpResponse(json.dumps(response))
    for group in groups:
        groupdict = {"status": '正常', "name": '参数组名称', "value": '', "range": ''}
        groupname = group.dg_name
        groupvalue = group.realtimevalue
        groupvalue = float(groupvalue)
        alert = Alert.objects.get(a_datagroup_id=group)
        high_line = alert.a_high_line
        low_line = alert.a_low_line
        range = str(low_line) + '-' + str(high_line)
        groupdict['range'] = range
        groupdict['name'] = groupname
        groupdict['value'] = groupvalue
        if groupvalue >= alert.a_highest_line:
            groupdict['status'] = '过高'
        elif groupvalue >= high_line:
            groupdict['status'] = '偏高'
        elif groupvalue <= alert.a_lowest_line:
            groupdict['status'] = '过低'
        elif groupvalue < low_line:
            groupdict['status'] = '偏低'
        results.append(groupdict)
    response = {
        'message': ['返回成功'],
        'code': ["200"],
        'data': results,
        'present': present,
    }
    return HttpResponse(json.dumps(response))


def drawline1(f, g):
    timedata = []
    seriesdata = []
    name = f[0]["name"]
    for ff in f:
        time = ff["time"]
        timedata.append(time)
        value = ff["value"]
        value = float(value)
        value = round(value, 2)
        seriesdata.append(value)
    series = []
    dict = {'name': name, 'data': seriesdata}
    series.append(dict)
    data = {'RandomID': g, 'name': name, 'categories': timedata, "series": series}
    return data


class Uploaddefault(GenericAPIView):
    '''
    查询配件类
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        image1 = request.FILES.get('image')

        image = DefaultImage()
        image.name = name
        image.image = image1
        image.save()
        response = {
            'message': ['添加成功'],
            'code': ["200"]
        }
        return Response(response)


# 添加配件设备信息
class AddFittings(GenericAPIView):
    '''
    添加配件设备信息
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AddFittingsSerializer

    def post(self, request, *args, **kwargs):
        serializer = AddFittingsSerializer(data=request.data)
        if serializer.is_valid():
            fitting = Fittings()
            fitting.f_name = serializer.data['f_name']
            fitting.f_subject = FitSub.objects.get(fs_name=serializer.data['f_subject'])
            fitting.f_number = serializer.data['f_number']
            fitting.f_machine = serializer.data['f_machine']

            if request.POST.get("f_else"):
                fitting.f_else = request.POST.get("f_else")

            # try:
            #     fitting.f_else = serializer.data["f_else"]
            # except Exception as e:
            #     print("配件备注信息未上传")

            if request.FILES.get("f_picture") is None:
                fitting.f_image = DefaultImage.objects.get(name='配件设备').image
            else:
                fitting.f_image = request.FILES.get("f_picture")
            fitting.save()
            response = {
                'message': ['配件信息创建成功'],
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 修改配件设备信息
class ChangeFittings(GenericAPIView):
    '''
    修改知识库/行业资讯解决方案，需后台人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ChangeFittingsSerializer

    def post(self, request, *args, **kwargs):
        serializer = ChangeFittingsSerializer(data=request.data)
        if serializer.is_valid():
            fitting = Fittings.objects.get(id=serializer.data['f_id'])
            fitting.f_name = serializer.data['f_name']
            fitting.f_subject = FitSub.objects.get(fs_name=serializer.data['f_subject'])
            fitting.f_number = serializer.data['f_number']
            fitting.f_machine = serializer.data['f_machine']

            try:
                fitting.f_else = serializer.data["f_else"]
            except Exception as e:
                print("配件备注信息未上传")

            if request.FILES.get("f_picture") is None:
                fitting.f_image = DefaultImage.objects.get(id=1).image
            else:
                fitting.f_image = request.FILES.get("f_picture")
            fitting.save()
            response = {
                'message': ['配件信息修改成功'],
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 删除配件设备信息
class DeleteFittings(GenericAPIView):
    '''
    删除知识库/行业资讯解决方案，需后台人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DeleteFittingsSerializer

    def post(self, request, *args, **kwargs):
        serializer = DeleteFittingsSerializer(data=request.data)
        if serializer.is_valid():
            fitting = Fittings.objects.get(id=serializer.data['f_id'])

            fitting.delete()
            response = {
                'message': ['配件信息删除成功'],
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 查询配件设备信息
class SelectFittings(GenericAPIView):
    '''
    查询单个配件设备信息
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = SelectFittingsSerializer

    def post(self, request, *args, **kwargs):
        serializer = SelectFittingsSerializer(data=request.data)
        if serializer.is_valid():
            fit = Fittings.objects.get(id=serializer.data['f_id'])
            f_sub_name = FitSub.objects.get(id=fit.f_subject_id).fs_name

            data = {}
            data["fit_name"] = fit.f_name
            data["f_sub"] = f_sub_name
            data["f_else"] = fit.f_else
            data["f_machine"] = fit.f_machine
            data["f_number"] = fit.f_number
            data["f_image"] = str(fit.f_image)
            data["f_sub_id"] = fit.f_subject_id

            response_data = {'code': ["200"], 'data': data}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# 增加配件类
class AddFitSub(GenericAPIView):
    """增加配件类"""

    authentication_classes = []
    permission_classes = []
    serializer_class = AddFitSubSerializer

    def post(self, request, *args, **kwargs):
        serializer = AddFitSubSerializer(data=request.data)
        if serializer.is_valid():
            fitsub = FitSub()
            fitsub.fs_name = serializer.data['f_name']

            fitsub.save()
            response = {
                'message': ['配件类信息创建成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 根据配件类查询设备信息
class SelectFitAccSub(GenericAPIView):
    '''
    根据配件类查询设备信息
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = SelectFitAccSubSerializer

    def post(self, request, *args, **kwargs):
        serializer = SelectFitAccSubSerializer(data=request.data)
        if serializer.is_valid():
            fitting = Fittings.objects.filter(f_subject_id=serializer.data['sub_id'])
            if not fitting:
                response_data = {'code': ["953"], 'message': "此配件类下目前没有配件"}
                return HttpResponse(json.dumps(response_data))
            data1 = []

            f_sub_name = FitSub.objects.get(id=serializer.data['sub_id']).fs_name

            # print(fitting)
            for fit in fitting:
                data = {}
                data["fit_name"] = fit.f_name
                data["f_else"] = fit.f_else
                data["f_machine"] = fit.f_machine
                data["f_number"] = fit.f_number
                data["f_image"] = str(fit.f_image)
                data["f_sub_id"] = fit.f_subject_id
                data["f_id"] = fit.id
                data1.append(data)

            response_data = {"sub_name": f_sub_name, 'code': ["200"], 'data': data1}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)

# 查询配件类
class SelectFitSub(GenericAPIView):
    '''
    查询配件类
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = SelectFitSubSerializer

    def post(self, request, *args, **kwargs):
        serializer = SelectFitSubSerializer(data=request.data)
        if serializer.is_valid():
            fitsub = FitSub.objects.all()
            if not fitsub:
                response_data = {'code': ["951"], 'message': "配件类型不存在"}
                return HttpResponse(json.dumps(response_data))
            objJson = serialize("json", fitsub)
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# 删除配件类
class DeleteFitSub(GenericAPIView):
    """
    删除配件类
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = DeleteFitSubSerializer

    def post(self, request, *args, **kwargs):
        serializer = DeleteFitSubSerializer(data=request.data)
        if serializer.is_valid():
            fitsub = FitSub.objects.get(id=serializer.data["fs_id"])
            fitsub.delete()
            response = {
                'message': ['配件类信息删除成功'],
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class uploaddefault(GenericAPIView):
    '''
    查询配件类
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        image1 = request.FILES.get('image')

        image = DefaultImage()
        image.name = name
        image.image = image1
        image.save()
        response = {
            'message': ['添加成功'],
            'code': ["200"]
        }
        return HttpResponse(json.dumps(response))


class DeviceStatus(GenericAPIView):
    '''
    正常设备，异常设备
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DeviceStatusSerializer

    def post(self, request, *args, **kwargs):
        serializer = DeviceStatusSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['user_id']
            user = LoginUser.objects.get(id=user_id)
            if user.u_type == '公司管理员':
                company = Company.objects.get(id=user.u_company_id)
                co = Collectdevice.objects.filter(cd_c_id=company.id)
                if not co:
                    response = {
                        'message': ['公司不存在任何设备'],
                        'code': ["932"]
                    }
                    return HttpResponse(json.dumps(response))
                health = 0
                unhealth = 0
                for c in co:
                    healthdevices = Device.objects.filter(d_c_id=c.id, d_status='健康')
                    healthcount = healthdevices.count()
                    totaldevices = Device.objects.filter(d_c_id=c.id)
                    alarmlogscount = 0
                    for totaldevice in totaldevices:
                        alarmlogs = AlarmLog.objects.filter(log_device=totaldevice)
                        alarmlogs = alarmlogs.count()
                        alarmlogscount += alarmlogs
                    totalcount = totaldevices.count()
                    unhealthcount = totalcount - healthcount
                    health += healthcount
                    unhealth += unhealthcount
                response = {
                    'health': health,
                    'unhealth': unhealth,
                    'alarmlogscount': alarmlogscount,
                    'code': ["200"]
                }
                return HttpResponse(json.dumps(response))
            if user.u_type == '超级管理员':
                co = Collectdevice.objects.all()
                if not co:
                    response = {
                        'message': ['采集设备不存在'],
                        'code': ["946"]
                    }
                    return HttpResponse(json.dumps(response))
                health = 0
                unhealth = 0
                for c in co:
                    healthdevices = Device.objects.filter(d_c_id=c.id, d_status='健康')
                    healthcount = healthdevices.count()
                    totaldevices = Device.objects.filter(d_c_id=c.id)
                    alarmlogscount = 0
                    for totaldevice in totaldevices:
                        alarmlogs = AlarmLog.objects.filter(log_device=totaldevice)
                        alarmlogs = alarmlogs.count()
                        alarmlogscount += alarmlogs
                    totalcount = totaldevices.count()
                    unhealthcount = totalcount - healthcount
                    health += healthcount
                    unhealth += unhealthcount
                response = {
                    'health': health,
                    'unhealth': unhealth,
                    'alarmlogscount': alarmlogscount,
                    'code': ["200"]
                }
                return HttpResponse(json.dumps(response))

            co = user.collectdevice.all()
            if not co:
                response = {
                    'message': ['您尚未关联任何设备'],
                    'code': ["933"]
                }
                return HttpResponse(json.dumps(response))
            health = 0
            unhealth = 0
            for c in co:
                healthdevices = Device.objects.filter(d_c_id=c.id, d_status='健康')
                healthcount = healthdevices.count()
                totaldevices = Device.objects.filter(d_c_id=c.id)
                alarmlogscount = 0
                for totaldevice in totaldevices:
                    alarmlogs = AlarmLog.objects.filter(log_device=totaldevice)
                    alarmlogs = alarmlogs.count()
                    alarmlogscount += alarmlogs
                totalcount = totaldevices.count()
                unhealthcount = totalcount - healthcount
                health += healthcount
                unhealth += unhealthcount
            response = {
                'health': health,
                'unhealth': unhealth,
                'alarmlogscount': alarmlogscount,
                'code': ["200"]
            }
            return HttpResponse(json.dumps(response))
        return Response(serializer.errors)


class HealthDeviceList(GenericAPIView):
    '''
    正常设备，异常设备
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DeviceStatusSerializer

    def post(self, request, *args, **kwargs):
        serializer = DeviceStatusSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['user_id']
            user = LoginUser.objects.get(id=user_id)

            if user.u_type == '公司管理员':
                company = Company.objects.get(id=user.u_company_id)
                co = Collectdevice.objects.filter(cd_c_id=company.id)
                devices = Device.objects.filter(d_status='332523健康')
                for c in co:
                    device = Device.objects.filter(d_c_id=c.id, d_status='健康')
                    devices = devices | device

                objJson = serialize("json", devices)
                objStr = json.loads(objJson)
                response_data = {'code': ["200"], 'data': objStr}
                return HttpResponse(json.dumps(response_data))
            if user.u_type == '超级管理员':
                co = Collectdevice.objects.all()
                devices = Device.objects.filter(d_status='332523健康')
                for c in co:
                    device = Device.objects.filter(d_c_id=c.id, d_status='健康')
                    devices = devices | device

                objJson = serialize("json", devices)
                objStr = json.loads(objJson)
                response_data = {'code': ["200"], 'data': objStr}
                return HttpResponse(json.dumps(response_data))

            co = user.collectdevice.all()
            devices = Device.objects.filter(d_status='332523健康')
            for c in co:
                device = Device.objects.filter(d_c_id=c.id, d_status='健康')
                devices = devices | device

            objJson = serialize("json", devices)
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


class UnHealthDeviceList(GenericAPIView):
    '''
    正常设备，异常设备
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DeviceStatusSerializer

    def post(self, request, *args, **kwargs):
        serializer = DeviceStatusSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['user_id']
            user = LoginUser.objects.get(id=user_id)

            if user.u_type == '公司管理员':
                company = Company.objects.get(id=user.u_company_id)
                co = Collectdevice.objects.filter(cd_c_id=company.id)
                devices = Device.objects.filter(d_status='332523健康')
                for c in co:
                    device = Device.objects.filter(d_c_id=c.id, d_status='异常')
                    devices = devices | device

                objJson = serialize("json", devices)
                objStr = json.loads(objJson)
                response_data = {'code': ["200"], 'data': objStr}
                return HttpResponse(json.dumps(response_data))
            if user.u_type == '超级管理员':
                co = Collectdevice.objects.all()
                devices = Device.objects.filter(d_status='332523健康')
                for c in co:
                    device = Device.objects.filter(d_c_id=c.id, d_status='异常')
                    devices = devices | device

                objJson = serialize("json", devices)
                objStr = json.loads(objJson)
                response_data = {'code': ["200"], 'data': objStr}
                # response_data = {'code': ["200"], 'data': qs}
                return HttpResponse(json.dumps(response_data))

            co = user.collectdevice.all()
            devices = Device.objects.filter(d_status='332523健康')
            for c in co:
                device = Device.objects.filter(d_c_id=c.id, d_status='异常')
                devices = devices | device

            objJson = serialize("json", devices)
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# 返回所有配件类与类下数据
class SelectAllFit(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def post(self, request, *args, **kwargs):
        a = FitSub.objects.all()
        if not a:
            response_data = {'code': ["951"], 'message': "配件类型不存在"}
            return HttpResponse(json.dumps(response_data))
        d = []

        for i in a:  # 每个类

            fits = Fittings.objects.filter(f_subject_id=i.id)
            subject = i.fs_name
            sub_id = i.id
            b = []
            for fit in fits:
                data = {"fit": fit.f_name, 'ID': fit.id}
                b.append(data)
            c = {'subject': subject, 'fit': b, 'sub_id': sub_id}
            d.append(c)
        response_data = {'code': ["200"], 'data': d}
        return HttpResponse(json.dumps(response_data))


class CompanyProList(GenericAPIView):
    """
    公司项目列表
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def post(self, request, *args, **kwargs):
        a = Company.objects.filter(active=1)
        d = []
        for i in a:  # 每个公司
            projects = Project.objects.filter(p_c_id=i.id, p_active=1)
            subject = i.company_name
            sub_id = i.id
            b = []
            for project in projects:
                data = {"project": project.p_name, 'ID': project.id}
                b.append(data)
            c = {'subject': subject, 'project': b, 'company_id': sub_id}
            d.append(c)
        response_data = {'code': ["200"], 'data': d}
        return HttpResponse(json.dumps(response_data))


class PersonDevicelistV1(GenericAPIView):
    """
    查看用户设备列表
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        user = LoginUser.objects.get(id=user_id)
        if user.u_type == '公司管理员':
            company = Company.objects.get(id=user.u_company_id)
            a = Collectdevice.objects.filter(cd_c_id=company.id)
            d = []
            for collectdevice in a:  # 每个采集设备
                devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)
                subject = collectdevice.cd_name
                sub_id = collectdevice.id

                for device in devices:
                    b = []
                    subject = device.d_c_id.cd_name
                    deviceattt = []
                    deviceatts = Devicedata.objects.filter(ddd_d_id=device)
                    if deviceatts:
                        for deviceatt in deviceatts:
                            att = {'name': '', 'detail': ''}
                            att["name"] = deviceatt.ddd_name
                            att['detail'] = deviceatt.ddd_detail
                            deviceattt.append(att)
                    data = {'d_company_number': device.d_company_number, "devicename": device.d_name, 'ID': device.id,
                            'd_GPS': device.d_GPS,
                            'd_manufacturer': device.d_manufacturer, 'd_status': device.d_status,
                            'd_produce_time': device.d_produce_time, 'Boolean': True, 'deviceatt': deviceattt}

                    b.append(data)
                    c = {'subject': subject, 'devices': b, 'collectdevice_id': sub_id}
                    d.append(c)
            response_data = {'code': ["200"], 'data': d}
            return Response(response_data)
        if user.u_type == '超级管理员':
            print('超级管理员')
            a = Collectdevice.objects.all()
            print(a)
            d = []
            for collectdevice in a:  # 每个采集设备
                devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)
                subject = collectdevice.cd_name
                sub_id = collectdevice.id

                for device in devices:
                    b = []
                    subject = device.d_c_id.cd_name
                    deviceattt = []
                    deviceatts = Devicedata.objects.filter(ddd_d_id=device)
                    if deviceatts:
                        for deviceatt in deviceatts:
                            att = {'name': '', 'detail': ''}
                            att["name"] = deviceatt.ddd_name
                            att['detail'] = deviceatt.ddd_detail
                            deviceattt.append(att)
                    data = {"devicename": device.d_name, 'ID': device.id, 'd_GPS': device.d_GPS,
                            'd_manufacturer': device.d_manufacturer, 'd_status': device.d_status,
                            'd_produce_time': device.d_produce_time, 'Boolean': True, 'deviceatt': deviceattt}

                    b.append(data)
                    c = {'subject': subject, 'devices': b, 'collectdevice_id': sub_id}
                    d.append(c)
            response_data = {'code': ["200"], 'data': d}
            return Response(response_data)
        a = user.collectdevice.all()
        print(a)
        d = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)
            subject = collectdevice.cd_name
            sub_id = collectdevice.id

            for device in devices:
                b = []
                subject = device.d_c_id.cd_name
                deviceattt = []
                deviceatts = Devicedata.objects.filter(ddd_d_id=device)
                if deviceatts:
                    for deviceatt in deviceatts:
                        att = {'name': '', 'detail': ''}
                        att["name"] = deviceatt.ddd_name
                        att['detail'] = deviceatt.ddd_detail
                        deviceattt.append(att)
                data = {"devicename": device.d_name, 'ID': device.id, 'd_GPS': device.d_GPS,
                        'd_manufacturer': device.d_manufacturer, 'd_status': device.d_status,
                        'd_produce_time': device.d_produce_time, 'Boolean': True, 'deviceatt': deviceattt}

                b.append(data)
                c = {'subject': subject, 'devices': b, 'collectdevice_id': sub_id}
                d.append(c)
        response_data = {'code': ["200"], 'data': d}
        return Response(response_data)


class PersonDevicelistV2(GenericAPIView):
    """
    查看用户设备列表
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        user = LoginUser.objects.get(id=user_id)
        if user.u_type == '公司管理员':
            company = Company.objects.get(id=user.u_company_id)
            a = Collectdevice.objects.filter(cd_c_id=company.id)
            d = []
            for collectdevice in a:  # 每个采集设备
                devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)

                for device in devices:
                    data = {"devicename": device.d_name}
                    d.append(data)
            response_data = {'code': ["200"], 'data': d}
            return Response(response_data)
        if user.u_type == '超级管理员':
            print('超级管理员')
            a = Collectdevice.objects.all()
            print(a)
            d = []
            for collectdevice in a:  # 每个采集设备
                devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)
                for device in devices:
                    data = {"devicename": device.d_name}
                    d.append(data)
            response_data = {'code': ["200"], 'data': d}
            return Response(response_data)
        a = user.collectdevice.all()
        print(a)
        d = []
        for collectdevice in a:  # 每个采集设备
            devices = Device.objects.filter(d_c_id=collectdevice, d_active=1)

            for device in devices:
                data = {"devicename": device.d_name}
                d.append(data)
        response_data = {'code': ["200"], 'data': d}
        return Response(response_data)


def searchlistresult(user_id, project, d_name):
    devices = []
    user = LoginUser.objects.get(id=user_id)
    if user.u_type == '设备管理员':
        devices = Device.objects.filter(d_name__icontains=d_name, d_p_id=project)
    if user.u_type == '公司管理员':
        devices = Device.objects.filter(d_name__icontains=d_name, d_co_id=user.u_company_id)
    if user.u_type in ['运维顾问', '客服运营', '超级管理员']:
        devices = Device.objects.all().order_by('d_co_id')
    if not devices:
        return
    b = []
    d = []
    for device in devices:
        subject = device.d_c_id.cd_name
        sub_id = device.d_c_id.id
        deviceattt = []
        deviceatts = Devicedata.objects.filter(ddd_d_id=device)
        if deviceatts:
            for deviceatt in deviceatts:
                att = {'name': '', 'detail': ''}
                att["name"] = deviceatt.ddd_name
                att['detail'] = deviceatt.ddd_detail
                deviceattt.append(att)
        data = {"devicename": device.d_name, 'ID': device.id, 'd_GPS': device.d_GPS,
                'd_manufacturer': device.d_manufacturer, 'd_status': device.d_status,
                'd_produce_time': device.d_produce_time, 'Boolean': True, 'deviceatt': deviceattt}

        b.append(data)
        c = {'subject': subject, 'devices': b, 'collectdevice_id': sub_id}
        d.append(c)
    return d


from django.db.models import Sum


class CompanyProListV1(GenericAPIView):
    """
    公司项目列表
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def post(self, request, *args, **kwargs):
        alarm_sum_group_items = Project.objects.filter(p_active=1).annotate(alarm_sum=Sum('collectdevice'))
        print(alarm_sum_group_items)
        objJson = serialize("json", alarm_sum_group_items)
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
        return HttpResponse(json.dumps(response_data))


# 修改配件设备信息
class FixFitSub(GenericAPIView):
    '''
    修改配件类信息
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = FixFitSubSerializer

    def post(self, request, *args, **kwargs):
        serializer = FixFitSubSerializer(data=request.data)
        if serializer.is_valid():
            fitsub = FitSub.objects.get(id=serializer.data['f_id'])
            fitsub.fs_name = serializer.data['f_name']
            fitsub.save()
            response = {
                'message': ['配件信息修改成功'],

                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 模糊查询配件
class SelectAboveFit(APIView):
    '''
    查询配件类
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        f_name = request.GET.get('f_name')

        if not f_name:
            response_data = {'code': ["950"], 'data': "不能输入空值"}
            return HttpResponse(json.dumps(response_data))
        fits = Fittings.objects.filter(f_name__icontains=f_name)

        if not fits:
            response_data = {'code': ["949"], 'data': "没有找到与输入值相关的配件"}
            return HttpResponse(json.dumps(response_data))
        data1 = []
        for fit in fits:
            data = {"f_id": fit.id, "fit_name": fit.f_name, "f_sub": FitSub.objects.get(id=fit.f_subject_id).fs_name,
                    "f_else": fit.f_else, "f_machine": fit.f_machine, "f_number": fit.f_number,
                    "f_image": str(fit.f_image), "f_sub_id": fit.f_subject_id}

            data1.append(data)

        response_data = {"sub_name": f_name, 'code': ["200"], 'data': data1}
        return HttpResponse(json.dumps(response_data))


# 大屏左屏控制台数据统计
class CompanyControl(APIView):
    '''
    大屏左屏控制台数据统计
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        company_id = request.GET.get('company_id')
        company = Company.objects.filter(id=company_id, active=1)
        if company:
            company = Company.objects.get(id=company_id)
            alarmlogs = AlarmLog.objects.filter(log_company=company)
            i = 0
            if alarmlogs:
                for a in alarmlogs:
                    i += 1
            healthydevice = Device.objects.filter(d_co_id=company, d_status='健康')
            j = 0
            if healthydevice:
                for h in healthydevice:
                    j += 1
            totaldevice = Device.objects.filter(d_co_id=company)
            k = 0
            if totaldevice:
                for t in totaldevice:
                    k += 1
            k = k - j
            response_data = {'code': ["200"], "totalalarm": i, "healthydevice": j, "unhealthydevice": k}
            return HttpResponse(json.dumps(response_data))
        response_data = {'code': ["200"], "message": ["公司不存在或已停用"]}
        return HttpResponse(json.dumps(response_data))


class MonthAlarm(APIView):
    '''
    大屏左屏设备月度报警统计
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        company_id = request.GET.get('company_id')
        month = request.GET.get('month')
        if not month:
            month = datetime.datetime.now().month
        company = Company.objects.filter(id=company_id, active=1)
        # 饼图
        piedata = []
        # 柱状图
        barxdata = []
        bardata = []
        if company:
            company = Company.objects.get(id=company_id)
            devices = Device.objects.filter(d_co_id=company_id)
            if devices:
                colorindex = 0
                for device in devices:
                    piedict = {"value": 0, "name": None}
                    bardict = {"value": 0, "itemStyle": None}
                    itemstyle = {"color": color[colorindex]}
                    colorindex += 1
                    alarmlogs = AlarmLog.objects.filter(log_device=device, log_time__month=month)
                    i = 0
                    if alarmlogs:
                        for alarmlog in alarmlogs:
                            i += 1
                    piedict['value'] = i
                    piedict['name'] = device.d_name
                    piedata.append(piedict)
                    bardict['value'] = i
                    bardict['itemStyle'] = itemstyle
                    bardata.append(bardict)
                    barxdata.append(device.d_name)
            # 柱状图
            barxaxis = {"type": 'category', "data": barxdata}
            baryaxis = {"type": 'value'}
            bardatadict = {'data': bardata, 'type': 'bar'}
            barseries = [bardatadict]
            bartooltip = {'trigger': 'axis'}
            bar = {"xAxis": barxaxis, "yAxis": baryaxis, "tooltip": bartooltip, "series": barseries}
            # 饼图
            pielegend = {'orient': 'vertical', 'left': 'left'}
            pielabel = {'positon': 'top', "fontSize": 16}
            pieitemstyle = {'shadowBlur': 10, 'shadowOffsetX': 0, 'shadowColor': 'rgba(0, 0, 0, 0.5)'}
            pieemphasis = {'itemStyle': pieitemstyle}
            pieseriesdict = {"type": 'pie', "radius": '50%', 'label': pielabel, 'data': piedata,
                             'emphasis': pieemphasis}
            pieseries = [pieseriesdict]
            pie = {'lengend': pielegend, 'series': pieseries}
            response_data = {'code': ["200"], "bar": bar, "pie": pie}
            return HttpResponse(json.dumps(response_data))
        response_data = {'code': ["998"], "message": ['公司不存在或已被平台停用']}
        return HttpResponse(json.dumps(response_data))


class YearAlarm(APIView):
    '''
    大屏左屏设备年度报警统计
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        company_id = request.GET.get('company_id')
        year = request.GET.get('year')
        if not year:
            year = datetime.datetime.now().year
        company = Company.objects.filter(id=company_id, active=1)
        date = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
        dateindex = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        if company:
            company = Company.objects.get(id=company_id)
            data = []
            for d in dateindex:
                alarmlogs = AlarmLog.objects.filter(log_company=company, log_time__year=year, log_time__month=d)
                i = 0
                if alarmlogs:
                    i = alarmlogs.count()
                data.append(i)
            # 柱状图
            xaxis = {"type": 'category', 'boundaryGap': False, "data": date}
            tooltip = {'trigger': 'axis'}
            grid = {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': True}
            yaxis = {"type": 'value'}
            datadict = {'data': data, 'type': 'line'}
            series = [datadict]
            bar = {"tooltip": tooltip, "grid": grid, "xAxis": xaxis, "yAxis": yaxis, "series": series}
            response_data = {'code': ["200"], "data": bar}
            return HttpResponse(json.dumps(response_data))
        response_data = {'code': ["998"], "message": ['公司不存在或已被平台停用']}
        return HttpResponse(json.dumps(response_data))


class AlarmList(GenericAPIView):
    '''
    删除数据告警规则,需要用户为公司管理人员或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []  # 权限判断相同

    def get(self, request, *args, **kwargs):
        company_id = request.GET.get('company_id')
        company = Company.objects.filter(id=company_id, active=1)
        if company:
            alert = AlarmLog.objects.filter(log_company=company).values('id', 'log_name',
                                                                        'log_alarm_type',
                                                                        'log_alarm_data',
                                                                        'log_device__d_name',
                                                                        'log_project__p_name',
                                                                        'log_group_name',
                                                                        'log_message',
                                                                        'log_type',
                                                                        'log_time').order_by('-log_time')[:30]
            response_data = {'code': ['200'], 'data': alert}
            return Response(response_data)
        response_data = {'code': ["998"], "message": ['公司不存在或已被平台停用']}
        return HttpResponse(json.dumps(response_data))


from itertools import chain


def uniontest(request):
    jan = DataLogJan2021.objects.all()
    feb = DataLogFeb2021.objects.all()
    mar = DataLogMar2021.objects.all()
    result = chain(jan, feb, mar)
    for r in result:
        print(r.dl_g_id)
        print(r.dl_month)
        print(r.dl_time)
        print(r.dl_value)

    return HttpResponse('s')

def qrcode(request):
    code = request.GET.get('code')
    if not code:
        return HttpResponse('用户禁止授权')
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    params = {
        'appid':'wx18df29006e42bcf9',
        'secret':'531c7e8e3f73048bbd9f40156eeae3eb',
        'code': code,
        'grant_type': 'authorization_code'
    }
    resp = requests.get(url, params=params).json()
    access_tokenn = resp["access_token"]  # 只是呈现给大家看,可以删除这行
    openidd = resp["openid"]  # 只是呈现给大家看,可以删除这行
    print(access_tokenn)
    print(openidd)
    user_info_url = 'https://api.weixin.qq.com/sns/userinfo'
    params = {
        'access_token': resp["access_token"],
        'openid': resp["openid"],
    }
    resp = requests.get(user_info_url, params=params)
    print(resp)
    response = resp.content.decode()  # str
    r_str = json.loads(response)  # dict
    print(r_str)
    openid = jsonpath(r_str, '$.openid')
    openid = openid[0]

    print('成功获取到用户微信数据')
    user = LoginUser.objects.filter(openid=openid)
    print(user)
    if not user:
        response_data = {'code': ["999"], 'message': ['用户不存在']}
        return HttpResponse(json.dumps(response_data))
    objJson = serialize("json", user)
    objStr = json.loads(objJson)
    user = LoginUser.objects.get(openid=openid)
    if user.u_company_id:
        company = Company.objects.filter(id=user.u_company_id)
        if company:
            company = Company.objects.get(id=user.u_company_id)
            response_data = {'code': ["200"], 'data': objStr, 'companyname': company.company_name}
            return HttpResponse(json.dumps(response_data))
    companyname = '无'
    identity = '前台'
    type = user.u_type
    u_type = ['超级管理员', '运维顾问', '客服运营']
    if type in u_type:
        identity = '后台'
    print(identity)
    response_data = {'code': ["200"], 'data': objStr, 'companyname': companyname}
    response = HttpResponse(json.dumps(response_data))
    return response


def qrcodev1(request):
    code = request.GET.get('code')
    user_id = request.GET.get('user_id')
    if not code:
        return HttpResponse('用户禁止授权')
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    params = {
        'appid':'wx18df29006e42bcf9',
        'secret':'531c7e8e3f73048bbd9f40156eeae3eb',
        'code': code,
        'grant_type': 'authorization_code'
    }
    resp = requests.get(url, params=params).json()
    access_tokenn = resp["access_token"]  # 只是呈现给大家看,可以删除这行
    openidd = resp["openid"]  # 只是呈现给大家看,可以删除这行
    print(access_tokenn)
    print(openidd)
    user_info_url = 'https://api.weixin.qq.com/sns/userinfo'
    params = {
        'access_token': resp["access_token"],
        'openid': resp["openid"],
    }
    resp = requests.get(user_info_url, params=params)
    print(resp)
    response = resp.content.decode()  # str
    r_str = json.loads(response)  # dict
    print(r_str)
    openid = jsonpath(r_str, '$.openid')
    openid = openid[0]

    print('成功获取到用户微信数据')
    user = LoginUser.objects.filter(id=user_id)
    print(user)
    if not user:
        response_data = {'code': ["999"], 'message': ['用户不存在']}
        return HttpResponse(json.dumps(response_data))
    user = user[0]
    user.openid = openid
    user.save()

    response_data = {'code': ["200"], 'message': ['绑定成功']}
    response = HttpResponse(json.dumps(response_data))
    return response

def qrcodev2(request):
    user_id = request.GET.get('user_id')
    user = LoginUser.objects.filter(id=user_id)
    print(user)
    if not user:
        response_data = {'code': ["999"], 'message': ['用户不存在']}
        return HttpResponse(json.dumps(response_data))
    user = user[0]
    print(user)
    user.openid = 1
    user.save()

    response_data = {'code': ["200"], 'message': ['解绑成功']}
    response = HttpResponse(json.dumps(response_data))
    return response

def deletedata(request):
    data = DataLogFeb2021.objects.all()
    data.delete()
    response_data = {'code': ["998"], "message": ['公司不存在或已被平台停用']}

    return HttpResponse(json.dumps(response_data))
# import time
def historydata(request):
    """
        对某设备的所有参数组 进行单独的webaccess数据获取，并将三个数据进行判断取其一返回前端
        :param request: 机械设备ID device_id
        :return:
        """
    print('---------开始读取昨日历史数据-----------')
    now = datetime.datetime.now()
    # print(now)
    i = 0
    # datacount = Data.objects.filter(d_g_id=40).count()
    datacount = Data.objects.all().count()
    # print(datacount)
    cycle = int((datacount + 1) / 50)
    for i in range(cycle + 1):
        if i == 0:
            print('等于0')
            start = 0
            end = 10
            datas = Data.objects.all().order_by('id')[0:51]
            # datas = Data.objects.all(d_g_id=40).order_by('id')[0:51]
            # print(datas)
            print(start)
            print(end)
        if i == cycle:
            print('等于最后')
            start = i * 50 + 1
            end = datacount
            datas = Data.objects.all()[start:end]
            # datas = Data.objects.filter(d_g_id=40)[start:end]
            print(start)
            print(end)
        if i > 0 and i != cycle:
            start = i * 50 + 1
            end = (i + 1) * 50 + 1
            print(start)
            print(end)
            datas = Data.objects.all()[start:end]

        now = datetime.datetime.now()
        time = timedelta(sign='d', value=-1, dt=now)
        time = time.strftime('%Y-%m-%d')
        time = time + ' 00:00:01'
        # time = now.strftime('%Y-%m-%d %H:%M:%S')
        ProjectName = 'test'
        url = ip + 'WaWebService/Json/GetDataLog' + '/' + ProjectName + '/' + 'node1'
        headers = {"Content-Type": "application/json"}
        # request数据格式,Total指有几个tag
        format_header0 = '{"StartTime":"'
        format_header0 = format_header0 + str(time)
        format_header1 = '","IntervalType":"M","Interval":10,"Records":144'
        format_header = format_header0 + format_header1 + ',"Tags": '
        format_tail = '}'
        taglist = []
        for data in datas:
            name = data.d_name
            taglistchild = {"Name": str(name), "DataType": 0}
            taglist.append(taglistchild)
        print(taglist)
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
        print(r_str)
        # try:
        realtimevalue = jsonpath(r_str, '$.DataLog..Values')
        realtimetag = jsonpath(r_str, '$.DataLog..Name')
        print(realtimetag)
        datarange = len(realtimetag)
        # datarange = datarange + 1
        print(datarange)
        j = 0
        for j in range(datarange):
            time1 = timedelta(sign='d', value=-1, dt=now)
            print(j)
            tagname = realtimetag[j]
            print(tagname)
            thisdata = Data.objects.get(d_name=tagname)
            datagroup = thisdata.d_g_id
            tagvaluelist = realtimevalue[j]
            print(tagvaluelist)
            valueindex = 0
            for value in tagvaluelist:
                if valueindex == 0:
                    valueindex += 1
                    k = value
                    datalog = DataLogFeb2021()
                    datalog.dl_value = value
                    datalog.dl_g_id = datagroup
                    datalog.dl_d_name = thisdata.d_name
                    time1 = timedelta(sign='n', value=10, dt=time1)
                    datalog.dl_time = time1
                    datalog.dl_month = now.month
                    datalog.save()
                if k == value:
                    time1 = timedelta(sign='n', value=10, dt=time1)
                if k != value and value != '#':
                    k = value
                    datalog = DataLogFeb2021()
                    datalog.dl_value = value
                    datalog.dl_g_id = datagroup
                    datalog.dl_d_name = thisdata.d_name
                    time1 = timedelta(sign='n', value=10, dt=time1)
                    datalog.dl_time = time1
                    datalog.dl_month = now.month
                    datalog.save()

        now = datetime.datetime.now()
        print(now)
        print(i)
        print('---------------------功能结束------------------')
    response_data = {'code': ["998"], "message": ['公司不存在或已被平台停用']}
    return HttpResponse(json.dumps(response_data))




# 建立公告，发送公告
class SendAnnouncement(GenericAPIView):
    """
    建立公告 ，发送公告
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = SendAnnounceSerializer(data=request.data)
        if serializer.is_valid():
            # set_time = serializer.data['set_time']

            announce = Announce()
            announce.head = serializer.data["head"]
            announce.datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
            announce.content = serializer.data['a_content']
            announce.sender_id = serializer.data["user_id"]
            user = LoginUser.objects.get(id=serializer.data["user_id"])

            if user.u_type == "运维" or user.u_type == "超级管理员":
                announce.type = 0
                announce.status = 3  # 公告设置成未读
                announce.save()
                userlist = LoginUser.objects.all()
                global frontuser
                #  给所有用户添加信息
                for user in userlist:
                    user.message.add(announce)
                response = {
                    'message': ['系统通知创建成功'],
                    'code': ["200"]
                }
            elif user.u_type in frontuser:  # 前台用户
                announce.type = 1  # 用户自己设置的通知为1
                announce.status = 1  # 消息状态设置为未发送
                announce.set_time = serializer.data['set_time']
                announce.singnal = 1
                announce.save()
                user.message.add(announce)
                set_time = datetime.strptime(serializer.data['set_time'], '%Y-%m-%dT%H:%M:%S')

                # 因重启系统后定时任务都消失 定时任务改为每天8点发送当天的预约提醒
                # 代码再主url中

                # 只给此员工创建定时任务
                def func():
                    announce.status = 3  # 信息设置成未读状态 1 未发送 2 已读 3 发送但未读
                    announce.save()

                # 定时任务
                scheduler.add_job(func, 'date',
                                  run_date=datetime(set_time.year, set_time.month, set_time.day, set_time.hour,
                                                    set_time.minute), id=str(announce.id))


                response = {
                    'message': ['保养提醒创建成功'],
                    'code': ["200"]
                }

            return Response(response, status=200)

        return Response(serializer.errors)


# # 发送站内消息
# sender = LoginUser.objects.get(id=serializer.data['user_id'])  # 发送者 一般是超级管理员
# # print(type(sender))
# # notify.send(user=发送者,recipient=接收者,verb="通知内容",action_object=动作发出的起点)
# recipient = LoginUser.objects.exclude(id=serializer.data["user_id"])  # 接收者 一般是除了发送者之外的所有用户
# # print(recipient)
# verb = "{0}发布了公告{1}".format(sender, strip_tags(serializer.data['a_content']))
# # print(verb)
# notify.send(sender, recipient=recipient, verb=verb, action_object=announce)

# 时间比较大小  前面时间大于后面时间 返回0 ，否则返回1
def CompareTime(front_time, last_time):
    if int(front_time.strftime("%Y%m%d")) >= int(last_time.strftime("%Y%m%d")):
        return 0
    else:
        return 1

# 任意用户查询的单个公告
class SelectAnnounce(GenericAPIView):
    '''
    查询单个公告
    '''
    authentication_classes = []
    permission_classes = []

    # serializer_class = SelectFitSubSerializer

    def post(self, request, *args, **kwargs):
        serializer = SelectAnnounceSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])  # 获取用户
            announce = user.message.get(id=serializer.data['a_id'])

            if announce.set_time:
                # 通知
                now = datetime.now()
                a = CompareTime(now, announce.set_time)
                # 查询时间 大于设置的通知时间
                if a == 0:
                    announce.status = 2  # 消息状态设置成已读
                    announce.save()
            else:
                # 系统通知
                announce.status = 2  # 消息状态设置成已读
                announce.save()

            objJson = serialize("json", [announce])
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# 前台用户查询所有已发送的公告  最新的在上面
class SelectAllAnnounce(GenericAPIView):
    '''
    查询公告
    '''
    authentication_classes = []
    permission_classes = []

    # serializer_class = SelectFitSubSerializer

    def post(self, request, *args, **kwargs):
        serializer = SelectAllAnnounceSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])  # 获取用户
            announce = user.message.exclude(status=1).order_by('-datetime')  # 查询所有发送但未读和已读的信息
            if not announce:
                response_data = {'code': ["931"], 'message': "消息不存在"}
                return HttpResponse(json.dumps(response_data))

            objJson = serialize("json", announce)
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# 前台用户查询所有未到时消息通知  最新的在上面
class SelectPreMessage(GenericAPIView):
    '''
    查询公告
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = SelectAllAnnounceSerializer

    def post(self, request, *args, **kwargs):
        serializer = SelectAllAnnounceSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])  # 获取用户

            if not serializer.data['keyword']:
                announce = user.message.filter(status=1).order_by('-datetime')  # 查询所有发送但未读和已读的信息
            else:
                announce = user.message.filter(head__icontains=serializer.data['keyword'])
            if not announce:
                response_data = {'code': ["931"], 'message': "公告不存在"}
                return HttpResponse(json.dumps(response_data))
            objJson = serialize("json", announce)
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))

        return Response(serializer.errors)


response = {}


# 前台开启或者关闭定时任务
class AboutMessage(GenericAPIView):
    '''
    前台开启或者关闭定时任务
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AboutMessageSerializer

    def post(self, request, *args, **kwargs):
        serializer = AboutMessageSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])  # 获取用户
            announce = user.message.get(id=serializer.data['a_id'])
            option = serializer.data["option"]
            global response

            # 用户关闭提醒
            if option == 'False':
                # scheduler.remove_job(job_id=str(announce.id))
                # 因重启系统后，定时器关闭 采用每天定时方式修改开启关闭属性值
                announce.singnal = 0  # 关闭
                announce.save()
                response = {
                    'message': ['定时提醒已经关闭'],
                    'code': ["200"]
                }

            # 用户开启提醒
            if option == 'True':
                # 只给此员工创建定时任务
                # def func():
                #     announce.status = 3  # 信息设置成未读状态 1 未发送 2 已读 3 发送但未读
                #     announce.save()

                announce.singnal = 1  # 开启
                announce.save()

                # set_time = datetime.strptime(str(announce.set_time), '%Y-%m-%d %H:%M:%S')
                # # 定时任务
                #
                # print(str(announce.id))
                # scheduler.add_job(func, 'date',
                #                   run_date=datetime(set_time.year, set_time.month, set_time.day, set_time.hour,
                #                                     set_time.minute, ), id=str(announce.id))
                # # scheduler.start()
                response = {
                    'message': ['定时提醒已经开启'],
                    'code': ["200"]
                }

            return HttpResponse(json.dumps(response))
        return Response(serializer.errors)


# 超级管理员 管理员 运维查询所有公告
class ASelectAllAnnounce(GenericAPIView):
    '''
    查询公告
    '''
    authentication_classes = []
    permission_classes = []

    serializer_class = ASelectAllAnnounceSerializer

    def post(self, request, *args, **kwargs):
        serializer = ASelectAllAnnounceSerializer(data=request.data)
        if serializer.is_valid():
            # if serializer.data["number"]==0:
            if serializer.data['keyword']:
                announce = Announce.objects.filter(type=0).order_by('-datetime').filter(
                    head__icontains=serializer.data['keyword'])
            else:
                announce = Announce.objects.filter(type=0).order_by('-datetime')  # 查询所有发送但未读和已读的信息
            if not announce:
                response_data = {'code': ["931"], 'message': "公告不存在"}
                return HttpResponse(json.dumps(response_data))
            objJson = serialize("json", announce)
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)


# 普通用户删除单个公告
class DeleteAnnounce(GenericAPIView):
    '''
    删除公告
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DeleteAnnounceSerializer

    def post(self, request, *args, **kwargs):
        serializer = DeleteAnnounceSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])  # 获取用户
            announce = user.message.get(id=serializer.data['a_id'])
            if not announce:
                response_data = {'code': ["931"], 'message': "公告不存在"}
                return HttpResponse(json.dumps(response_data))
            announce.delete()
            response = {
                'message': ['公告删除成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


#
# # 完成前台用户删除自己到期的提醒  单个
# class FUserDeleteMessage(GenericAPIView):
#     '''
#     完成前台用户删除自己到期的提醒  单个
#     '''
#     authentication_classes = []
#     permission_classes = []
#     serializer_class = DeleteAnnounceSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = DeleteAnnounceSerializer(data=request.data)
#         if serializer.is_valid():
#             user = LoginUser.objects.filter(id=serializer['user_id'])  # 获取用户
#             announce = user.message.filter(id=serializer.data['a_id'])
#             announce.delete()
#             response = {
#                 'message': ['公告删除成功'],
#                 # 'token':token
#                 'code': ["200"]
#             }
#             return Response(response, status=200)
#         return Response(serializer.errors)


# 普通用户删除属于自己的所有公告
class DeleteAllAnnounce(GenericAPIView):
    '''
    删除所有公告
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DeleteAllAnnounceSerializer

    def post(self, request, *args, **kwargs):
        serializer = DeleteAllAnnounceSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.filter(id=serializer['user_id'])  # 获取用户
            user.message.clear()  # 找到与用户对应的消息公告 删除

            response = {
                'message': ['公告删除成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 普通用户一键已读所有未读公告
class ReadAllMessage(GenericAPIView):
    '''
    删除所有公告
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ReadAllMessageSerializer

    def post(self, request, *args, **kwargs):
        serializer = ReadAllMessageSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.filter(id=serializer['user_id'])  # 获取用户
            announces = user.message.objects.filter(status=3)  # 找到与用户对应的消息公告
            for i in announces:
                i.status = 2  # 把消息状态改为已读
            #   i.save()
            announces.save()  # 保存状态
            response = {
                'message': ['消息全部已读成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)



# 完成所有人更改自己发出的提醒公告
class EditMessage(GenericAPIView):
    '''
    完成所有人更改自己发出的提醒公告
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditMessageSerializer

    def post(self, request, *args, **kwargs):
        serializer = EditMessageSerializer(data=request.data)
        if serializer.is_valid():
            announce = Announce.objects.get(id=serializer.data['a_id'])
            announce.head = serializer.data['head']
            announce.content = serializer.data['a_content']
            if serializer.data['set_time']:
                announce.set_time = serializer.data['set_time']
            announce.save()
            response = {
                'message': ['信息修改成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 所有人根据不同传参 查询到时保养提醒 系统公告
class SelectMessageAlone(GenericAPIView):
    '''
    查询单个公告
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = SelectMessageAloneSerializer

    def post(self, request, *args, **kwargs):
        serializer = SelectMessageAloneSerializer(data=request.data)
        if serializer.is_valid():
            user = LoginUser.objects.get(id=serializer.data['user_id'])  # 获取用户
            # 0 系统通知 ，1 自定义消息通知
            if serializer.data['c_id'] == 0:
                announce = user.message.filter(type=0).exclude(status=1).order_by('-datetime')
            else:
                announce = user.message.filter(type=1).exclude(status=1).order_by('-datetime')
            if not announce:
                response_data = {'code': ["931"], 'message': "公告不存在"}
                return HttpResponse(json.dumps(response_data))
            objJson = serialize("json", announce)
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)
