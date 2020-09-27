import json
import random

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
# from .models import UserToken
from rest_framework_jwt.settings import api_settings
from conf.aliyun_api import AliYunSms
from .models import *
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


# from django.http import HttpResponse
# from captcha.views import CaptchaStore, captcha_image
# import base64


# 搜素功能
# 搜索所有激活状态公司
def companylist(request):
    companies = Company.objects.filter(active=1)
    for company in companies:
        print(company.company_name)
    return HttpResponse("sd")  # render (request, 'companylist.html', context=locals() )


# 搜索所有未激活状态公司
def unactivatedcompanylist(request):
    companies = Company.objects.filter(active=0)
    for company in companies:
        print(company.company_name)
    return HttpResponse("sd")

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
            companies = Company.objects.filter(active=0)
            a = []
            for company in companies:
                a.append(company.company_name)
                a.append(company.id)
            response = {
                'msg': ['查询成功'],
                'codes': [200],
                'company_name': a
            }
            return Response(response, status=200)
        return Response(serializer.errors)


#  查看所有激活状态用户
def userlist(request):
    users = LoginUser.objects.filter(is_active=1)
    for user in users:
        print(user.username)
    return HttpResponse("sd")  # render (request, 'companylist.html', context=locals() )


#  查看所有未激活状态用户
def unactivateduserlist(request):
    users = LoginUser.objects.filter(is_active=0)
    for user in users:
        print(user.username)
    return HttpResponse("sd")


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
    for project in projects:
        project.p_active = 0
        deldevice(project.id)
        project.save()
    return True


def deldevice(project_id):
    devices = Device.objects.filter(d_p_id=project_id)
    for device in devices:
        device.d_active = 0
        device.save()
    return True


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
                'msg': ['手机号格式正确，已发送验证码，注意查收'],
                'codes': [200],
            }
            phone = serializer.data['phone']
            response['phone'] = phone
            response['code'] = code

            cache.set(phone, code, 150)

            # # 发送短信验证
            # params = "{'code':%d}" % code
            # sms_obj = AliYunSms(phone, params)
            # res_obj = sms_obj.send()
            # print('发送结果：',res_obj)

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
                'msg': ['已发送验证码，注意查收'],
                'codes': [200],
            }
            phone = serializer.data['phone']
            response['phone'] = phone
            response['code'] = code

            cache.set(phone, code, 150)

            # # 发送短信验证
            # params = "{'code':%d}" % code
            # sms_obj = AliYunSms(phone, params)
            # res_obj = sms_obj.send()
            # print('发送结果：',res_obj)

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
            # password = serializer.data['password']
            user.phone_numbers = serializer.data['phone_numbers']
            # password = serializer.data['password']
            user.save()
            response = {
                'msg': ['用户注册成功'],
                'code': [200],
            }
            return Response(response)
        return Response(serializer.errors)


