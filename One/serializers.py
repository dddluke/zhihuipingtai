import re
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.validators import UniqueValidator
from django_redis import get_redis_connection
from .models import *
from django.core.cache import cache
from django.db.models import Q
from django.http import Http404


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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
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


# class RegisterSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(required=True)
#     password = serializers.CharField(required=True)
#     phone_numbers = serializers.CharField(required=True)
#     pwd2 = serializers.CharField(max_length=256, min_length=4, write_only=True)
#     code = serializers.CharField(required=True)
#
#
#     class Meta:
#         model = LoginUser
#         fields = ('username', 'password', 'pwd2', 'phone_numbers', 'code')
#
#     def validate(self, attrs):
#         # print(attrs['code'])
#         if LoginUser.objects.filter(phone_numbers=attrs['phone_numbers']):
#             raise ValidationError(detail={'code': 982, 'message': '手机号已注册'})
#         if LoginUser.objects.filter(username=attrs['username']):
#             raise ValidationError(detail={'code': 980, 'message': '用户名已注册'})
#         if not re_phone(attrs['phone_numbers']):
#             raise ValidationError(detail={'code': 983, 'message': '手机号码格式错误'})
#         # 'username', 'password'是系统用户表中已经存在的，系统会自动对用户输入的username进行检查
#         sms_code = cache.get(attrs['phone_numbers'])
#         print(sms_code)
#         print(attrs['code'])
#         # print('从redis取出的code:' sms_code)
#         if str(sms_code) != attrs['code']:
#             raise ValidationError(detail={'code': 979, 'message': '验证码错误或过期'})
#         if attrs['pwd2'] != attrs['password']:
#             raise ValidationError(detail={'code': 978, 'message': '两次密码输入不一致'})
#         # del attrs['pwd2']
#         # del attrs['code']
#         # attrs['password'] = make_password(attrs['password'])
#         return attrs

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    phone_numbers = serializers.CharField(required=True)
    pwd2 = serializers.CharField(max_length=256, min_length=4, write_only=True)
    # 短信验证码
    code = serializers.CharField(required=True)

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
        # 判断短信验证码是否输入正确
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % attrs['phone_numbers'])
        if sms_code_server is None:
            raise ValidationError(detail={'code': 9791, 'message': '验证码过期'})

        if sms_code_server.decode() != attrs['code']:
            raise ValidationError(detail={'code': 979, 'message': '验证码错误'})
        if attrs['pwd2'] != attrs['password']:
            raise ValidationError(detail={'code': 978, 'message': '两次密码输入不一致'})
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
        type = user.u_type
        u_type = ['员工', '公司管理员', '设备管理员', '游客']
        if type not in u_type:
            raise ValidationError(detail={'code': 964, 'message': '登录接口错误'})
        password = attrs['password']
        if not check_password(password, user.password):
            raise ValidationError(detail={'code': 976, 'message': '密码不正确'})
        return attrs


class LoginbSerializer(serializers.ModelSerializer):
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
        if not user:
            raise ValidationError(detail={'code': 977, 'message': '用户名输入有误'})
        user = LoginUser.objects.get(
            Q(username=attrs['ph']) | Q(phone_numbers=attrs['ph']) | Q(email=attrs['ph']))
        type = user.u_type
        u_type = ['客服', '运维', '运营', '超级管理员']
        if type not in u_type:
            raise ValidationError(detail={'code': 964, 'message': '登录接口错误'})
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
    username = serializers.CharField(required=False, allow_blank=True)
    phonenumber = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_blank=True)
    u_icon = serializers.FileField(required=False)

    class Meta:
        model = LoginUser
        fields = ('username', 'phonenumber', 'email', 'u_icon')

    def validate(self, attrs):
        # if LoginUser.objects.filter(phone_numbers=attrs['phonenumber']).count():
        #     raise ValidationError('手机号码已经注册')
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        user.username = "sdadasdasdasdsasd"

        user.save()
        if LoginUser.objects.filter(username=attrs['username']):
            raise ValidationError(detail={'code': 980, 'message': '用户名已经注册'})

        return attrs


class ChangepasswordSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='用户id')
    password = serializers.CharField(max_length=256, min_length=4, help_text='用户旧密码')
    newpassword = serializers.CharField(max_length=256, min_length=4, help_text='用户新密码')
    pwd2 = serializers.CharField(max_length=256, min_length=4, help_text='用户重复输入密码')


    class Meta:
        model = LoginUser
        fields = ('user_id', 'password', 'newpassword', 'pwd2')

    def validate(self, attrs):
        # print(attrs['password'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        if attrs['pwd2'] != attrs['newpassword']:
            raise ValidationError(detail={'code': 978, 'message': '两次密码输入不一致'})
        oldpassword = attrs['password']
        print(oldpassword)
        if not check_password(oldpassword, user.password):
            raise ValidationError(detail={'code': 976, 'message': '密码不正确'})
        return attrs


# 忘记密码 修改密码 未登录状态
class ForgotPasswordSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True, help_text='电话号码')
    text = serializers.CharField(required=True, help_text='图形验证码')
    pass_word = serializers.CharField(required=True, help_text='用户新密码')
    pass_word2 = serializers.CharField(required=True, help_text='确认新密码')
    phone_code = serializers.CharField(required=True, help_text='手机验证码')

    class Meta:
        model = LoginUser
        fields = ('phone_number', 'text', 'pass_word', 'pass_word2', 'phone_code')

    def validate(self, attrs):
        if not LoginUser.objects.filter(phone_numbers=attrs['phone_number']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not re_phone(attrs['phone_number']):
            raise ValidationError(detail={'code': 983, 'message': '手机号码格式错误'})
        # 'username', 'password'是系统用户表中已经存在的，系统会自动对用户输入的username进行检查
        # 判断短信验证码是否输入正确
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % attrs['phone_number'])

        if sms_code_server is None:
            raise ValidationError(detail={'code': 9791, 'message': '短信验证码过期'})

        if sms_code_server.decode() != attrs['phone_code']:
            raise ValidationError(detail={'code': 979, 'message': '短信验证码错误'})
        if attrs['pass_word2'] != attrs['pass_word']:
            raise ValidationError(detail={'code': 978, 'message': '两次密码输入不一致'})

        return attrs


# 修改手机号码
class ModifyPhoneNumberSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True, help_text='用户id')
    phone_number = serializers.CharField(required=True, help_text='电话号码')
    text = serializers.CharField(required=True, help_text='图形验证码')
    phone_code = serializers.CharField(required=True, help_text='手机验证码')

    class Meta:
        model = LoginUser
        fields = ('phone_number', 'text', 'user_id', 'phone_code')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not re_phone(attrs['phone_number']):
            raise ValidationError(detail={'code': 983, 'message': '手机号码格式错误'})
        # 'username', 'password'是系统用户表中已经存在的，系统会自动对用户输入的username进行检查
        # 判断短信验证码是否输入正确
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % attrs['phone_number'])

        if sms_code_server is None:
            raise ValidationError(detail={'code': 9791, 'message': '短信验证码过期'})

        if sms_code_server.decode() != attrs['phone_code']:
            raise ValidationError(detail={'code': 979, 'message': '短信验证码错误'})
        return attrs


class CreatecompanySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    company_name = serializers.CharField(required=True)
    company_address = serializers.CharField(required=False, allow_blank=True)
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
        # if not Company.objects.filter(c_u_id=attrs['user_id']):
        #     raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']).filter(
                u_type='公司管理员'):  # 如果用户不是公司管理员，需要他拥有后台人员身份
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


# 通过公司名字 搜索公司信息
class SelectCompanySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(required=True, help_text='公司名字')

    class Meta:
        model = Company
        fields = ('company_name',)


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
    user_id = serializers.IntegerField(required=True, help_text='员工id')
    user_id1 = serializers.IntegerField(required=True, help_text='操作人id,公司管理员')  # 操作人id
    company_id = serializers.IntegerField(required=True, help_text='公司id')  # 操作人id

    class Meta:
        model = LoginUser
        fields = ('user_id', 'user_id1', 'company_id')

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


