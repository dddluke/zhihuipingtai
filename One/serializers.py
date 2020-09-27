import re
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.validators import UniqueValidator

from .models import LoginUser, Company, Device, Project, Data, Alert, Worksheet
from django.core.cache import cache
from django.db.models import Q
from django.http import Http404


# from rest_framework_jwt.settings import api_settings
# from captcha.views import CaptchaStore, captcha_image
class MyException(Exception):
    def __init__(self, code, error, data):
        self.code = code
        self.error = error
        self.data = data


def re_phone(phonenumber):
    ret = re.match(r"^1[1-8]\d{9}$", phonenumber)
    if ret:
        return True
    return False


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def re_email(phone):
    ret = re.match(r"\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*", phone)
    if ret:
        return True
    return False


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


class UnactivatedcompanylistSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('user_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs



class SmsSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('phone',)

    def validate_phone(self, phone):
        '''
        手机号验证
        :return:
        '''

        if LoginUser.objects.filter(phone_numbers=phone).count():
            raise ValidationError(detail={'code': 982, 'message': '手机号已注册'})

        if not re_phone(phone):
            raise ValidationError(detail={'code': 983, 'message': '手机号码格式错误'})
        return phone


class SmsvalidSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('phone',)

    def validate_phone(self, phone):
        '''
        手机号验证
        :return:
        '''

        if not LoginUser.objects.filter(phone_numbers=phone):
            raise ValidationError(detail={'code': 981, 'message': '手机号码未注册'})

        if not re_phone(phone):
            raise ValidationError(detail={'code': 983, 'message': '手机号码格式错误'})
        return phone


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    phone_numbers = serializers.CharField(required=True)
    pwd2 = serializers.CharField(max_length=256, min_length=4, write_only=True)
    code = serializers.CharField(required=True)

    # password = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('username', 'password', 'pwd2', 'phone_numbers', 'code')

    def validate(self, attrs):
        # print(attrs['code'])
        if LoginUser.objects.filter(phone_numbers=attrs['phone_numbers']):
            raise ValidationError(detail={'code': 982, 'message': '手机号已注册'})
        if LoginUser.objects.filter(username=attrs['username']):
            raise ValidationError(detail={'code': 980, 'message': '用户名已注册'})
        if not re_phone(attrs['phone_numbers']):
            raise ValidationError(detail={'code': 983, 'message': '手机号码格式错误'})
        # 'username', 'password'是系统用户表中已经存在的，系统会自动对用户输入的username进行检查
        sms_code = cache.get(attrs['phone_numbers'])
        # print(sms_code)
        # print('从redis取出的code:' sms_code)
        if str(sms_code) != attrs['code']:
            raise ValidationError(detail={'code': 979, 'message': '验证码错误或过期'})
        if attrs['pwd2'] != attrs['password']:
            raise ValidationError(detail={'code': 978, 'message': '两次密码输入不一致'})
        # del attrs['pwd2']
        # del attrs['code']
        # attrs['password'] = make_password(attrs['password'])
        return attrs


class LoginSerializer(serializers.ModelSerializer):
    ph = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('ph', 'password')

    def validate(self, attrs):
        # Q(username=attrs['ph']) | Q(phone=attrs['ph']) | Q(email=attrs['ph'])
        # print(attrs['password'])
        user = LoginUser.objects.filter(
            Q(username=attrs['ph']) | Q(phone_numbers=attrs['ph']) | Q(email=attrs['ph'])).first()
        # print(user)
        if not user:
            raise ValidationError(detail={'code': 977, 'message': '用户名输入有误'})
        user = LoginUser.objects.get(
            Q(username=attrs['ph']) | Q(phone_numbers=attrs['ph']) | Q(email=attrs['ph']))
        password = attrs['password']
        # print(password)
        # print(user.password)
        if not check_password(password, user.password):
            raise ValidationError(detail={'code': 976, 'message': '密码不正确'})
        # if not user.check_password(attrs['password']):
        #     raise ValidationError(detail={'code': 976, 'message': '密码不正确'})
        return attrs


class OrderSerializer(serializers.Serializer):
    title = serializers.CharField()
    name = serializers.CharField()


#
# 查看用户个人信息
class MyprofileSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = LoginUser
        fields = ('user_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        return attrs


class EditmyprofileSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    username = serializers.CharField(required=False)
    phonenumber = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    u_icon = serializers.FileField(required=False)

    class Meta:
        model = LoginUser
        fields = ('username', 'phonenumber', 'u_icon')

    def validate(self, attrs):
        # if LoginUser.objects.filter(phone_numbers=attrs['phonenumber']).count():
        #     raise ValidationError('手机号码已经注册')
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        user.username = "sdadasdasdasdasd"

        user.save()
        if LoginUser.objects.filter(username=attrs['username']).count():
            raise ValidationError(detail={'code': 980, 'message': '用户名已经注册'})

        # if LoginUser.objects.filter(username=attrs['username']).count():
        #     raise ValidationError(detail={'code': 980, 'message': '用户名已经注册'})

        # if LoginUser.objects.filter(email=attrs['email']).count():
        #     raise ValidationError('邮箱已经注册')
        # if not attrs['phonenumber']:
        #     raise ValidationError(detail={'code': 972, 'message': '用户名已经注册'})
        # if not re_phone(attrs['phonenumber']):
        #     raise ValidationError(detail={'code': 983, 'message': '手机号码格式错误'})

        return attrs


class ChangepasswordSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='用户id')
    phone_numbers = serializers.CharField(required=True, help_text='用户验证手机号')
    password = serializers.CharField(max_length=256, min_length=4, help_text='用户旧密码')
    newpassword = serializers.CharField(max_length=256, min_length=4, help_text='用户新密码')
    pwd2 = serializers.CharField(max_length=256, min_length=4, help_text='用户重复输入密码')
    code = serializers.CharField(required=True, help_text='手机验证码')

    # password = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('user_id', 'phone_numbers', 'password', 'newpassword', 'pwd2', 'code')

    def validate(self, attrs):
        # print(attrs['password'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        if user.phone_numbers != attrs['phone_numbers']:
            raise ValidationError(detail={'code': 975, 'message': '手机号输入错误，请检查'})
        sms_code = cache.get(attrs['phone_numbers'])
        # print(sms_code)
        if str(sms_code) != attrs['code']:
            raise ValidationError(detail={'code': 979, 'message': '验证码错误或过期'})
        if attrs['pwd2'] != attrs['newpassword']:
            raise ValidationError(detail={'code': 978, 'message': '两次密码输入不一致'})
        oldpassword = attrs['password']
        print(oldpassword)
        if not check_password(oldpassword, user.password):
            raise ValidationError(detail={'code': 976, 'message': '密码不正确'})
        # del attrs['pwd2']
        # del attrs['code']
        # attrs['password'] = make_password(attrs['password'])
        return attrs


class CreatecompanySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    company_name = serializers.CharField(required=True)
    company_address = serializers.CharField(required=True)
    context = serializers.CharField(required=False)
    company_icon = serializers.FileField(required=True)

    class Meta:
        model = Company
        fields = ('user_id', 'company_name', 'company_address', 'context', 'company_icon')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if Company.objects.filter(company_name=attrs['company_name']):
            # raise ValidationError('公司名已注册')
            raise ValidationError(detail={'code': 974, 'message': '公司名已注册'})

        if Company.objects.filter(c_u_id_id=attrs['user_id']):
            raise ValidationError(detail={'code': 973, 'message': '每个用户只能创建一个公司'})
        return attrs


class EditcompanySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    company_id = serializers.IntegerField(required=True)
    company_name = serializers.CharField(required=True)
    company_address = serializers.CharField(required=True)
    context = serializers.CharField(required=False)
    company_icon = serializers.FileField(required=False)

    class Meta:
        model = Company
        fields = ('user_id', 'company_id', 'company_name', 'company_address', 'context', 'company_icon')

    def validate(self, attrs):
        # flag = 1
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not Company.objects.filter(c_u_id=attrs['user_id']):
            raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        return attrs


class DeactivatecompanySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    company_id = serializers.IntegerField(required=True)

    class Meta:
        model = Company
        fields = ('user_id', 'company_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not Company.objects.filter(c_u_id=attrs['user_id']):
            raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']).filter(
                u_type='公司管理员'):  # 如果用户不是公司管理员，需要他拥有后台人员身份
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class JoincompanySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    company_id = serializers.IntegerField(required=True)

    class Meta:
        model = Company
        fields = ('user_id', 'company_id')

    def validate(self, attrs):

        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        return attrs


class EnrollstaffSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    user_id1 = serializers.IntegerField(required=True, help_text='操作人id')  # 操作人id

    class Meta:
        model = LoginUser
        fields = ('user_id', 'user_id1')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id1']).filter(u_company_id=attrs['company_id']).filter(
                u_type='公司管理员'):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class DeactivatestaffSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='被删除员工id')  # 被删除员工id
    user_id1 = serializers.IntegerField(required=True, help_text='操作人id')  # 操作人id
    company_id = serializers.IntegerField(required=True, help_text='公司id')  # 操作公司id，需要在用户列表页面中

    class Meta:
        model = LoginUser
        fields = ('user_id', 'user_id1', 'company_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id1']).filter(is_active=1):
            raise ValidationError(detail={'code': 990, 'message': '您的账号不存在或已被停用'})
        if not LoginUser.objects.filter(id=attrs['user_id1']).filter(u_company_id=attrs['company_id']).filter(
                u_type='公司管理员'):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']):
            raise ValidationError(detail={'code': 989, 'message': '用户不属于公司，无权操作'})
        return attrs