#  用户登录
class LoginView(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # user = LoginUser.objects.get(phone_numbers=serializer.data['ph'])

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
            loginuser = LoginUser.objects.get(id=user.id)
            user_id = loginuser.id
            response = {
                'msg': ['登录成功'],
                'code': [200],
                'user_id': [user_id],
                # 'token':token
                # 'loginuser': loginuser,
                # 'user_username': loginuser.username,
                # 'user_id': [loginuser.id],
            }
            return Response(response, status=200)
        return Response(serializer.errors, status=200)


#  不知道是要干嘛
class Order(APIView):
    def get(self, request):
        ret = {'code': 1000, 'msg': '成功GET进来了', 'data': None}
        ret['data'] = '欢迎使用本系统'
        return Response(ret)

    def post(self, request):
        order = OrderSerializer(data=request.data)
        if order.is_valid():
            print(order)
            ret = {'code': 1000, 'msg': '成功POST进来了', 'data': order.data}
            return Response(ret)
        return Response(order.errors, status=400)


# 修改个人信息
class Editmyprofile(APIView):
    '''
    修改个人信息
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditmyprofileSerializer,

    def get(self, request, *args, **kwargs):
        # serializer = MyprofileSerializer(data=request.data)
        # if serializer.is_valid():
        user_id = request.GET.get("user_id")
        print(user_id)
        # user = LoginUser.objects.get(id=serializer.data['user_id'])
        loginuser = LoginUser.objects.filter(id=user_id)
        if loginuser:
            user = LoginUser.objects.get(id=user_id)
            username = user.username
            userphone = user.phone_numbers
            usertype = user.u_type
            # usericon = user.u_icon
            usercompanyid = user.u_company_id

            response = {
                'msg': ['获取成功'],
                # 'token':token
                'code': [200],
                'userphone': [userphone],
                'usertype': [usertype],
                "icon_url": "/static/upload" + user.u_icon.url,
                # 'usericon': usericon,
                'usercompanyid': [usercompanyid],
            }

            return Response(response, status=200)
        response1 = {
            'msg': ['用户不存在'],
            # 'token':token
            'code': [404]
        }
        return Response(response1, status=200)
        # return Response(serializer.errors)
        # return HttpResponse("sd")

    def post(self, request, *args, **kwargs):
        serializer = EditmyprofileSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data['username']
            user_id = serializer.data['user_id']
            email = serializer.data['email']
            u_icon = request.FILES.get("u_icon")
            # u_icon = serializer.data['u_icon']
            print(u_icon)
            user = LoginUser.objects.get(id=serializer.data['user_id'])
            user.username = username
            user.id = user_id
            user.email = email
            user.u_icon = u_icon

            user.save()

            response = {
                'msg': ['用户信息修改成功'],
                'code': [200],

            }

            return Response(response, status=200)
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
                'msg': ['密码修改成功'],
                'code': [200]
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


# 查看个人信息
# class Myprofile(GenericAPIView):
#     authentication_classes = []
#     permission_classes = []
#     serializer_class = MyprofileSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = MyprofileSerializer(data=request.data)
#         if serializer.is_valid():
#             user = LoginUser.objects.get(id=serializer.data['id'])
#
#             username = user.username
#             userphone = user.phone_numbers
#             usertype = user.u_type
#             usericon = user.u_icon
#
#             company = Company.objects.get(c_u_id=serializer.data['id'])
#             companymid = company.c_u_id.id
#
#             response = {
#                 'msg': '获取成功',
#                 # 'token':token
#                 'code': 200,
#                 "username": username,
#                 "userphone": userphone,
#                 "usertype": usertype,
#                 "companyid": companymid,  # 不显示，拿来做空与非空判断
#                 "usericon": "/static/upload" + user.u_icon.url,
#             }
#
#             return Response(response, status=200)
#             # error = {
#             #     'msg': '尚未加入公司',
#             # }
#         return Response(serializer.errors)


# 公司CRUD
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
            company_name = request.POST.get("company_name")
            company_address = request.POST.get("company_address")
            context = request.POST.get("context")
            company_icon = request.FILES.get("company_icon")

            company = Company()
            # users = LoginUser()
            user = LoginUser.objects.get(id=user_id)
            company.c_u_id = user
            company.company_name = company_name
            company.company_address = company_address
            company.context = context
            company.company_icon = company_icon

            company.save()

            user.u_company_id = company.id  # 添加公司id到用户表
            user.u_type = "公司管理员"
            user.save()
            response = {
                'msg': ['公司创建成功，等待平台审核。'],
                # 'token':token
                'code': [200],
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
        print(company_id)
        company = Company.objects.get(id=company_id)

        companyname = company.company_name
        companyaddress = company.company_address
        companycontext = company.context
        companymid = company.c_u_id.id

        response = {
            'msg': ['获取成功'],
            # 'token':token
            'code': [200],
            # "companyname": companyname,
            # "companyaddress": companyaddress,
            # "companycontext": companycontext,
            # "companymanagerid": companymid,  # 不显示，拿来做判断
            # "icon_url": "/static/upload" + company.company_icon.url,
        }

        return Response(response, status=200)


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
        company = Company.objects.get(id=company_id)

        companyname = company.company_name
        companyaddress = company.company_address
        companycontext = company.context
        companymanagerid = company.c_u_id.id

        response = {
            'msg': ['获取成功'],
            # 'token':token
            'code': [200],
            "companyname": companyname,
            "companyaddress": companyaddress,
            "companycontext": companycontext,
            "companymanagerid": companymanagerid,  # 不显示，拿来做判断
            "icon_url": "/static/upload" + company.company_icon.url,
        }

        return Response(response, status=200)

    def post(self, request, *args, **kwargs):
        serializer = EditcompanySerializer(data=request.data)
        if serializer.is_valid():
            company_name = request.POST.get("company_name")
            company_address = request.POST.get("company_address")
            context = request.POST.get("context")
            company_icon = request.FILES.get("company_icon")

            company = Company.objects.get(id=serializer.data['company_id'])
            company.company_name = company_name
            company.company_address = company_address
            company.context = context
            company.company_icon = company_icon

            company.save()

            response = {
                'msg': ['公司信息修改成功'],
                'code': [200]
            }

            return Response(response, status=200)
        return Response(serializer.errors)


# 停用公司，公司管理员
class Deactivatecompany(GenericAPIView):
    '''
    停用公司，需要公司管理员身份或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = DeactivatecompanySerializer

    def post(self, request, *args, **kwargs):
        serializer = DeactivatecompanySerializer(data=request.data)
        if serializer.is_valid():
            company = Company.objects.get(id=serializer.data['company_id'])
            company.active = 0
            delprojects(serializer.data['company_id'])
            company.save()

            response = {
                'msg': ['公司及所有项目设备停用成功'],
                'code': [200]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


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
            user_id = request.POST.get("user_id")
            user = LoginUser.objects.get(id=user_id)
            user.u_company_id = request.POST.get("company_id")  # LoginUser is_staff 为0

            user.save()
            response = {
                'msg': ['已提交申请，等待公司管理员审核。'],
                'code': [200]
            }

            return Response(response, status=200)
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

            user.save()
            response = {
                'msg': ['添加成功'],
                'code': [200]
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
                    'msg': ['该用户不是员工'],
                    'code': [301]
                }
                return Response(response0, status=200)
            user.is_staff = 0  # 此时用户处于停用状态，但仍属于该公司

            user.save()
            response = {
                'msg': ['停用成功'],
                'code': [200]
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
            # user = LoginUser()
            users = LoginUser.objects.filter(u_company_id=serializer.data['company_id']).filter(is_staff=1)

            for user in users:
                print(user.username)
        return HttpResponse("sd")


#
# # 前端页面companylist.html可以通过Django方法
# # {% company in companies %}
# # {{company.company_name}} 等等
# # {% end for %}
# # 在前端页面展示数据
#


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
            p_u_id = request.POST.get("user_id")  # 获取创建人ID
            p_c_id = request.POST.get("company_id")

            project = Project()
            # users = LoginUser()
            user = LoginUser.objects.get(id=p_u_id)
            company = Company.objects.get(id=p_c_id)
            project.p_u_id = user
            project.p_c_id = company
            project.p_name = request.POST.get("p_name")
            project.p_description = request.POST.get("p_description")
            project.p_type = request.POST.get("p_type")
            project.p_customer_type = request.POST.get("p_customer_type")
            project.p_party_a = request.POST.get("p_party_a")
            project.p_purchase_time = request.POST.get("p_purchase_time")
            project.p_setup_time = request.POST.get("p_setup_time")
            project.p_built_time = request.POST.get("p_built_time")
            project.p_contact_name = request.POST.get("p_contact_name")
            project.p_contact_number = request.POST.get("p_contact_number")
            project.p_province = request.POST.get("p_province")
            project.p_city = request.POST.get("p_city")
            project.p_address = request.POST.get("p_address")
            project.p_longitude = request.POST.get("p_longitude")
            project.p_latitude = request.POST.get("p_latitude")

            project.save()

            response = {
                'msg': ['项目创建成功，等待平台审核。'],
                # 'token':token
                'code': [200],
            }
            return Response(response, status=200)
        return Response(serializer.errors)


def projectlist(request):
    '''
    查看项目列表
    '''
    company_id = request.GET.get("company_id")
    projects = Project.objects.filter(p_c_id=company_id)
    for project in projects:
        print(project.p_name)
    return HttpResponse("sd")


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
            project_id = request.POST.get("project_id")
            project = Project.objects.get(id=project_id)

            p_name = project.p_name

            response = {
                'msg': ['获取成功'],
                # 'token':token
                'code': [200]

            }

            return Response(response, 200)
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
            project_id = request.POST.get("project_id")
            p_name = request.POST.get("p_name")
            project = Project.objects.get(id=project_id)

            project.p_name = p_name
            project.save()

            response = {
                'msg': ['修改成功'],
                # 'token':token
                'code': [200],

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
    serializer_class = EditprojectSerializer

    def post(self, request, *args, **kwargs):
        serializer = EditprojectSerializer(data=request.data)
        if serializer.is_valid():
            project = Project.objects.get(id=serializer.data['project_id'])
            project.p_active = 0
            deldevice(project.id)
            project.save()

            response = {
                'msg': ['项目及其设备停用成功'],
                # 'token':token
                'code': [200],
            }

            return Response(response, 200)
        return Response(serializer.errors)


# 在项目中添加设备，需公司管理员操作
class Applydevice(GenericAPIView):
    '''
    在项目中添加设备，需公司管理员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ApplydeviceSerializer

    def post(self, request, *args, **kwargs):
        serializer = ApplydeviceSerializer(data=request.data)
        if serializer.is_valid():
            d_m_id = request.POST.get("user_id")  # 获取创建人ID
            d_p_id = request.POST.get("project_id")

            device = Device()
            user = LoginUser.objects.get(id=d_m_id)
            company = Project.objects.get(id=d_p_id)
            device.d_m_id = user
            device.d_p_id = company
            device.d_name = request.POST.get("d_name")
            device.d_series_number = request.POST.get("d_series_number")
            device.d_tunnel = request.POST.get("d_tunnel")
            device.d_status = request.POST.get("d_status")
            device.d_data_status = request.POST.get("d_data_status")
            device.d_last_contract_time = request.POST.get("d_last_contract_time")
            device.d_register_time = datetime.datetime.now()

            device.save()

            response = {
                'msg': ['设备创建成功，等待平台审核。'],
                # 'token':token
                'code': [200],
            }
            return Response(response, status=200)
        return Response(serializer.errors)


#
class Editdevice(GenericAPIView):
    '''
    get查看&&post修改设备信息,需要公司管理员或设备负责人操作或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditdeviceSerializer

    def get(self, request, *args, **kwargs):
        serializer = EditdeviceSerializer(data=request.data)
        if serializer.is_valid():
            device = Device.objects.get(id=serializer.data['device_id'])
            response = {
                'msg': ['设备查询成功'],
                # 'token':token
                'code': [200]
                # '设备名': device.d_name,
            }
            return Response(response, status=200)
        return Response(serializer.errors)

    def post(self, request, *args, **kwargs):
        serializer = EditdeviceSerializer(data=request.data)
        if serializer.is_valid():
            device = Device.objects.get(id=serializer.data['device_id'])
            device.d_name = request.POST.get("d_name")
            device.d_tunnel = request.POST.get("d_tunnel")
            device.save()

            response = {
                'msg': ['修改成功'],
                # 'token':token
                'code': [200]
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

    def get(self, request, *args, **kwargs):
        serializer = DevicelistSerializer(data=request.data)
        if serializer.is_valid():
            devices = Device.objects.filter(d_p_id=serializer.data['project_id']).filter(d_active=1)
            response = {
                'msg': ['获取成功'],
                # 'token':token
                'code': [200]
            }
            return Response(response, status=200)  # return render  locals()
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
                'msg': ['关联成功'],
                # 'token':token
                'code': [200]
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
                'msg': ['取消关联成功'],
                # 'token':token
                'code': [200]
            }
            return Response(response, status=200)
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
                'msg': ['数据添加成功'],
                # 'token':token
                'code': [200]
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
    serializer_class = SigndeviceSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = SigndeviceSerializer(data=request.data)
        if serializer.is_valid():
            alldata = Data.objects.filter(d_d_id=serializer.data['device_id'])
            # for data in alldata:
            #     print(data.d_name)
            response = {
                'msg': ['获取成功'],
                # 'token':token
                'code': [200]
            }
            return Response(response, status=200)  # return render  locals()
        return Response(serializer.errors)


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
            data.delete()
            response = {
                'msg': ['数据删除成功'],
                # 'token':token
                'code': [200]
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
    serializer_class = AlertSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = AlertSerializer(data=request.data)
        if serializer.is_valid():
            alert = Alert()
            # d_d_id = serializer.data['device_id']
            alert.a_data_id = Data.objects.get(id=serializer.data['data_id'])
            # alert.a_data_id = request.POST.get('data_id')
            alert.a_highest_line = request.POST.get('a_highest_line')
            alert.a_highest_level = request.POST.get('a_highest_level')
            alert.a_highest_tip = request.POST.get('a_highest_tip')
            alert.a_high_line = request.POST.get('a_high_line')
            alert.a_high_level = request.POST.get('a_high_level')
            alert.a_high_tip = request.POST.get('a_high_tip')
            alert.a_low_line = request.POST.get('a_low_line')
            alert.a_low_level = request.POST.get('a_low_level')
            alert.a_low_tip = request.POST.get('a_low_tip')
            alert.a_lowest_line = request.POST.get('a_lowest_line')
            alert.a_lowest_level = request.POST.get('a_lowest_level')
            alert.a_lowest_tip = request.POST.get('a_lowest_tip')
            alert.save()
            response = {
                'msg': ['数据告警规则添加成功'],
                # 'token':token
                'code': [200]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


# 查询数据告警规则
class Viewalert(GenericAPIView):
    '''
    查询数据告警规则,需要用户为公司管理人员或设备负责人或后台人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = AlertSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = AlertSerializer(data=request.data)
        if serializer.is_valid():
            alert = Alert.objects.get(id=serializer.data['alert_id'])

            response = {
                'msg': ['查询成功'],
                'code': [200]
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

    def post(self, request, *args, **kwargs):
        serializer = AlertSerializer(data=request.data)
        if serializer.is_valid():
            alert = Alert.objects.get(id=serializer.data['alert_id'])
            alert.a_highest_line = request.POST.get('a_highest_line')
            alert.a_highest_level = request.POST.get('a_highest_level')
            alert.a_highest_tip = request.POST.get('a_highest_tip')
            alert.a_high_line = request.POST.get('a_high_line')
            alert.a_high_level = request.POST.get('a_high_level')
            alert.a_high_tip = request.POST.get('a_high_tip')
            alert.a_low_line = request.POST.get('a_low_line')
            alert.a_low_level = request.POST.get('a_low_level')
            alert.a_low_tip = request.POST.get('a_low_tip')
            alert.a_lowest_line = request.POST.get('a_lowest_line')
            alert.a_lowest_level = request.POST.get('a_lowest_level')
            alert.a_lowest_tip = request.POST.get('a_lowest_tip')
            alert.save()
            response = {
                'msg': ['数据告警规则修改成功'],
                # 'token':token
                'code': [200]
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
            alert.delete()
            response = {
                'msg': ['告警规则删除成功'],
                # 'token':token
                'code': [200]
            }
            return Response(response, status=200)
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
                'msg': ['公司通过审核'],
                # 'token':token
                'code': [200]
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
                'msg': ['查询成功'],
                # 'token':token
                'code': [200]
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
                'msg': ['设备激活成功'],
                # 'token':token
                'code': [200]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


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
            worksheet.w_status = serializer.data['w_status']
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
                'msg': ['工单创建成功'],
                # 'token':token
                'code': [200]
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
            worksheets = Worksheet.objects.all()
            for worksheet in worksheets:
                print(worksheet.w_name)
            return HttpResponse("sd")
        return Response(serializer.errors)


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
                'msg': ['用户不存在或已停用'],
                # 'token':token
                'code': [999]
            }
            return Response(response, status=200)
        if not LoginUser.objects.filter(id=user_id).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
            response1 = {
                'msg': ['您无权进行此操作'],
                # 'token':token
                'code': [996]
            }
            return Response(response1, status=200)
        worksheets = Worksheet.objects.filter(w_e_id=user_id)
        for worksheet in worksheets:
            print(worksheet.w_name)
        response2 = {
            'msg': ['查询工单成功'],
            # 'token':token
            'code': [200],

        }
        return Response(response2, status=200)


class Searchworksheets(GenericAPIView):
    '''
    搜索工单（根据名称、时间段）,需后台工作人员身份
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = []

    def get(self, request, *args, **kwargs):
        name = request.GET.get('w_name')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        worksheets = Worksheet.objects.filter(w_name=name).filter(w_time__gt=start_time).filter(w_time__lt=end_time)
        for worksheet in worksheets:
            name = worksheet.w_name
        for worksheet in worksheets:
            timess = worksheet.w_time

        response = {
            'msg': ['查询工单成功'],
            # 'token':token
            'code': [200],
            'name': [name],
            'time': [timess],

        }
        return Response(response, status=200)




# class Editworksheet(GenericAPIView):
#     authentication_classes = []
#     permission_classes = []
#     serializer_class = EditworksheetSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = EditworksheetSerializer(data=request.data)
#         if serializer.is_valid():

# 删除工单
# class Deleteworksheet(GenericAPIView):
#     '''
#     删除工单,需后台工作人员身份
#     '''
#     authentication_classes = []
#     permission_classes = []
#     serializer_class = DeleteworksheetSerializer  # 权限判断相同
#
#     def post(self, request, *args, **kwargs):
#         serializer = DeleteworksheetSerializer(data=request.data)
#         if serializer.is_valid():