class DeactivatestaffSerializerv2(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='被删除员工id')  # 被删除员工id
    user_id1 = serializers.IntegerField(required=True, help_text='操作人id')  # 操作人id

    class Meta:
        model = LoginUser
        fields = ('user_id', 'user_id1')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id1']).filter(is_active=1):
            raise ValidationError(detail={'code': 990, 'message': '您的账号不存在或已被停用'})
        if not LoginUser.objects.filter(id=attrs['user_id1']).filter(is_superuser=1):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        return attrs


class CompanystaffSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=False)

    class Meta:
        model = Company
        fields = ('company_id', 'user_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 990, 'message': '您的账号不存在或已被停用'})
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        return attrs


# 管理员创建员工账户
class ManagerCreateStaffSerializer(serializers.ModelSerializer):
    """
    管理员创建员工账户
    """
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    staff_name = serializers.CharField(required=True, help_text='员工姓名')
    staff_phone = serializers.CharField(required=True, help_text='员工电话号码')
    staff_password = serializers.CharField(required=True, help_text='员工账号密码')

    class Meta:
        model = LoginUser
        fields = ('user_id', 'staff_name', 'staff_phone', 'staff_password')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_type='公司管理员'):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


# 超级管理员创建后台员工
class ManagerCreateStaffSerializerv2(serializers.ModelSerializer):
    """
    超级管理员创建后台员工
    """
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    staff_name = serializers.CharField(required=True, help_text='员工姓名')
    staff_phone = serializers.CharField(required=True, help_text='员工电话号码')
    staff_password = serializers.CharField(required=True, help_text='员工账号密码')
    u_type = serializers.CharField(required=True, help_text='员工类型')

    class Meta:
        model = LoginUser
        fields = ('user_id', 'staff_name', 'staff_phone', 'staff_password', 'u_type')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_superuser=1):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if LoginUser.objects.filter(phone_numbers=attrs['staff_phone']):
            raise ValidationError(detail={'code': 982, 'message': '手机号已注册'})
        if LoginUser.objects.filter(username=attrs['staff_name']):
            raise ValidationError(detail={'code': 980, 'message': '用户名已注册'})
        if not re_phone(attrs['staff_phone']):
            raise ValidationError(detail={'code': 983, 'message': '手机号码格式错误'})
        return attrs


# 超级管理员编辑后台员工
class EditstaffSerializer(serializers.ModelSerializer):
    """
    超级管理员修改后台员工
    """
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    user_id1 = serializers.IntegerField(required=True, help_text='员工id')
    staff_name = serializers.CharField(required=True, help_text='员工姓名')
    staff_phone = serializers.CharField(required=True, help_text='员工电话号码')
    staff_password = serializers.CharField(required=True, help_text='员工账号密码')
    u_type = serializers.CharField(required=True, help_text='员工类型')

    class Meta:
        model = LoginUser
        fields = ('user_id', 'user_id1', 'staff_name', 'staff_phone', 'staff_password', 'u_type')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 990, 'message': '您的账号不存在或已被停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_superuser=1):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        user = LoginUser.objects.get(id=attrs['user_id1'])
        user.username = 'sadkjgfsiu'
        user.phone_numbers = '111111111'
        user.save()
        if LoginUser.objects.filter(phone_numbers=attrs['staff_phone']):
            raise ValidationError(detail={'code': 982, 'message': '手机号已注册'})
        if LoginUser.objects.filter(username=attrs['staff_name']):
            raise ValidationError(detail={'code': 980, 'message': '用户名已注册'})
        if not re_phone(attrs['staff_phone']):
            raise ValidationError(detail={'code': 983, 'message': '手机号码格式错误'})
        return attrs


