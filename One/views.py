import json
import random
from datetime import timedelta

from django.core import serializers
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.contrib.sessions import serializers
from aliyunsdkcore.http.format_type import JSON
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from conf.aliyun_api import AliYunSms
from .models import *
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


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
            response = {
                'message': ['用户注册成功'],
                'code': ["200"]
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

            response_data = {'code': ["200"], 'data': objStr, 'companyname': companyname}
            response = HttpResponse(json.dumps(response_data))
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


#  不知道是要干嘛
class Order(APIView):
    def get(self, request):
        ret = {'code': 1000, 'message': '成功GET进来了', 'data': None}
        ret['data'] = '欢迎使用本系统'
        return Response(ret)

    def post(self, request):
        order = OrderSerializer(data=request.data)
        if order.is_valid():
            print(order)
            ret = {'code': 1000, 'message': '成功POST进来了', 'data': order.data}
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
        user_id = request.GET.get("user_id")
        print(user_id)
        # user = LoginUser.objects.get(id=serializer.data['user_id'])
        loginuser = LoginUser.objects.filter(id=user_id)
        if loginuser:
            objJson = serialize("json", LoginUser.objects.filter(id=user_id))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
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
            user_id = serializer.data["user_id"]  # 获取创建1人ID
            company_name = serializer.data['company_name']
            company_address = serializer.data['company_address']
            context = serializer.data['context']
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
            company_name = serializer.data['company_name']
            company_address = serializer.data['company_address']
            context = serializer.data['context']
            company_icon = request.FILES.get("company_icon")

            company = Company.objects.get(id=serializer.data['company_id'])
            company.company_name = company_name
            company.company_address = company_address
            company.context = context
            if company_icon:
                company.company_icon = company_icon

            company.save()

            response = {
                'message': ['公司信息修改成功'],
                'code': ["200"]
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
                                    LoginUser.objects.filter(u_company_id=serializer.data['company_id']).filter(is_staff=1))
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
            user = LoginUser()  # 创建员工对象
            user.is_staff = 1
            #            user.id = serializer.data['staff_id']
            user.phone_numbers = serializer.data['staff_phone']
            user.username = serializer.data['staff_name']
            password = serializer.data['staff_password']
            user.password = make_password(password)
            user.u_company_id = manager.u_company_id
            user.save()
            response = {
                'message': ['添加员工成功'],
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
            project.p_type = serializer.data['p_type']
            project.p_customer_type = serializer.data['p_customer_type']
            project.p_party_a = serializer.data['p_party_a']
            project.p_purchase_time = serializer.data['p_purchase_time']
            project.p_setup_time = serializer.data['p_setup_time']
            project.p_built_time = serializer.data['p_built_time']
            project.p_contact_name = serializer.data['p_contact_name']
            project.p_contact_number = serializer.data['p_contact_number']
            project.p_province = serializer.data['p_province']
            project.p_city = serializer.data['p_city']
            project.p_address = serializer.data['p_address']
            project.p_dashboard = serializer.data['p_dashboard']
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
        user_type = user.u_type
        u_type = ['运维', '公司管理员', '客服', '运营', '超级管理员']
        if user.u_type in u_type:
            objJson = serialize("json", Project.objects.filter(p_c_id=company_id).filter(p_active=1))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        if LoginUser.objects.filter(id=user_id).filter(is_active=1):
            objJson = serialize("json", user.project.all())
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
            objJson = serialize("json", Project.objects.filter(id=project_id))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
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
            project.p_type = serializer.data['p_type']
            project.p_customer_type = serializer.data['p_customer_type']
            project.p_party_a = serializer.data['p_party_a']
            project.p_purchase_time = serializer.data['p_purchase_time']
            project.p_setup_time = serializer.data['p_setup_time']
            project.p_built_time = serializer.data['p_built_time']
            project.p_contact_name = serializer.data['p_contact_name']
            project.p_contact_number = serializer.data['p_contact_number']
            project.p_province = serializer.data['p_province']
            project.p_city = serializer.data['p_city']
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
                        Q(u_type='公司管理员') | Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                    user.u_type = '设备管理员'
                    user.save()
                user.save()
                response = {
                    'message': ['关联成功。'],
                    # 'token':token
                    'code': ["200"]
                }
                return Response(response, status=200)
            collectdevice = Collectdevice.objects.get(cd_p_id_id=project.id)
            user.collectdevice.add(Collectdevice.objects.get(id=collectdevice.id))
            if not LoginUser.objects.filter(id=user_id).filter(
                    Q(u_type='公司管理员') | Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
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
            # 设备管理员 员工
            u_type = ['员工', '公司管理员', '设备管理员']

            if user.u_type in u_type:
                objJson = serialize("json", project.loginuser_set.filter(u_type='设备管理员'))
                objStr = json.loads(objJson)
                response_data = {'code': ["200"], 'data': objStr}
                return HttpResponse(json.dumps(response_data))
            objJson = serialize("json", project.loginuser_set.filter(Q(u_type='运维') | Q(u_type='运营') | Q(u_type='客服')))
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
                            Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员') | Q(u_type='公司管理员')):
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
                        Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员') | Q(u_type='公司管理员')):
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

            print(collectdevices)
            url = 'https://portal-apm-user1-eks004.hz.wise-paas.com.cn/api-apm/topo/node?nodeIds='

            for collectdevice in collectdevices:
                nodeid = collectdevice.cd_nodeid
                nodeid = str(nodeid)
                url = url + nodeid + ','
            url = url[:-1]
            # print(url)
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
            cd_p_id = serializer.data['project_id']
            cd_c_id = serializer.data['company_id']
            print(cd_c_id)
            device = Collectdevice()
            user = LoginUser.objects.get(id=d_m_id)
            project = Project.objects.get(id=cd_p_id)
            company = Company.objects.get(id=cd_c_id)
            device.cd_p_id = project
            device.cd_m_id = user
            device.cd_c_id = company
            device.cd_nodeid = serializer.data['cd_nodeid']
            device.cd_name = serializer.data['cd_name']
            device.cd_produce_time = serializer.data['cd_produce_time']
            device.cd_manufacturer = serializer.data['cd_manufacturer']

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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                response = {
                    'message': ['您无权进行此操作'],
                    # 'token':token
                    'code': ["996"]
                }
                return Response(response, status=200)
        devices = Collectdevice.objects.filter(cd_p_id_id=project_id)

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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                response = {
                    'message': ['您无权进行此操作'],
                    # 'token':token
                    'code': ["996"]
                }
                return Response(response, status=200)

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
        collectdevice_id = request.GET.get("collectdevice_id")

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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
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

            device.cd_nodeid = serializer.data['cd_nodeid']
            device.cd_name = serializer.data['cd_name']
            device.cd_produce_time = serializer.data['cd_produce_time']
            device.cd_manufacturer = serializer.data['cd_manufacturer']

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
        collectdevice_id = request.GET.get("collectdevice_id")

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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                response = {
                    'message': ['您无权进行此操作'],
                    # 'token':token
                    'code': ["996"]
                }
                return Response(response, status=200)
        objJson = serialize("json", Cdevicedata.objects.filter(cdd_c_id_id=collectdevice_id))
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
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


class Delcollectdeviceatt(GenericAPIView):
    '''
    删除采集设备属性，需公司管理员或运维人员操作
    '''
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
    '''
    在项目中添加设备，需公司管理员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = ApplydeviceSerializer

    def post(self, request, *args, **kwargs):
        serializer = ApplydeviceSerializer(data=request.data)
        if serializer.is_valid():
            d_m_id = serializer.data["user_id"]  # 获取创建人ID
            d_p_id = serializer.data["project_id"]

            device = Device()
            user = LoginUser.objects.get(id=d_m_id)
            company = Project.objects.get(id=d_p_id)
            device.d_m_id = user
            device.d_p_id = company
            device.d_name = serializer.data["d_name"]
            device.d_series_number = serializer.data["d_series_number"]
            device.d_tunnel = serializer.data["d_tunnel"]
            device.d_status = serializer.data["d_status"]
            device.d_data_status = serializer.data["d_data_status"]
            device.d_last_contract_time = serializer.data["d_last_contract_time"]
            device.d_register_time = datetime.datetime.now()

            device.save()

            response = {
                'message': ['设备创建成功，等待平台审核.'],
                # 'token':token
                'code': ["200"]
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
            device_id = request.GET.get('device_id')
            objJson = serialize("json", Device.objects.filter(id=serializer.data['device_id']))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
        return Response(serializer.errors)

    def post(self, request, *args, **kwargs):
        serializer = EditdeviceSerializer(data=request.data)
        if serializer.is_valid():
            device = Device.objects.get(id=serializer.data['device_id'])
            device.d_name = serializer.data['d_name']
            device.d_tunnel = serializer.data['d_tunnel']
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

    def get(self, request, *args, **kwargs):
        serializer = DevicelistSerializer(data=request.data)
        if serializer.is_valid():
            objJson = serialize("json", Device.objects.filter(d_p_id=serializer.data['project_id']).filter(d_active=1))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
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


# 添加机械设备属性，需公司管理员操作
class Adddeviceatt(GenericAPIView):
    """添加机械设备属性"""
    authentication_classes = []
    permission_classes = []
    serializer_class = AdddeviceattSerializer  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = AdddeviceattSerializer(data=request.data)
        if serializer.is_valid():
            device_data = Devicedata()
            device_data.ddd_d_id = Device.objects.get(id=serializer.data['device_id'])
            device_data.ddd_name = serializer.data['device_attribute']
            device_data.ddd_data = serializer.data['device_data']
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
            device_data.ddd_data = serializer.data['device_data']
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
            device_data = Devicedata.objects.filter(ddd_name=serializer.data['device_attribute'])
            device_data.delete()
            response = {
                'message': ['删除机械设备属性成功'],
                'code': ["200"]
            }
            return Response(response)
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
    serializer_class = SigndeviceSerializer  # 权限判断相同

    def post(self, request, *args, **kwargs):
        serializer = SigndeviceSerializer(data=request.data)
        if serializer.is_valid():
            objJson = serialize("json", Data.objects.filter(d_d_id=serializer.data['device_id']))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
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
                'message': ['数据告警规则添加成功'],
                # 'token':token
                'code': ["200"]
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
            # alert = Alert.objects.get(id=serializer.data['alert_id'])
            objJson = serialize("json", Alert.objects.get(id=serializer.data['alert_id']))
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
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
            alert.delete()
            response = {
                'message': ['告警规则删除成功'],
                # 'token':token
                'code': ["200"]
            }
            return Response(response, status=200)
        return Response(serializer.errors)


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
                'msg': ['创建投诉记录成功'],
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
                'msg': ['删除投诉记录成功'],
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
                'msg': ['投诉状态修改成功'],
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
            maintainrecord.dm_d_id = Device.objects.get(id=serializer.data['dm_d_id'])
            maintainrecord.dm_o_id = LoginUser.objects.get(id=serializer.data['user_id'])
            maintainrecord.dmo_name = maintainrecord.dm_o_id.username
            maintainrecord.dm_d_detail = serializer.data['dm_d_detail']
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

        paginator = Paginator(records, per_page)
        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)
        response_data = {'code': '200', 'data': objStr, 'max_page': total_page, 'datacount': total_data}

        return HttpResponse(json.dumps(response_data))


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
            record = Devicemaintainrecord.objects.get(id=serializer.data['id'])
            objJson = serialize("json", record)
            objStr = json.loads(objJson)
            response_data = {'code': '200', 'data': objStr}
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
            files = request.FILES.getlist('image')
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
            objJson = serialize("json", Worksheet.objects.all())
            objStr = json.loads(objJson)
            response_data = {'code': ["200"], 'data': objStr}
            return HttpResponse(json.dumps(response_data))
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
                'message': ['用户不存在或已停用'],
                # 'token':token
                'code': ["999"]
            }
            return Response(response, status=200)
        if not LoginUser.objects.filter(id=user_id).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            response1 = {
                'message': ['您无权进行此操作'],
                # 'token':token
                'code': ["996"]
            }
            return Response(response1, status=200)

        objJson = serialize("json", Worksheet.objects.filter(w_e_id=user_id))
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
            worksheet.w_name = serializer.data['w_name']
            worksheet.w_type = serializer.data['w_type']
            worksheet.w_content = serializer.data['w_content']
            worksheet.w_status = serializer.data['w_status']
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
            knowledge.k_tag = serializer.data['k_tag']

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
                'message': ['创建成功'],
                # 'token':token
                'code': ["200"]
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

        enterprises = Enterprise.objects.all()
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
        knowledgemediastore.m_k_ip = 'http://47.104.81.202:8002/static/upload/'
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

        knowledges = Knowledge.objects.filter(k_type=type)
        paginator = Paginator(knowledges, per_page)

        total_page = paginator.num_pages
        total_data = paginator.count

        page_object = paginator.page(page)
        objJson = serialize("json", page_object)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr, 'totalpage': total_page, 'datacount': total_data}

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

        knowledges = Knowledge.objects.filter(k_type=type)
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
        page = int(request.GET.get("page"))  # 第几页
        per_page = int(request.GET.get("per_page", 10))  # 每页多少条

        knowledges = Knowledge.objects.filter(k_type=type).filter(k_tag=tag)
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
        knowledges = Knowledge.objects.filter(k_type=type).order_by('-k_date')[:5]
        objJson = serialize("json", knowledges)
        objStr = json.loads(objJson)

        response_data = {'code': ["200"], 'data': objStr}

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
        knowledge = Knowledge.objects.filter(id=k_id)
        if not knowledge:
            response0 = {
                'message': ['数据不存在'],
                'code': ["988"]
            }
            return Response(response0, status=200)
        objJson = serialize("json", Knowledge.objects.filter(id=k_id))
        objStr = json.loads(objJson)
        objJson1 = serialize("json", Solution.objects.filter(s_k_id_id=k_id))
        objStr1 = json.loads(objJson1)
        response_data = {'code': ["200"], 'knowledge': objStr, 'solution': objStr1}
        return HttpResponse(json.dumps(response_data))


class Editknowledge(GenericAPIView):
    '''
    查询知识库/行业资讯详情&&编辑知识库/行业资讯, 编辑功能post需后台人员身份  GET功能需传值知识库/行业资讯id： k_id
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = EditknowledgeSerializer()  # 权限相同

    def get(self, request, *args, **kwargs):
        k_id = request.GET.get('k_id')
        knowledge = Knowledge.objects.filter(id=k_id)
        if not knowledge:
            response0 = {
                'message': ['数据不存在'],
                'code': ["988"]
            }
            return Response(response0, status=200)
        objJson = serialize("json", Knowledge.objects.filter(id=k_id))
        objStr = json.loads(objJson)
        response_data = {'code': ["200"], 'data': objStr}
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
            knowledge.k_tag = serializer.data['k_tag']
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
            k.k_status = 1
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
            k.k_status = 0
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
                                LoginUser.objects.filter(Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')).filter(
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



def login1(request):
    return render(request, 'post.html')


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
    '''
    查看当前研华token，需要登录后操作
    '''
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


class Editwisepasstoken(GenericAPIView):
    '''
    更新研华token，需要后台人员操作
    '''
    authentication_classes = []
    permission_classes = []
    serializer_class = WisepasstokenSerializerV2  # 权限要求相同

    def post(self, request, *args, **kwargs):
        serializer = WisepasstokenSerializerV2(data=request.data)
        if serializer.is_valid():
            w = WisePassToken.objects.get(id=1)
            w.token = serializer.data['token']
            w.save()
            response = {
                'code': ['200'],
                'message': ['更新成功']
            }
        return Response(serializer.errors)