# class CompanyprofileSerializer(serializers.ModelSerializer):
#     id = serializers.CharField(required=True)
#
#     class Meta:
#         model = Company
#         fields = ('id',)
#
#     def validate(self, attrs):
#         if not Company.objects.get(id=attrs['id']).filter(active=1):
#             print(attrs['id'])
#             raise ValidationError('公司不存在或已被平台停用')
#         return attrs


# class MycompanyprofileSerializer(serializers.ModelSerializer):
#     u_company_id = serializers.CharField(required=True)
#
#     class Meta:
#         model = Company
#         fields = ('u_company_id',)
#
#     def validate(self, attrs):
#         if not Company.objects.filter(id=attrs['u_company_id']):
#             raise ValidationError('公司不存在或已被平台停用')
#         return attrs


class CompanystaffSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)

    class Meta:
        model = Company
        fields = ('company_id',)

    def validate(self, attrs):
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        return attrs


# 项目与公司 CRUD
class CreateprojectSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Project
        fields = ('company_id', 'user_id')

    def validate(self, attrs):
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
            # raise MyException(1001, '你的说法错误', '1不小于0')   # 500 error
            # raise Http404  # 无法自定义错误信息
        if not Company.objects.filter(c_u_id=attrs['user_id']):
            raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        return attrs


class ViewprojectSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Project
        fields = ('project_id', 'company_id', 'user_id')

    def validate(self, attrs):
        # print(attrs['project_id'])
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not Project.objects.filter(id=attrs['project_id']).filter(p_active=1):
            raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        project = Project.objects.get(id=attrs['project_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        # user = LoginUser.objects.get(id=attrs['user_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=project.p_c_id_id):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
                raise ValidationError(detail={'code': 994, 'message': '您无权访问其他公司项目'})
            return attrs
        return attrs


class EditprojectSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Project
        fields = ('project_id', 'company_id', 'user_id')

    def validate(self, attrs):
        # print(attrs['project_id'])
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not Project.objects.filter(id=attrs['project_id']).filter(p_active=1):
            raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        project = Project.objects.get(id=attrs['project_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=project.p_c_id_id).filter(
                u_type='公司管理员'):  # 如果用户不是公司管理员，需要他拥有后台人员身份
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
                raise ValidationError(detail={'code': 993, 'message': '您无权编辑其他公司项目'})
            return attrs
        return attrs


class ApplydeviceSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Device
        fields = ('project_id', 'company_id', 'user_id')

    def validate(self, attrs):
        print(attrs['project_id'])
        if not Project.objects.filter(id=attrs['project_id']).filter(p_active=1):
            raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not LoginUser.objects.filter(u_company_id=attrs['company_id']).filter(u_type='公司管理员'):
            raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        return attrs


class EditdeviceSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    device_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Device
        fields = ('company_id', 'device_id', 'user_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Device.objects.filter(id=attrs['device_id']).filter(d_active=1):
            raise ValidationError(detail={'code': 992, 'message': '设备不存在或已停用'})
        device = Device.objects.get(id=attrs['device_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='公司管理员') | Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']).filter(
                    Q(u_type='公司管理员') | Q(id=device.d_u_id)):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class DevicelistSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Device
        fields = ('company_id', 'project_id', 'user_id')

    def validate(self, attrs):
        if not Device.objects.filter(d_p_id=attrs['project_id']).filter(d_active=1):
            raise ValidationError(detail={'code': 991, 'message': '项目暂无可用设备'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']).filter(u_type='公司管理员'):
                if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']):
                    raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class SigndeviceSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=False, help_text='公司id，非必填')
    device_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)  # 操作人id，一般为公司管理员或平台工作人员
    operator_id = serializers.IntegerField(required=False, help_text='制定负责人的id，在关联设备功能时必填')  # 设备负责人id

    class Meta:
        model = Device
        fields = ('company_id', 'device_id', 'user_id', 'operator_id')

    def validate(self, attrs):
        if not Device.objects.filter(id=attrs['device_id']).filter(d_active=1):
            raise ValidationError(detail={'code': 992, 'message': '设备不存在或已停用'})
        device = Device.objects.get(id=attrs['device_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']).filter(
                    Q(u_type='公司管理员') | Q(id=device.d_u_id)):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class DataSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    data_id = serializers.IntegerField(required=True)

    class Meta:
        model = Data
        fields = ('company_id', 'data_id', 'user_id')

    def validate(self, attrs):
        if not Data.objects.filter(id=attrs['data_id']):
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        if not Company.objects.filter(id=attrs['company_id']).filter(c_u_id=attrs['user_id']):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='公司管理员') | Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class AlertSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    device_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    data_id = serializers.IntegerField(required=True)
    alert_id = serializers.IntegerField(required=False)

    class Meta:
        model = Alert
        fields = ('company_id', 'device_id', 'user_id', 'data_id', 'alert_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Device.objects.filter(id=attrs['device_id']).filter(d_active=1):
            raise ValidationError(detail={'code': 992, 'message': '设备不存在或已停用'})
        if not Data.objects.filter(id=attrs['data_id']):
            raise ValidationError(detail={'code': 987, 'message': '数据项不存在'})
        device = Device.objects.get(id=attrs['device_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']).filter(
                    Q(u_type='公司管理员') | Q(id=device.d_u_id)):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class ActivatecompanySerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)  # 后台员工id

    class Meta:
        model = Company
        fields = ('company_id', 'user_id')

    def validate(self, attrs):
        if not Company.objects.filter(id=attrs['company_id']):
            raise ValidationError(detail={'code': 986, 'message': '公司不存在'})
        if not Company.objects.filter(id=attrs['company_id']).filter(active=0):
            raise ValidationError(detail={'code': 985, 'message': '公司已激活'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class DeactivedevicelistSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = LoginUser
        fields = ('user_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class ActivatedeviceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    device_id = serializers.IntegerField(required=True)

    class Meta:
        model = Device
        fields = ('user_id', 'device_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Device.objects.filter(id=attrs['device_id']).filter(d_active=0):
            raise ValidationError(detail={'code': 984, 'message': '设备已激活，请刷新页面查看'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class AddworksheetSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    w_name = serializers.CharField(required=True)
    w_type = serializers.CharField(required=True)
    w_content = serializers.CharField(required=True)
    w_status = serializers.CharField(required=True)

    class Meta:
        model = Worksheet
        fields = ('user_id', 'w_name', 'w_type', 'w_content', 'w_status')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class ViewworksheetsSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = LoginUser
        fields = ('user_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


# class EditworksheetSerializer(serializers.ModelSerializer):
#     user_id = serializers.IntegerField(required=True)
#
#     class Meta:
#         model = LoginUser
#         fields = ('user_id',)
#
#     def validate(self, attrs):
#         if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
#             raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
#         if not LoginUser.objects.filter(id=attrs['user_id']).filter(
#                 Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
#             raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
#         return attrs

# class DeleteworksheetSerializer(serializers.ModelSerializer):
#     user_id = serializers.IntegerField(required=True)
#     w_id = serializers.IntegerField(required=True)
#
#     class Meta:
#         model = LoginUser
#         fields = ('user_id',)
#
#     def validate(self, attrs):
#         if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
#             raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
#         if not LoginUser.objects.filter(id=attrs['user_id']).filter(
#                 Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服')):
#             raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
#         return attrs