# 项目与公司 CRUD
class CreateprojectSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    p_name = serializers.CharField(required=True, help_text='项目名称')
    p_description = serializers.CharField(required=False, allow_blank=True, help_text='项目简介')
    p_type = serializers.CharField(required=True, help_text='项目类型')
    p_customer_type = serializers.CharField(required=False, allow_blank=True, help_text='客户类型')
    p_party_a = serializers.CharField(required=True, help_text='甲方')
    p_purchase_time = serializers.CharField(required=False, allow_blank=True, help_text='采购日期')
    p_setup_time = serializers.CharField(required=False, allow_blank=True, help_text='安装日期')
    p_built_time = serializers.CharField(required=False, allow_blank=True, help_text='竣工日期')
    p_contact_name = serializers.CharField(required=False, allow_blank=True, help_text='联系人')
    p_contact_number = serializers.CharField(required=False, allow_blank=True, help_text='联系电话')
    p_dashboard = serializers.CharField(required=False, allow_blank=True, help_text='组套图链接')
    p_province = serializers.CharField(required=True, help_text='省')
    p_city = serializers.CharField(required=True, help_text='城市')
    p_address = serializers.CharField(required=True, help_text='地址')


    class Meta:
        model = Project
        fields = (
            'company_id', 'user_id', 'p_name', 'p_description', 'p_type', 'p_customer_type', 'p_party_a',
            'p_purchase_time',
            'p_setup_time', 'p_built_time',
            'p_contact_name', 'p_contact_number', 'p_province', 'p_city', 'p_address', 'p_dashboard')

    def validate(self, attrs):
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Company.objects.filter(c_u_id=attrs['user_id']):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
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
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=project.p_c_id_id):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 994, 'message': '您无权访问其他公司项目'})
            return attrs
        return attrs


class EditprojectSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    p_name = serializers.CharField(required=True, help_text='项目名称')
    p_description = serializers.CharField(required=False, allow_blank=True, help_text='项目简介')
    p_type = serializers.CharField(required=True, help_text='项目类型')
    p_customer_type = serializers.CharField(required=False, allow_blank=True, help_text='客户类型')
    p_party_a = serializers.CharField(required=True, help_text='甲方')
    p_purchase_time = serializers.CharField(required=False, allow_blank=True, help_text='采购日期')
    p_setup_time = serializers.CharField(required=False, allow_blank=True, help_text='安装日期')
    p_built_time = serializers.CharField(required=False, allow_blank=True, help_text='竣工日期')
    p_contact_name = serializers.CharField(required=False, allow_blank=True, help_text='联系人')
    p_contact_number = serializers.CharField(required=False, allow_blank=True, help_text='联系电话')
    p_province = serializers.CharField(required=True, help_text='省')
    p_city = serializers.CharField(required=True, help_text='城市')
    p_address = serializers.CharField(required=True, help_text='地址')
    p_dashboard = serializers.CharField(required=False, allow_blank=True, help_text='组态图链接')

    class Meta:
        model = Project
        fields = (
            'company_id', 'project_id', 'user_id', 'p_name', 'p_description', 'p_type', 'p_customer_type', 'p_party_a',
            'p_purchase_time',
            'p_setup_time', 'p_built_time',
            'p_contact_name', 'p_contact_number', 'p_province', 'p_city', 'p_address', 'p_dashboard')

    def validate(self, attrs):
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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 993, 'message': '您无权编辑其他公司项目'})
            return attrs
        return attrs


class DelprojectSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Project
        fields = ('project_id', 'company_id', 'user_id')

    def validate(self, attrs):
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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 993, 'message': '您无权编辑其他公司项目'})
            return attrs
        return attrs


class SignprojectSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True, help_text='项目ID')
    user_id = serializers.IntegerField(required=True, help_text='操作人ID')
    p_o_id = serializers.IntegerField(required=True, help_text='被指定员工ID')


    class Meta:
        model = Project
        fields = ('project_id', 'company_id', 'user_id', 'p_o_id')

    def validate(self, attrs):
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not Project.objects.filter(id=attrs['project_id']).filter(p_active=1):
            raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 990, 'message': '您的账户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['p_o_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 968, 'message': '员工不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']).filter(
                u_type='公司管理员'):  # 如果用户不是公司管理员，需要他拥有后台人员身份
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
            return attrs
        return attrs


class SignprojectSerializerv2(serializers.ModelSerializer):
    project_id = serializers.IntegerField(required=True, help_text='项目ID')
    user_id = serializers.IntegerField(required=True, help_text='操作人ID')

    class Meta:
        model = Project
        fields = ('project_id', 'user_id',)

    def validate(self, attrs):
        if not Project.objects.filter(id=attrs['project_id']).filter(p_active=1):
            raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 990, 'message': '您的账户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='公司管理员') | Q(u_type='设备管理员')):  # 如果用户不是公司管理员，需要他拥有后台人员身份
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
            return attrs
        return attrs


class ApplycollectdeviceSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True, help_text='公司ID')
    project_id = serializers.IntegerField(required=True, help_text='项目ID')
    user_id = serializers.IntegerField(required=True, help_text='申请人ID')
    cd_nodeid = serializers.CharField(required=True, help_text='采集设备ID')
    cd_name = serializers.CharField(required=False, help_text='设备名')
    cd_produce_time = serializers.CharField(required=False, help_text='设备出厂日期')
    cd_manufacturer = serializers.CharField(required=False, help_text='设备生产商')

    class Meta:
        model = Collectdevice
        fields = ('project_id', 'company_id', 'user_id', 'cd_nodeid', 'cd_name','cd_produce_time','cd_manufacturer')

    def validate(self, attrs):

        if not Project.objects.filter(id=attrs['project_id']).filter(p_active=1):
            raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not LoginUser.objects.filter(u_company_id=attrs['company_id']).filter(u_type='公司管理员'):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        return attrs


class Collectdeviceattlistv3Serializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='申请人ID')
    company_id = serializers.IntegerField(required=True, help_text='公司ID')

    class Meta:
        model = Collectdevice
        fields = ('user_id', 'company_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        return attrs


class EditcollectdeviceSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True, help_text='公司id')
    project_id = serializers.IntegerField(required=True, help_text='项目id')
    cdevice_id = serializers.IntegerField(required=True, help_text='采集设备id')
    user_id = serializers.IntegerField(required=True)
    cd_nodeid = serializers.CharField(required=True, help_text='采集设备ID')
    cd_name = serializers.CharField(required=False, help_text='设备名')
    cd_produce_time = serializers.CharField(required=False, help_text='设备出厂日期')
    cd_manufacturer = serializers.CharField(required=False, help_text='设备生产商')

    class Meta:
        model = Collectdevice
        fields = ('project_id', 'company_id', 'user_id', 'cdevice_id', 'cd_nodeid', 'cd_name', 'cd_produce_time', 'cd_manufacturer')

    def validate(self, attrs):
        if not Project.objects.filter(id=attrs['project_id']).filter(p_active=1):
            raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not Collectdevice.objects.filter(id=attrs['cdevice_id']):
            raise ValidationError(detail={'code': 969, 'message': '采集设备不存在或已被平台停用'})
        if not LoginUser.objects.filter(u_company_id=attrs['company_id']).filter(u_type='公司管理员'):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        return attrs


class EditcollectdeviceSerializerv2(serializers.ModelSerializer):
    cdevice_id = serializers.IntegerField(required=True, help_text='采集设备id')
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Collectdevice
        fields = ('user_id', 'cdevice_id')

    def validate(self, attrs):

        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Collectdevice.objects.filter(id=attrs['cdevice_id']):
            raise ValidationError(detail={'code': 969, 'message': '采集设备不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        return attrs


class CollectdeviceattSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    device_id = serializers.IntegerField(required=True, help_text='采集设备id')
    name = serializers.IntegerField(required=True, help_text='采集设备属性名')
    cdd_data = serializers.CharField(required=True, help_text='采集设备属性值')

    class Meta:
        model = Cdevicedata
        fields = ('user_id', 'device_id', 'name', 'cdd_data')

    def validate(self, attrs):

        if not Collectdevice.objects.filter(id=attrs['device_id']).filter(cd_active=1):
            raise ValidationError(detail={'code': 995, 'message': '采集设备不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(u_company_id=attrs['company_id']).filter(u_type='公司管理员'):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        return attrs


class EditcollectdeviceattSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    device_data_id = serializers.IntegerField(required=True, help_text='采集设备属性id')
    name = serializers.IntegerField(required=False, help_text='采集设备属性名,删除操作不用传值')
    cdd_data = serializers.CharField(required=False, allow_blank=True, help_text='采集设备属性值,删除操作不用传值')

    class Meta:
        model = Cdevicedata
        fields = ('user_id', 'device_data_id', 'name', 'cdd_data')

    def validate(self, attrs):

        if not Cdevicedata.objects.filter(id=attrs['device_data_id']):
            raise ValidationError(detail={'code': 995, 'message': '采集设备属性不存在'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(u_company_id=attrs['company_id']).filter(u_type='公司管理员'):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
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
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
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
                Q(u_type='公司管理员') | Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
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
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']).filter(
                    u_type='公司管理员'):
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
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']).filter(
                    Q(u_type='公司管理员') | Q(id=device.d_u_id)):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


# 添加设备属性 需公司管理员操作
class AdddeviceattSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True, help_text='管理员id')
    device_id = serializers.CharField(required=True, help_text='设备id')
    device_attribute = serializers.CharField(required=True, help_text='设备属性名')
    device_data = serializers.CharField(required=True, help_text='设备属性值')

    class Meta:
        model = Devicedata
        fields = ('device_id', 'device_attribute', 'user_id', 'device_data')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(u_type='公司管理员'):
            raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        return attrs


# 查看 编辑设备属性 需公司管理员操作
class EditdeviceattSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True, help_text='管理员id')
    device_id = serializers.CharField(required=True, help_text='设备id')
    device_attribute = serializers.CharField(required=True, help_text='设备属性名')
    device_data = serializers.CharField(help_text='设备属性值')

    class Meta:
        model = Devicedata
        fields = ('device_id', 'device_attribute', 'user_id', 'device_data')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Device.objects.filter(id=attrs['device_id']).filter(d_active=1):
            raise ValidationError(detail={'code': 992, 'message': '设备不存在或已停用'})
        if not LoginUser.objects.filter(u_type='公司管理员'):
            raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        return attrs


# 删除机械设备属性，需公司管理员操作
class DeldeviceattSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True, help_text='管理员id')
    device_id = serializers.CharField(required=True, help_text='设备id')
    device_attribute = serializers.CharField(required=True, help_text='设备属性名')

    class Meta:
        model = Devicedata
        fields = ('device_id', 'device_attribute', 'user_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Device.objects.filter(id=attrs['device_id']).filter(d_active=1):
            raise ValidationError(detail={'code': 992, 'message': '设备不存在或已停用'})
        if not LoginUser.objects.filter(u_type='公司管理员'):
            raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
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
                    Q(u_type='公司管理员') | Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
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
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']).filter(
                    Q(u_type='公司管理员') | Q(id=device.d_u_id)):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class UserComplainSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    employee_id = serializers.IntegerField(required=True)
    context = serializers.CharField(required=True)

    class Meta:
        model = Complainrecord
        fields = ('user_id', 'employee_id', 'context')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        return attrs


class UserDeleteComplainSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    employee_id = serializers.IntegerField(required=True)
    complain_id = serializers.IntegerField(required=True)

    class Meta:
        model = Complainrecord
        fields = ('user_id', 'employee_id', 'complain_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Complainrecord.objects.filter(cr_u_id=attrs['user_id']):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not Complainrecord.objects.filter(id=attrs['complain_id']):
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        return attrs


# 客户查看自己投诉记录列表
class SelectMyComplainSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Complainrecord
        fields = ('user_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        return attrs


#  客户查看自己投诉记录详情
class SelectComplainDetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    complain_id = serializers.IntegerField(required=True)

    class Meta:
        model = Complainrecord
        fields = ('user_id', 'complain_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Complainrecord.objects.filter(id=attrs['complain_id']):
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        return attrs


# 客户编辑自己的投诉记录
class ChangeMyComplainSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    complain_id = serializers.IntegerField(required=True)

    class Meta:
        model = Complainrecord
        fields = ('user_id', 'complain_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Complainrecord.objects.filter(id=attrs['complain_id']):
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        return attrs


# 客服查看自己投诉记录列表
class SelectEmployeeComplainSerializer(serializers.ModelSerializer):
    employee_id = serializers.IntegerField(required=True)

    class Meta:
        model = Complainrecord
        fields = ('employee_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['employee_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '客服不存在或已停用'})
        return attrs


# 客服查看自己投诉记录详情
class SelectEmployeeComplainDetailSerializer(serializers.ModelSerializer):
    employee_id = serializers.IntegerField(required=True)
    complain_id = serializers.IntegerField(required=True)

    class Meta:
        model = Complainrecord
        fields = ('employee_id', 'complain_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['employee_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '客服不存在或已停用'})
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
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
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
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class AddmaintainrecordSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    dm_d_id = serializers.IntegerField(required=True, help_text='设备id')
    dm_d_detail = serializers.CharField(required=False, allow_blank=True, help_text='维修记录详情')

    class Meta:
        model = Devicemaintainrecord
        fields = ('user_id', 'dm_d_id', 'dm_d_detail')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Device.objects.filter(id=attrs['dm_d_id']).filter(d_active=1):
            raise ValidationError(detail={'code': 992, 'message': '设备不存在或已停用'})
        device = Device.objects.get(id=attrs['dm_d_id'])
        d_u_id = device.d_u_id
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=d_u_id):
                if not LoginUser.objects.filter(u_type='公司管理员'):
                    raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class MaintainrecordSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    dm_d_id = serializers.IntegerField(required=True, help_text='设备id')

    class Meta:
        model = Devicemaintainrecord
        fields = ('user_id', 'dm_d_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Device.objects.filter(id=attrs['dm_d_id']).filter(d_active=1):
            raise ValidationError(detail={'code': 992, 'message': '设备不存在或已停用'})
        device = Device.objects.get(id=attrs['dm_d_id'])
        d_u_id = device.d_u_id
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=d_u_id):
                if not LoginUser.objects.filter(u_type='公司管理员'):
                    raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class MaintainrecorddetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    id = serializers.IntegerField(required=True, help_text='维修记录id')

    class Meta:
        model = Devicemaintainrecord
        fields = ('user_id', 'id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Devicemaintainrecord.objects.filter(id=attrs['id']):
            raise ValidationError(detail={'code': 970, 'message': '维修记录不存在'})
        record = Devicemaintainrecord.objects.get(id=attrs['id'])
        dm_d_id = record.dm_d_id_id
        device = Device.objects.get(id=dm_d_id)
        d_u_id = device.d_u_id
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=d_u_id):
                if not LoginUser.objects.filter(u_type='公司管理员'):
                    raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class AddworksheetSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    w_name = serializers.CharField(required=True, help_text='工单名称')
    w_type = serializers.CharField(required=True, help_text='工单类型，由用户自定义上传')
    w_content = serializers.CharField(required=True, help_text='工单内容')
    w_status = serializers.CharField(required=True, help_text='工单状态')

    class Meta:
        model = Worksheet
        fields = ('user_id', 'w_name', 'w_type', 'w_content', 'w_status')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class EditworksheetSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    w_id = serializers.IntegerField(required=True, help_text='工单id')
    w_name = serializers.CharField(required=True, help_text='工单名称')
    w_type = serializers.CharField(required=True, help_text='工单类型')
    w_content = serializers.CharField(required=True, help_text='工单详情')
    w_status = serializers.CharField(required=True, help_text='工单状态')

    class Meta:
        model = Worksheet
        fields = ('user_id', 'w_name', 'w_id', 'w_type', 'w_content', 'w_status')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not Worksheet.objects.filter(id=attrs['w_id']):
            raise ValidationError(detail={'code': 966, 'message': '工单不存在'})
        return attrs


class AddknowledgeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    k_title = serializers.CharField(required=True, help_text='文章标题')
    k_type = serializers.CharField(required=True, help_text='文章类型：知识库或行业资讯')
    k_content = serializers.CharField(required=True, help_text='文章内容')
    k_tag = serializers.CharField(required=True, help_text='文章标签')

    class Meta:
        model = Knowledge
        fields = ('user_id', 'k_title', 'k_type', 'k_content', 'k_tag')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class AddenterpriseSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    e_title = serializers.CharField(required=True, help_text='文章标题')
    e_image = serializers.FileField(required=False, help_text='封面图')
    e_content = serializers.CharField(required=True, help_text='文章内容')

    class Meta:
        model = Enterprise
        fields = ('user_id', 'e_title', 'e_image', 'e_content')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class EditenterpriseSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    k_id = serializers.IntegerField(required=True, help_text='文章id')
    e_title = serializers.CharField(required=False, allow_blank=True, help_text='文章标题, 做删除操作时不用传值')
    e_image = serializers.FileField(required=False, help_text='封面图')
    e_content = serializers.CharField(required=False, allow_blank=True, help_text='文章内容, 做删除操作时不用传值')
    # print(e_image)
    class Meta:
        model = Enterprise
        fields = ('user_id', 'k_id', 'e_title', 'e_image', 'e_content')

    def validate(self, attrs):
        # print(attrs['e_image'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not Enterprise.objects.filter(id=attrs['k_id']):
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        return attrs


class EditknowledgeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    k_id = serializers.IntegerField(required=True, help_text='文章id')
    k_title = serializers.CharField(required=False, allow_blank=True, help_text='文章标题, 做删除操作时不用传值')
    k_content = serializers.CharField(required=False, allow_blank=True, help_text='文章内容, 做删除操作时不用传值')
    k_tag = serializers.CharField(required=False, allow_blank=True, help_text='文章标签')

    class Meta:
        model = Knowledge
        fields = ('user_id', 'k_id', 'k_title', 'k_content', 'k_tag')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not Knowledge.objects.filter(id=attrs['k_id']):
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        return attrs


class AddsolutionSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    s_k_id = serializers.IntegerField(required=True, help_text='问题文章id')
    s_id = serializers.IntegerField(required=False, help_text='解决方案id, 新建时非必传')
    s_title = serializers.CharField(required=False, allow_blank=True, help_text='文章标题，查看、删除操作时非必传')
    s_type = serializers.CharField(required=False, allow_blank=True, help_text='文章类型：知识库或行业资讯解决方案，查看、删除操作时非必传')
    s_content = serializers.CharField(required=False, allow_blank=True, help_text='文章内容, 做删除操作时不用传值，查看、删除操作时非必传')

    class Meta:
        model = Knowledge
        fields = ('user_id', 's_k_id', 's_id', 's_title', 's_type', 's_content')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not Knowledge.objects.filter(id=attrs['s_k_id']):
            raise ValidationError(detail={'code': 965, 'message': '文章不存在'})
        if Solution.objects.filter(s_k_id_id=attrs['s_k_id']):
            raise ValidationError(detail={'code': 967, 'message': '解决方案已存在'})
        return attrs


class EmployeelistSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=False)

    class Meta:
        model = LoginUser
        fields = ('user_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 990, 'message': '您的账号不存在或已被停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_superuser=1):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class EditsolutionSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    s_k_id = serializers.IntegerField(required=True, help_text='问题文章id')
    s_id = serializers.IntegerField(required=False, help_text='解决方案id, 新建时非必传')
    s_title = serializers.CharField(required=False, allow_blank=True, help_text='文章标题，查看、删除操作时非必传')
    s_type = serializers.CharField(required=False, allow_blank=True, help_text='文章类型：知识库或行业资讯解决方案，查看、删除操作时非必传')
    s_content = serializers.CharField(required=False, allow_blank=True, help_text='文章内容, 做删除操作时不用传值，查看、删除操作时非必传')

    class Meta:
        model = Knowledge
        fields = ('user_id', 's_k_id', 's_id', 's_title', 's_type', 's_content')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not Knowledge.objects.filter(id=attrs['s_k_id']):
            raise ValidationError(detail={'code': 965, 'message': '文章不存在'})
        return attrs

class WisepasstokenSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True, help_text='用户id')

    class Meta:
        model = LoginUser
        fields = ('id', )

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        return attrs


class WisepasstokenSerializerV2(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True, help_text='用户id')
    token = serializers.CharField(required=True, allow_blank=True, help_text='研华token')

    class Meta:
        model = LoginUser
        fields = ('id', 'token')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs