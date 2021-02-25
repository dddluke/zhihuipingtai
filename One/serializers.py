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


def re_picture_form(picture):
    suffix = picture.name.rfind('.')
    if suffix == -1:
        return 1  # 图片不正确
    file_postfix = picture.name[suffix + 1:]
    if file_postfix not in ['jpg', 'png', 'gif', 'bmp', 'jpeg', 'JPG', 'PNG',
                            'BMP', 'JPEG', ]:
        return 2  # 图片格式不正确


def re_email(email):
    ret = re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email)
    if ret:
        return True
    return False


class MyException(Exception):
    def __init__(self, code, error, data):
        self.code = code
        self.error = error
        self.data = data


def re_phone(phonenumber):
    reg = '^[1](([3][0-9])|([4][5-9])|([5][0-3,5-9])|([6][5,6])|([7][0-8])|([8][0-9])|([9][1,8,9]))[0-9]{8}$'
    ret = re.match(reg, phonenumber)
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class DeviceStatusSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('user_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
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
    # pwd2 = serializers.CharField(max_length=256, min_length=4, write_only=True)
    # 短信验证码
    code = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('username', 'password', 'phone_numbers', 'code')

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
        # if attrs['pwd2'] != attrs['password']:
        #     raise ValidationError(detail={'code': 978, 'message': '两次密码输入不一致'})
        # del attrs['pwd2']
        # del attrs['code']
        # attrs['password'] = make_password(attrs['password'])
        return attrs


class WechatLoginSerializerv2(serializers.ModelSerializer):
    phone_numbers = serializers.CharField(required=True)
    # 短信验证码
    code = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('phone_numbers', 'code')

    def validate(self, attrs):
        # print(attrs['code'])
        if not LoginUser.objects.filter(phone_numbers=attrs['phone_numbers']):
            raise ValidationError(detail={'code': 981, 'message': '手机号码未注册'})
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
        # if attrs['pwd2'] != attrs['password']:
        #     raise ValidationError(detail={'code': 978, 'message': '两次密码输入不一致'})
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
        type = user.u_type
        u_type = ['员工', '公司管理员', '设备管理员', '游客']
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


class LeaveContactMessageSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    company = serializers.CharField(required=False, allow_blank=True)
    question = serializers.CharField(required=True)
    contactnumber = serializers.CharField(required=True)

    class Meta:
        model = ContactUs
        fields = ('name', 'company', 'question', 'contactnumber')

    def validate(self, attrs):
        return attrs


class ContactMessageListSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('user_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class ViewContactMessageSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True)
    c_id = serializers.IntegerField(required=True)

    class Meta:
        model = LoginUser
        fields = ('user_id', 'c_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not ContactUs.objects.filter(id=attrs['c_id']):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class WechatLoginSerializerV1(serializers.ModelSerializer):
    ph = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('ph', 'password')

    def validate(self, attrs):
        user = LoginUser.objects.filter(
            Q(username=attrs['ph']) | Q(phone_numbers=attrs['ph']) | Q(email=attrs['ph'])).first()
        if not user:
            raise ValidationError(detail={'code': 977, 'message': '用户名输入有误'})
        user = LoginUser.objects.get(
            Q(username=attrs['ph']) | Q(phone_numbers=attrs['ph']) | Q(email=attrs['ph']))

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
        u_type = ['客服运营', '运维', '运营', '超级管理员']
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


class ChangeIconSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    u_icon = serializers.FileField(required=True)

    class Meta:
        model = LoginUser
        fields = ('user_id', 'u_icon')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})

        return attrs


class SearchDeviceSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    d_name = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('user_id', 'd_name')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        company_id = user.u_company_id
        if user.u_type == '':
            raise ValidationError(detail={'code': 963, 'message': '您当前没有关联的设备'})
        if user.u_type == '游客':
            raise ValidationError(detail={'code': 963, 'message': '您当前没有关联的设备'})
        if user.u_type == '员工':
            raise ValidationError(detail={'code': 963, 'message': '您当前没有关联的设备'})
        if not Device.objects.filter(d_name=attrs['d_name'], d_co_id=company_id):  # 属于自己公司的
            if not LoginUser.objects.filter(Q(u_type='设备管理员') | Q(u_type='公司管理员')):  # 是设备管理员或者公司管理员
                raise ValidationError(detail={'code': 992, 'message': '设备不存在'})
        return attrs


class SearchDeviceSerializerV1(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    d_name = serializers.CharField(required=True)
    company_name = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('user_id', 'd_name', 'company_name')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Company.objects.filter(company_name=attrs['company_name'], active=1):
            raise ValidationError(detail={'code': 997, 'message': '公司不存在或已被平台停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        if not LoginUser.objects.filter(Q(u_type='超级管理员') | Q(u_type='客服运营')):  # 是设备管理员或者公司管理员
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
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
        # del attrs['pwd2']
        # del attrs['code']
        # attrs['password'] = make_password(attrs['password'])
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


# class CreatecompanySerializer(serializers.ModelSerializer):
#     user_id = serializers.IntegerField(required=True)
#     company_name = serializers.CharField(required=True)
#     company_address = serializers.CharField(required=False, allow_blank=True)
#     context = serializers.CharField(required=False)
#     company_icon = serializers.FileField(required=True)
#
#     class Meta:
#         model = Company
#         fields = ('user_id', 'company_name', 'company_address', 'context', 'company_icon')
#
#     def validate(self, attrs):
#         if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
#             raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
#         if Company.objects.filter(company_name=attrs['company_name']):
#             # raise ValidationError('公司名已注册')
#             raise ValidationError(detail={'code': 974, 'message': '公司名已注册'})
#         # print(attrs['company_address'])
#         # if attrs['company_address'] == '':
#         #     attrs['company_name'] == '无'
#         if Company.objects.filter(c_u_id_id=attrs['user_id']):
#             raise ValidationError(detail={'code': 973, 'message': '每个用户只能创建一个公司'})
#         return attrs
class CreatecompanySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text="用户id")
    company_name = serializers.CharField(max_length=32, required=True, help_text="企业名")
    company_mailbox = serializers.CharField(required=True, max_length=50, help_text="企业邮箱")
    company_address = serializers.CharField(max_length=64, required=True, help_text="企业地址")
    company_zip_code = serializers.IntegerField(required=True, help_text="企业邮编")
    company_icon = serializers.FileField(required=True, help_text="企业标志")
    company_content = serializers.CharField(max_length=5000, required=False, help_text="企业简介", allow_blank=True)
    company_register_number = serializers.IntegerField(required=True, help_text="营业执照注册号")
    company_license = serializers.FileField(required=True, help_text="营业执照副本扫描件")
    company_begin_date = serializers.CharField(required=True, help_text="企业成立日期")
    company_office_number = serializers.CharField(max_length=30, required=True, help_text="企业对公账号")
    # company_boss_ID_card = serializers.FileField(required=True, help_text="法人代表身份证")
    company_business_range = serializers.CharField(max_length=30, required=False, help_text="经营范围", allow_blank=True)
    company_register_money = serializers.CharField(required=False, help_text="注册资本",
                                                   allow_blank=True)  # Intergerfield 不能使用allow_blank

    # company_organize_code = serializers.CharField(max_length=30, required=False, help_text="组织机构代码", allow_blank=True)

    class Meta:
        model = Company
        fields = (
            'user_id', 'company_name', 'company_address', 'company_zip_code', 'company_content', 'company_mailbox',
            'company_register_number', 'company_icon', 'company_license', 'company_begin_date', 'company_office_number',
            'company_business_range', 'company_register_money')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if Company.objects.filter(company_name=attrs['company_name']):
            # raise ValidationError('公司名已注册')
            raise ValidationError(detail={'code': 974, 'message': ['公司名已注册']})
        if not re_email(attrs["company_mailbox"]):
            raise ValidationError(detail={'code': 975, 'message': ["邮箱格式不正确"]})
        # if not re_picture_size(attrs["company_icon"]):
        #     raise ValidationError(detail={'code': 976, 'message': ["企业标志图片大小超出限制"]})
        # if not re_picture_size(attrs["company_license"]):
        #     raise ValidationError(detail={'code': 976, 'message': ["营业执照副本扫描件图片大小超出限制"]})
        # if not re_picture_size(attrs["company_boss_ID_card"]):
        #     raise ValidationError(detail={'code': 976, 'message': ["法人代表身份证图片大小超出限制"]})
        if re_picture_form(attrs["company_icon"]) == 1:
            raise ValidationError(detail={'code': 977, 'message': ["企业标志图片不正确"]})
        elif re_picture_form(attrs["company_icon"]) == 2:
            raise ValidationError(detail={'code': 978, 'message': ["企业标志图片格式不正确"]})
        if re_picture_form(attrs["company_license"]) == 1:
            raise ValidationError(detail={'code': 977, 'message': ["营业执照副本扫描件图片不正确"]})
        elif re_picture_form(attrs["company_license"]) == 2:
            raise ValidationError(detail={'code': 978, 'message': ["营业执照副本扫描件图片格式不正确"]})
        # if re_picture_form(attrs["company_boss_ID_card"]) == 1:
        #     raise ValidationError(detail={'code': 977, 'message': ["法人代表身份证图片不正确"]})
        # elif re_picture_form(attrs["company_boss_ID_card"]) == 2:
        #     raise ValidationError(detail={'code': 978, 'message': ["法人代表身份证图片格式不正确"]})
        if Company.objects.filter(c_u_id_id=attrs['user_id']):
            raise ValidationError(detail={'code': 973, 'message': ['每个用户只能创建一个公司']})
        return attrs


class CreatecompanySerializerv2(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='公司管理员id')
    superuser_id = serializers.IntegerField(required=True, help_text='超级管理员id')
    company_name = serializers.CharField(max_length=32, required=True, help_text="企业名")
    company_mailbox = serializers.CharField(required=True, max_length=50, help_text="企业邮箱")
    company_address = serializers.CharField(max_length=64, required=True, help_text="企业地址")
    company_zip_code = serializers.IntegerField(required=True, help_text="企业邮编")
    company_icon = serializers.FileField(required=True, help_text="企业标志")
    company_content = serializers.CharField(max_length=5000, required=False, help_text="企业简介", allow_blank=True)
    company_register_number = serializers.IntegerField(required=True, help_text="营业执照注册号")
    company_license = serializers.FileField(required=True, help_text="营业执照副本扫描件")
    company_begin_date = serializers.CharField(required=True, help_text="企业成立日期")
    company_office_number = serializers.CharField(max_length=30, required=True, help_text="企业对公账号")
    # company_boss_ID_card = serializers.FileField(required=True, help_text="法人代表身份证")
    company_business_range = serializers.CharField(max_length=30, required=False, help_text="经营范围", allow_blank=True)
    company_register_money = serializers.CharField(required=False, help_text="注册资本",
                                                   allow_blank=True)  # Intergerfield 不能使用allow_blank

    # company_organize_code = serializers.CharField(max_length=30, required=False, help_text="组织机构代码", allow_blank=True)

    class Meta:
        model = Company
        fields = ('user_id', 'superuser_id', 'company_name', 'company_address', 'company_zip_code', 'company_content',
                  'company_mailbox',
                  'company_register_number', 'company_icon', 'company_license', 'company_begin_date',
                  'company_office_number', 'company_business_range', 'company_register_money')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if Company.objects.filter(company_name=attrs['company_name']):
            # raise ValidationError('公司名已注册')
            raise ValidationError(detail={'code': 974, 'message': '公司名已注册'})
        if Company.objects.filter(c_u_id_id=attrs['user_id']):
            raise ValidationError(detail={'code': 973, 'message': '每个用户只能创建一个公司'})
        if not LoginUser.objects.filter(id=attrs['superuser_id']).filter(u_type='超级管理员'):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class UKMactchTagSerializer(serializers.ModelSerializer):
    "用户和知识库通过标签匹配"
    user_id = serializers.CharField(required=False, allow_blank=True, help_text='用户id')
    page = serializers.CharField(required=False, allow_blank=True)
    per_page = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = LoginUser
        fields = ('user_id', 'page', 'per_page')

    def validate(self, attrs):
        a = attrs['user_id']
        if a == '':
            a = None
        # print(a)
        if a is not None:
            if not LoginUser.objects.filter(id=a).filter(is_active=1):
                raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if a is None:
            raise ValidationError(detail={'code': 957, 'message': "您关注的标签下尚未存在知识库"})
        return attrs


# class EditcompanySerializer(serializers.ModelSerializer):
#     user_id = serializers.IntegerField(required=True)
#     company_id = serializers.IntegerField(required=True)
#     company_name = serializers.CharField(required=True)
#     company_address = serializers.CharField(required=True)
#     context = serializers.CharField(required=False)
#     company_icon = serializers.FileField(required=False)
#
#     class Meta:
#         model = Company
#         fields = ('user_id', 'company_id', 'company_name', 'company_address', 'context', 'company_icon')
#
#     def validate(self, attrs):
#         # flag = 1
#         if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
#             raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
#         if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
#             raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
#         if not Company.objects.filter(c_u_id=attrs['user_id']):
#             raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
#         return attrs
class EditcompanySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text="用户id")
    company_id = serializers.IntegerField(required=True, help_text="公司id")
    company_name = serializers.CharField(max_length=32, required=True, help_text="企业名")
    company_mailbox = serializers.CharField(required=True, max_length=50, help_text="企业邮箱")
    company_address = serializers.CharField(max_length=64, required=True, help_text="企业地址")
    company_zip_code = serializers.IntegerField(required=True, help_text="企业邮编")
    # company_icon = serializers.FileField(required=False, help_text="企业标志")
    company_content = serializers.CharField(max_length=5000, required=False, help_text="企业简介", allow_blank=True)
    company_register_number = serializers.IntegerField(required=True, help_text="营业执照注册号")
    # company_license = serializers.FileField(required=False, help_text="营业执照副本扫描件")
    company_begin_date = serializers.CharField(required=True, help_text="企业成立日期")
    company_office_number = serializers.CharField(max_length=30, required=True, help_text="企业对公账号")
    # company_boss_ID_card = serializers.FileField(required=False, help_text="法人代表身份证", )
    company_business_range = serializers.CharField(max_length=30, required=False, help_text="经营范围", allow_blank=True)
    company_register_money = serializers.CharField(required=False, help_text="注册资本", allow_blank=True)

    # company_organize_code = serializers.CharField(max_length=30, required=False, help_text="组织机构代码", allow_blank=True)

    class Meta:
        model = Company
        # fields = (
        #     'user_id', 'company_name', 'company_id','company_address', 'company_zip_code', 'company_content', 'company_mailbox',
        #     'company_register_number', 'company_icon', 'company_license', 'company_begin_date', 'company_office_number',
        #     'company_boss_ID_card', 'company_business_range', 'company_register_money', 'company_organize_code')
        fields = (
            'user_id', 'company_name', 'company_id', 'company_address', 'company_zip_code', 'company_content',
            'company_mailbox',
            'company_register_number', 'company_begin_date', 'company_office_number',
            'company_business_range', 'company_register_money')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not Company.objects.filter(c_u_id=attrs['user_id']):
            raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        if not re_email(attrs["company_mailbox"]):
            raise ValidationError(detail={'code': 975, 'message': ["邮箱格式不正确"]})
        # if attrs["company_icon"] is not None:
        #     if re_picture_form(attrs["company_icon"]) == 1:
        #         raise ValidationError(detail={'code': 977, 'message': ["企业标志图片不正确"]})
        #     elif re_picture_form(attrs["company_icon"]) == 2:
        #         raise ValidationError(detail={'code': 978, 'message': ["企业标志图片格式不正确"]})
        # if attrs["company_license"] is not None:
        #     if re_picture_form(attrs["company_license"]) == 1:
        #         raise ValidationError(detail={'code': 977, 'message': ["营业执照副本扫描件图片不正确"]})
        #     elif re_picture_form(attrs["company_license"]) == 2:
        #         raise ValidationError(detail={'code': 978, 'message': ["营业执照副本扫描件图片格式不正确"]})
        # if attrs["company_boss_ID_card"] is not None:
        #     if re_picture_form(attrs["company_boss_ID_card"]) == 1:
        #         raise ValidationError(detail={'code': 977, 'message': ["法人代表身份证图片不正确"]})
        #     elif re_picture_form(attrs["company_boss_ID_card"]) == 2:
        #         raise ValidationError(detail={'code': 978, 'message': ["法人代表身份证图片格式不正确"]})

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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
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
    # staff_id = serializers.IntegerField(required=True, help_text='员工id')
    staff_name = serializers.CharField(required=True, help_text='员工姓名')
    staff_phone = serializers.CharField(required=True, help_text='员工电话号码')
    staff_password = serializers.CharField(required=True, help_text='员工账号密码')
    staff_work = serializers.CharField(required=True, help_text="员工职务")
    staff_email = serializers.CharField(required=True, help_text="员工邮箱")

    # company_id = serializers.IntegerField(required=True, help_text='公司id')

    class Meta:
        model = LoginUser
        fields = ('user_id', 'staff_name', 'staff_phone', 'staff_password', "staff_work", "staff_email")

    def validate(self, attrs):
        if LoginUser.objects.filter(phone_numbers=attrs['staff_phone']):
            raise ValidationError(detail={'code': 982, 'message': ['手机号已注册']})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_type='公司管理员'):
            raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        if not re_email(attrs["staff_email"]):
            raise ValidationError(detail={'code': 975, 'message': ["邮箱格式不正确"]})
        return attrs


# 管理员修改员工信息ser
class MCSworkSerializer(serializers.ModelSerializer):
    staff_id = serializers.IntegerField(required=True, help_text="员工id")
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    staff_work = serializers.CharField(required=True, help_text="员工职务")

    class Meta:
        model = LoginUser
        fields = ("staff_work", "staff_id", "user_id")

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['staff_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_type='公司管理员'):
            raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
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


# 超级管理员创建公司管理员
class ManagerCreateStaffSerializerv3(serializers.ModelSerializer):
    """
    超级管理员创建公司管理员
    """
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    staff_name = serializers.CharField(required=True, help_text='员工姓名')
    staff_phone = serializers.CharField(required=True, help_text='员工电话号码')
    staff_password = serializers.CharField(required=True, help_text='员工账号密码')

    class Meta:
        model = LoginUser
        fields = ('user_id', 'staff_name', 'staff_phone', 'staff_password')

    def validate(self, attrs):
        if LoginUser.objects.filter(phone_numbers=attrs['staff_phone']):
            raise ValidationError(detail={'code': 982, 'message': '手机号已注册'})
        if not re_phone(attrs['staff_phone']):
            raise ValidationError(detail={'code': 983, 'message': '手机号码格式错误'})
        if LoginUser.objects.filter(username=attrs['staff_name']):
            raise ValidationError(detail={'code': 980, 'message': '用户名已注册'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_type='超级管理员'):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
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
    # p_type = serializers.CharField(required=True, help_text='项目类型')
    p_customer_type = serializers.CharField(required=False, allow_blank=True, help_text='客户类型')
    p_party_a = serializers.CharField(required=True, help_text='甲方')
    p_purchase_time = serializers.CharField(required=False, allow_blank=True, help_text='采购日期')
    p_setup_time = serializers.CharField(required=False, allow_blank=True, help_text='安装日期')
    p_built_time = serializers.CharField(required=False, allow_blank=True, help_text='竣工日期')
    p_contact_name = serializers.CharField(required=False, allow_blank=True, help_text='联系人')
    p_contact_number = serializers.CharField(required=False, allow_blank=True, help_text='联系电话')
    p_dashboard = serializers.CharField(required=False, allow_blank=True, help_text='组套图链接')
    # p_province = serializers.CharField(required=True, help_text='省')
    # p_city = serializers.CharField(required=True, help_text='城市')
    # p_address = serializers.CharField(required=True, help_text='地址')
    p_c_address = serializers.CharField(required=True, help_text='省')

    p_address = serializers.CharField(required=True, help_text='地址', max_length=40)
    p_position = serializers.CharField(required=False, help_text='经纬度', max_length=40)

    # p_longitude = serializers.CharField(required=False, allow_blank=True, help_text='经度')
    # p_latitude = serializers.CharField(required=False, allow_blank=True, help_text='纬度')

    class Meta:
        model = Project
        fields = (
            'company_id', 'user_id', 'p_name', 'p_description', 'p_customer_type', 'p_party_a',
            'p_purchase_time', 'p_position', 'p_c_address',
            'p_setup_time', 'p_built_time',
            'p_contact_name', 'p_contact_number', 'p_address', 'p_dashboard')

    def validate(self, attrs):
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
            # raise MyException(1001, '你的说法错误', '1不小于0')   # 500 error
            # raise Http404  # 无法自定义错误信息
        if not Company.objects.filter(c_u_id=attrs['user_id']):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
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
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not Project.objects.filter(id=attrs['project_id']).filter(p_active=1):
            raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        project = Project.objects.get(id=attrs['project_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=project.p_c_id_id):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 994, 'message': '您无权访问其他公司项目'})
            return attrs
        return attrs


class EditprojectSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    p_name = serializers.CharField(required=True, help_text='项目名称')
    p_description = serializers.CharField(required=False, allow_blank=True, help_text='项目简介')
    # p_type = serializers.CharField(required=True, help_text='项目类型')
    p_customer_type = serializers.CharField(required=False, allow_blank=True, help_text='客户类型')
    p_party_a = serializers.CharField(required=True, help_text='甲方')
    p_purchase_time = serializers.CharField(required=False, allow_blank=True, help_text='采购日期')
    p_setup_time = serializers.CharField(required=False, allow_blank=True, help_text='安装日期')
    p_built_time = serializers.CharField(required=False, allow_blank=True, help_text='竣工日期')
    p_contact_name = serializers.CharField(required=False, allow_blank=True, help_text='联系人')
    p_contact_number = serializers.CharField(required=False, allow_blank=True, help_text='联系电话')
    p_c_address = serializers.CharField(required=True, help_text='公司地址')
    p_position = serializers.CharField(required=False, help_text='经纬度', max_length=40)
    p_address = serializers.CharField(required=True, help_text='地址')
    p_dashboard = serializers.CharField(required=False, allow_blank=True, help_text='组态图链接')

    class Meta:
        model = Project
        fields = (
            'company_id', 'project_id', 'user_id', 'p_name', 'p_description', 'p_customer_type', 'p_party_a',
            'p_purchase_time', 'p_position',
            'p_setup_time', 'p_built_time',
            'p_contact_name', 'p_contact_number', 'p_c_address', 'p_address', 'p_dashboard')

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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 993, 'message': '您无权编辑其他公司项目'})
            return attrs
        return attrs


class SignprojectSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True, help_text='项目ID')
    user_id = serializers.IntegerField(required=True, help_text='操作人ID')
    p_o_id = serializers.IntegerField(required=True, help_text='被指定员工ID')

    # p_name = serializers.CharField(required=True)

    class Meta:
        model = Project
        fields = ('project_id', 'company_id', 'user_id', 'p_o_id')

    def validate(self, attrs):
        # print(attrs['project_id'])
        if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not Project.objects.filter(id=attrs['project_id']).filter(p_active=1):
            raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        # project = Project.objects.get(id=attrs['project_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 990, 'message': '您的账户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['p_o_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 968, 'message': '员工不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        # print(attrs['user_id'])
        # print(attrs['company_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']).filter(
                u_type='公司管理员'):  # 如果用户不是公司管理员，需要他拥有后台人员身份
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
            return attrs
        return attrs


class SignprojectSerializerv2(serializers.ModelSerializer):
    project_id = serializers.IntegerField(required=True, help_text='项目ID')
    user_id = serializers.IntegerField(required=True, help_text='操作人ID')

    # p_name = serializers.CharField(required=True)

    class Meta:
        model = Project
        fields = ('project_id', 'user_id',)

    def validate(self, attrs):
        # print(attrs['project_id'])
        if not Project.objects.filter(id=attrs['project_id']).filter(p_active=1):
            raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        # project = Project.objects.get(id=attrs['project_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 990, 'message': '您的账户不存在或已停用'})
        # user = LoginUser.objects.get(id=attrs['user_id'])
        # print(attrs['user_id'])
        # print(attrs['company_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='公司管理员') | Q(u_type='设备管理员')):  # 如果用户不是公司管理员，需要他拥有后台人员身份
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
            return attrs
        return attrs


class ApplycollectdeviceSerializer(serializers.ModelSerializer):
    # company_id = serializers.IntegerField(required=True, help_text='公司ID')
    # project_id = serializers.IntegerField(required=True, help_text='项目ID')
    user_id = serializers.IntegerField(required=True, help_text='申请人ID')
    cd_name = serializers.CharField(required=False, help_text='设备名')
    cd_produce_time = serializers.CharField(required=False, help_text='设备出厂日期')
    cd_manufacturer = serializers.CharField(required=False, help_text='设备生产商')
    cd_install_time = serializers.CharField(required=False, help_text='设备安装时间')
    cd_placed = serializers.CharField(required=False, help_text='设备安装地址')
    cd_SN = serializers.CharField(required=False, help_text='设备SN')
    cd_SIM = serializers.CharField(required=False, help_text='设备SIM卡号')
    cd_GPS = serializers.CharField(required=False, help_text='设备GPS')

    class Meta:
        model = Collectdevice
        fields = (
            'user_id', 'cd_name', 'cd_produce_time', 'cd_manufacturer', 'cd_install_time', 'cd_placed', 'cd_SN',
            'cd_SIM',
            'cd_GPS')

    def validate(self, attrs):
        # if not Project.objects.filter(id=attrs['project_id']).filter(p_active=1):
        #     raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        # if not Company.objects.filter(id=attrs['company_id']).filter(active=1):
        #     raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        # if not LoginUser.objects.filter(u_company_id=attrs['company_id']).filter(u_type='公司管理员'):
        #     if not LoginUser.objects.filter(id=attrs['user_id']).filter(
        #             Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
        #         raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
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
    cd_name = serializers.CharField(required=False, help_text='设备名')
    cd_produce_time = serializers.CharField(required=False, help_text='设备出厂日期')
    cd_manufacturer = serializers.CharField(required=False, help_text='设备生产商')
    cd_install_time = serializers.CharField(required=False, help_text='设备安装时间')
    cd_placed = serializers.CharField(required=False, help_text='设备安装地址')
    cd_SN = serializers.CharField(required=False, help_text='设备SN')
    cd_SIM = serializers.CharField(required=False, help_text='设备SIM卡号')
    cd_GPS = serializers.CharField(required=False, help_text='设备GPS')

    class Meta:
        model = Collectdevice
        fields = ('project_id', 'company_id', 'user_id', 'cdevice_id', 'cd_name', 'cd_install_time', 'cd_produce_time',
                  'cd_manufacturer', 'cd_placed', 'cd_SN', 'cd_SIM', 'cd_GPS')

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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        return attrs


class CollectdeviceattSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    device_id = serializers.IntegerField(required=True, help_text='采集设备id')
    name = serializers.IntegerField(required=True, help_text='采集设备属性名')
    cdd_data = serializers.CharField(required=True, help_text='采集设备属性值')

    # data = serializers.IntegerField(required=True)

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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        return attrs


class ApplydeviceSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)  # 公司ID
    project_id = serializers.IntegerField(required=True)  # 项目ID
    user_id = serializers.IntegerField(required=True)  # 操作人ID
    cd_name = serializers.CharField(required=True)  # 采集设备名称
    d_name = serializers.CharField(required=True)  # 设备名称
    d_GPS = serializers.CharField(required=False, allow_blank=True, )  # GPS信息
    d_produce_time = serializers.CharField(required=False, allow_blank=True, )  # 出厂日期
    d_manufacturer = serializers.CharField(required=False, allow_blank=True, )  # 设备制造商

    class Meta:
        model = Device
        fields = (
            'project_id', 'company_id', 'user_id', 'cd_name', 'd_name', 'd_GPS', 'd_produce_time', 'd_manufacturer')

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
                    Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 997, 'message': '您不是公司管理员，无权操作'})
        return attrs


class EditdeviceSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True)
    device_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    d_name = serializers.CharField(required=True)  # 设备名称
    d_GPS = serializers.CharField(required=False, allow_blank=True, )  # GPS信息
    d_produce_time = serializers.CharField(required=False, allow_blank=True, )  # 出厂日期
    d_manufacturer = serializers.CharField(required=False, allow_blank=True, )  # 设备制造商

    class Meta:
        model = Device
        fields = ('company_id', 'device_id', 'user_id', 'd_name', 'd_GPS', 'd_produce_time', 'd_manufacturer')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Device.objects.filter(id=attrs['device_id']):
            raise ValidationError(detail={'code': 992, 'message': '设备不存在或已停用'})
        device = Device.objects.get(id=attrs['device_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='公司管理员') | Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']).filter(
                    u_type='公司管理员'):
                if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=attrs['company_id']):
                    raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class PersonDevicelistSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Device
        fields = ('user_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        projects = user.project.all()
        company = user.u_company_id
        if not projects:
            raise ValidationError(detail={'code': 963, 'message': '您当前没有关联的设备'})
        devices = []
        for project in projects:
            d = Device.objects.filter(d_p_id=project).filter(d_active=1)
            if not d:
                continue
            devices.append(d)
        if not devices:
            raise ValidationError(detail={'code': 991, 'message': '项目暂无可用设备'})

        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=company).filter(
                    u_type='公司管理员'):
                if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=company):
                    raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class SigndeviceSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=False, help_text='公司id，非必填')
    cdevice_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)  # 操作人id，一般为公司管理员或平台工作人员
    operator_id = serializers.IntegerField(required=False, help_text='制定负责人的id，在关联设备功能时必填')  # 设备负责人id

    class Meta:
        model = Device
        fields = ('company_id', 'device_id', 'user_id', 'operator_id')

    def validate(self, attrs):
        if not Device.objects.filter(id=attrs['device_id']).filter(d_active=1):
            raise ValidationError(detail={'code': 992, 'message': '设备不存在或已停用'})
        device = Device.objects.get(id=attrs['device_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        company = user.u_company_id
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=company).filter(
                    Q(u_type='公司管理员') | Q(id=device.d_u_id)):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class DeleteDeviceSerializer(serializers.ModelSerializer):
    device_id = serializers.IntegerField(required=True)  # 采集设备ID
    user_id = serializers.IntegerField(required=True)  # 操作人id，一般为公司管理员或平台工作人员

    class Meta:
        model = Device
        fields = ('device_id', 'user_id',)

    def validate(self, attrs):
        if not Device.objects.filter(id=attrs['device_id']):
            raise ValidationError(detail={'code': 944, 'message': '机械设备不存在'})
        # device = Device.objects.get(id=attrs['device_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        company = user.u_company_id
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=company).filter(u_type='公司管理员'):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class ViewdataSerializer(serializers.ModelSerializer):
    cd_id = serializers.IntegerField(required=True)  # 采集设备ID
    user_id = serializers.IntegerField(required=True)  # 操作人id，一般为公司管理员或平台工作人员
    g_id = serializers.IntegerField(required=True)  # 组ID

    class Meta:
        model = Device
        fields = ('cd_id', 'user_id', 'g_id')

    def validate(self, attrs):
        if not Collectdevice.objects.filter(id=attrs['cd_id']):
            raise ValidationError(detail={'code': 946, 'message': '采集设备不存在'})
        # device = Device.objects.get(id=attrs['device_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        company = user.u_company_id
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=company).filter(u_type='公司管理员'):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


# 添加设备属性 需公司管理员操作
class AdddeviceattSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True, help_text='管理员id')
    device_id = serializers.CharField(required=True, help_text='设备id')
    dg_name = serializers.CharField(required=True, help_text='设备属性名')
    dg_type = serializers.CharField(required=True, help_text='设备属性类型')

    class Meta:
        model = DataGroup
        fields = ('device_id', 'dg_name', 'user_id', 'dg_type')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if DataGroup.objects.filter(dg_d_id_id=attrs['device_id'], dg_name=attrs['dg_name']):
            raise ValidationError(detail={'code': 930, 'message': '参数组名称重复'})
        if not LoginUser.objects.filter(
                Q(u_type='公司管理员') | Q(u_type='设备管理员') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


# 添加设备属性 需公司管理员操作
class AdddeviceattSerializerv2(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True, help_text='管理员id')
    d_id = serializers.CharField(required=True, help_text='设备id')
    ddd_name = serializers.CharField(required=True, help_text='设备属性名')
    ddd_detail = serializers.CharField(required=True, help_text='设备属性描述')

    class Meta:
        model = DataGroup
        fields = ('d_id', 'ddd_name', 'user_id', 'ddd_detail')

    def validate(self, attrs):
        if not Device.objects.get(id=attrs['d_id']):
            raise ValidationError(detail={'code': 944, 'message': '机械设备不存在'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(
                Q(u_type='公司管理员') | Q(u_type='设备管理员') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class DeldeviceSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True, help_text='管理员id')
    g_id = serializers.CharField(required=True, help_text='组id')

    # dg_name = serializers.CharField(required=True, help_text='设备属性名')

    class Meta:
        model = DataGroup
        fields = ('g_id', 'user_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(
                Q(u_type='公司管理员') | Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not DataGroup.objects.filter(id=attrs['g_id']):
            raise ValidationError(detail={'code': 945, 'message': '机械设备组不存在'})
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
    ddevice_id = serializers.CharField(required=True, help_text='设备属性id')

    class Meta:
        model = Devicedata
        fields = ('ddevice_id', 'user_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(Q(u_type='公司管理员') | Q(u_type='设备管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class DeviceGrouplistSerializer(serializers.ModelSerializer):
    device_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = DataGroup
        fields = ('device_id', 'user_id')

    def validate(self, attrs):
        if not Device.objects.filter(id=attrs["device_id"]):
            raise ValidationError(detail={'code': 944, 'message': '机械设备不存在'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        device = Device.objects.get(id=attrs["device_id"])
        company_id = device.d_co_id_id
        print(company_id)
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=company_id).filter(Q(
                    u_type='公司管理员') | Q(u_type='设备管理员')):
                # if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=company_id):
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
                    Q(u_type='公司管理员') | Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class AlertSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    alert_id = serializers.IntegerField(required=True)

    class Meta:
        model = Alert
        fields = ('user_id', 'alert_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        if not Alert.objects.filter(id=attrs['alert_id']):
            raise ValidationError(detail={'code': 937, 'message': '报警规则不存在'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=user.u_company_id).filter(
                    Q(u_type='公司管理员') | Q(u_type='设备管理员')):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class AlarmlistSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Alert
        fields = ('user_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        return attrs


class SearchAlarmlistSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True)
    start_time = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Alert
        fields = ('user_id', 'device_name')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        return attrs


class AddAlertSerializer(serializers.ModelSerializer):
    dg_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    a_highest_line = serializers.CharField(required=True, help_text='上告警线')
    a_highest_level = serializers.CharField(required=False, allow_blank=True, help_text='告警等级')
    a_highest_tip = serializers.CharField(required=False, allow_blank=True, help_text='告警提示')
    a_high_line = serializers.CharField(required=True, help_text='上预警线')
    a_high_level = serializers.CharField(required=False, allow_blank=True, help_text='预警等级')
    a_high_tip = serializers.CharField(required=False, allow_blank=True, help_text='过高提示')
    a_low_line = serializers.CharField(required=True, help_text='下预警线')
    a_low_level = serializers.CharField(required=False, allow_blank=True, help_text='过低等级')
    a_low_tip = serializers.CharField(required=False, allow_blank=True, help_text='过低提示')
    a_lowest_line = serializers.CharField(required=True, help_text='告警线')
    a_lowest_level = serializers.CharField(required=False, allow_blank=True, help_text='最低告警等级')
    a_lowest_tip = serializers.CharField(required=False, allow_blank=True, help_text='告警提示')

    class Meta:
        model = Alert
        fields = ('dg_id', 'user_id', 'a_highest_line', "a_highest_tip", 'a_high_line',
                  'a_high_tip', 'a_low_line', 'a_low_tip',
                  'a_lowest_line', 'a_lowest_tip', 'a_lowest_level', 'a_low_level', 'a_high_level', 'a_highest_level')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        if not DataGroup.objects.filter(id=attrs['dg_id']):
            raise ValidationError(detail={'code': 945, 'message': '机械设备组不存在'})
        if not Data.objects.filter(d_g_id=attrs['dg_id']):
            raise ValidationError(detail={'code': 940, 'message': '当前机械设备组未设置参数'})
        device = DataGroup.objects.get(id=attrs['dg_id'])
        device_id = device.dg_d_id_id
        if not Device.objects.filter(id=device_id):
            raise ValidationError(detail={'code': 944, 'message': '机械设备不存在'})
        c_id = device.dg_d_id.d_c_id_id
        if not Collectdevice.objects.filter(id=c_id):
            raise ValidationError(detail={'code': 946, 'message': '采集设备不存在'})
        p_id = device.dg_d_id.d_c_id.cd_p_id_id
        if not Project.objects.filter(id=p_id, p_active=1):
            raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        company_id = device.dg_d_id.d_co_id_id
        if not Company.objects.filter(id=company_id, active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=user.u_company_id).filter(
                    Q(u_type='公司管理员') | Q(u_type='设备管理员')):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class EditAlertSerializer(serializers.ModelSerializer):
    alert_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    a_highest_line = serializers.CharField(required=True, help_text='上告警线')
    a_highest_level = serializers.CharField(required=False, allow_blank=True, help_text='告警等级')
    a_highest_tip = serializers.CharField(required=False, allow_blank=True, help_text='告警提示')
    a_high_line = serializers.CharField(required=True, help_text='上预警线')
    a_high_level = serializers.CharField(required=False, allow_blank=True, help_text='预警等级')
    a_high_tip = serializers.CharField(required=False, allow_blank=True, help_text='过高提示')
    a_low_line = serializers.CharField(required=True, help_text='下预警线')
    a_low_level = serializers.CharField(required=False, allow_blank=True, help_text='过低等级')
    a_low_tip = serializers.CharField(required=False, allow_blank=True, help_text='过低提示')
    a_lowest_line = serializers.CharField(required=True, help_text='告警线')
    a_lowest_level = serializers.CharField(required=False, allow_blank=True, help_text='最低告警等级')
    a_lowest_tip = serializers.CharField(required=False, allow_blank=True, help_text='告警提示')

    class Meta:
        model = Alert
        fields = ('alert_id', 'user_id', 'a_highest_line', "a_highest_tip", 'a_high_line',
                  'a_high_tip', 'a_low_line', 'a_low_tip',
                  'a_lowest_line', 'a_lowest_tip', 'a_lowest_level', 'a_low_level', 'a_high_level', 'a_highest_level')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        if not Alert.objects.filter(id=attrs['alert_id']):
            raise ValidationError(detail={'code': 937, 'message': '报警规则不存在'})
        alert = Alert.objects.get(id=attrs['alert_id'])
        dg_id = alert.a_datagroup_id_id
        if not Data.objects.filter(d_g_id=dg_id):
            raise ValidationError(detail={'code': 940, 'message': '当前机械设备组未设置参数'})
        device = DataGroup.objects.get(id=dg_id)
        device_id = device.dg_d_id_id
        if not Device.objects.filter(id=device_id):
            raise ValidationError(detail={'code': 944, 'message': '机械设备不存在'})
        c_id = device.dg_d_id.d_c_id_id
        if not Collectdevice.objects.filter(id=c_id):
            raise ValidationError(detail={'code': 946, 'message': '采集设备不存在'})
        p_id = device.dg_d_id.d_c_id.cd_p_id_id
        if not Project.objects.filter(id=p_id, p_active=1):
            raise ValidationError(detail={'code': 995, 'message': '项目不存在或已被平台停用'})
        company_id = device.dg_d_id.d_co_id_id
        if not Company.objects.filter(id=company_id, active=1):
            raise ValidationError(detail={'code': 998, 'message': '公司不存在或已被平台停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_company_id=user.u_company_id).filter(
                    Q(u_type='公司管理员') | Q(u_type='设备管理员')):
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class AddmaintainrecordSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    d_id = serializers.IntegerField(required=True, help_text='设备id')
    dm_d_detail = serializers.CharField(required=False, allow_blank=True, help_text='维修记录详情')
    dm_name = serializers.CharField(required=False, allow_blank=True, help_text='维修记录名称')

    class Meta:
        model = Devicemaintainrecord
        fields = ('user_id', 'd_id', 'dm_d_detail', 'dm_name')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Device.objects.filter(id=attrs['d_id']).filter(d_active=1):
            raise ValidationError(detail={'code': 992, 'message': '设备不存在或已停用'})
        device = Device.objects.get(id=attrs['d_id'])
        d_u_id = device.d_u_id
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=d_u_id):
                if not LoginUser.objects.filter(Q(u_type='公司管理员') | Q(u_type='设备管理员')):
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=d_u_id):
                if not LoginUser.objects.filter(u_type='公司管理员'):
                    raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class CompanyMaintainrecordSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    company_id = serializers.IntegerField(required=True, help_text='公司id')

    class Meta:
        model = Devicemaintainrecord
        fields = ('user_id', 'company_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Devicemaintainrecord.objects.filter(dm_d_id__d_co_id=attrs['company_id']):
            raise ValidationError(detail={'code': 970, 'message': '维修记录不存在'})
        # device = Device.objects.get(id=attrs['dm_d_id'])
        # d_u_id = device.d_u_id
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(
        #         Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
        #     if not LoginUser.objects.filter(id=d_u_id):
        #         if not LoginUser.objects.filter(u_type='公司管理员'):
        #             raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            if not LoginUser.objects.filter(id=d_u_id):
                if not LoginUser.objects.filter(u_type='公司管理员'):
                    raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class AddworksheetSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    w_name = serializers.CharField(required=True, help_text='工单名称')
    w_type = serializers.CharField(required=True, help_text='工单类型，由用户自定义上传')
    w_u_phone = serializers.CharField(required=True, help_text='客户手机号')
    w_content = serializers.CharField(required=True, help_text='工单内容')

    # w_status = serializers.CharField(required=True, help_text='工单状态')

    class Meta:
        model = Worksheet
        fields = ('user_id', 'w_name', 'w_type', 'w_u_phone', 'w_content')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class SearhworksheetsSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    w_status = serializers.CharField(required=True)

    class Meta:
        model = LoginUser
        fields = ('user_id', 'w_status')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class EditworksheetSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    w_id = serializers.IntegerField(required=True, help_text='工单id')
    w_name = serializers.CharField(required=True, help_text='工单名称')
    w_u_phone = serializers.CharField(required=True, help_text='客户手机号')
    w_type = serializers.CharField(required=True, help_text='工单类型')
    w_content = serializers.CharField(required=True, help_text='工单详情')

    # w_status = serializers.CharField(required=True, help_text='工单状态')

    class Meta:
        model = Worksheet
        fields = ('user_id', 'w_name', 'w_id', 'w_type', 'w_u_phone', 'w_content')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not Worksheet.objects.filter(id=attrs['w_id']):
            raise ValidationError(detail={'code': 966, 'message': '工单不存在'})
        return attrs


class AddknowledgeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    k_title = serializers.CharField(required=True, help_text='文章标题')
    k_type = serializers.CharField(required=True, help_text='文章类型：知识库或行业资讯')
    k_content = serializers.CharField(required=True, help_text='文章内容')
    # k_tag = serializers.CharField(required=True, help_text='文章标签')
    k_condition = serializers.CharField(required=True, help_text="文章状态")  # 转载 编辑

    class Meta:
        model = Knowledge
        fields = ('user_id', 'k_title', 'k_type', 'k_content', 'k_condition')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class EditenterpriseSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    k_id = serializers.IntegerField(required=True, help_text='工单id')
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not Enterprise.objects.filter(id=attrs['k_id']):
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        return attrs


class DocSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    w_id = serializers.IntegerField(required=True, help_text='工单id')

    # print(e_image)
    class Meta:
        model = Doc
        fields = ('user_id', 'w_id')

    def validate(self, attrs):
        # print(attrs['w_id'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if Doc.objects.filter(w_id=attrs['w_id']):
            raise ValidationError(detail={'code': 959, 'message': '该工单已存在技术方案'})
        if not Worksheet.objects.filter(id=attrs['w_id']):
            raise ValidationError(detail={'code': 966, 'message': '工单不存在'})
        if Worksheet.objects.filter(id=attrs['w_id'], w_status='未完成'):
            raise ValidationError(detail={'code': 955, 'message': '该工单尚未完善，请勿上传解决方案'})
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(
        #         Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
        #     raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class DeleteDocSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    w_id = serializers.IntegerField(required=True, help_text='工单id')

    # print(e_image)
    class Meta:
        model = Doc
        fields = ('user_id', 'w_id')

    def validate(self, attrs):
        # print(attrs['e_image'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Doc.objects.filter(w_id=attrs['w_id']):
            raise ValidationError(detail={'code': 958, 'message': '该工单不存在技术方案'})
        if Doc.objects.filter(w_id=attrs['w_id'], doc_is_active=True):  # 若解决方案已激活，则必须超级管理员才可删除
            if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_type='超级管理员'):
                raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维顾问') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class UnactivetechlistSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')

    # print(e_image)
    class Meta:
        model = Doc
        fields = ('user_id',)

    def validate(self, attrs):
        # print(attrs['e_image'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        # if not Doc.objects.filter(w_id=attrs['w_id']):
        #     raise ValidationError(detail={'code': 958, 'message': '该工单不存在技术方案'})
        # if Doc.objects.filter(w_id=attrs['w_id'], doc_user_id=attrs['user_id'], doc_is_active=True):
        #     if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_type='客服运营'):
        #         raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_type='超级管理员'):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class ActiveDocSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    w_id = serializers.IntegerField(required=True, help_text='工单id')

    # print(e_image)
    class Meta:
        model = Doc
        fields = ('user_id', 'w_id')

    def validate(self, attrs):
        # print(attrs['e_image'])
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Doc.objects.filter(w_id=attrs['w_id']):
            raise ValidationError(detail={'code': 958, 'message': '该工单不存在技术方案'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


class ThumbknowledgeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    k_id = serializers.IntegerField(required=True, help_text='文章id')

    class Meta:
        model = Knowledge
        fields = ('user_id', 'k_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Knowledge.objects.filter(id=attrs['k_id']):
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        knowledge = Knowledge.objects.get(id=attrs['k_id'])
        if Thumbs.objects.filter(thu_user_id=attrs['user_id'], thu_k_id=knowledge):
            raise ValidationError(detail={'code': 960, 'message': '您已点过赞！'})
        return attrs


class CollectknowledgeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    k_id = serializers.IntegerField(required=True, help_text='文章id')

    class Meta:
        model = Knowledge
        fields = ('user_id', 'k_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Knowledge.objects.filter(id=attrs['k_id']):
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        knowledge = Knowledge.objects.get(id=attrs['k_id'])
        if knowledge.loginuser_set.filter(id=attrs['user_id'], knowledge=knowledge):
            raise ValidationError(detail={'code': 960, 'message': '您已收藏过此文章！'})
        return attrs


class UnCollectknowledgeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    k_id = serializers.IntegerField(required=True, help_text='文章id')

    class Meta:
        model = Knowledge
        fields = ('user_id', 'k_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not Knowledge.objects.filter(id=attrs['k_id']):
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        knowledge = Knowledge.objects.get(id=attrs['k_id'])
        if not knowledge.loginuser_set.filter(id=attrs['user_id'], knowledge=knowledge):
            raise ValidationError(detail={'code': 960, 'message': '您未收藏过此文章！'})
        return attrs


class ViewCollectionSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')

    class Meta:
        model = Knowledge
        fields = ('user_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        collection = user.knowledge.all()
        if not collection:
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        # if not Knowledge.objects.filter(id=attrs['k_id']):
        #     raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        # knowledge = Knowledge.objects.get(id=attrs['k_id'])
        # co = knowledge.loginuser_set.all(id=attrs['user_id'])
        # if not co:
        #     raise ValidationError(detail={'code': 960, 'message': '您未收藏过文章！'})
        return attrs


class ViewCollectionSerializerv1(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    key = serializers.CharField(required=True)

    class Meta:
        model = Knowledge
        fields = ('user_id', 'key')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        user = LoginUser.objects.get(id=attrs['user_id'])
        collection = user.knowledge.all()
        if not collection:
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        # if not Knowledge.objects.filter(id=attrs['k_id']):
        #     raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        # knowledge = Knowledge.objects.get(id=attrs['k_id'])
        # co = knowledge.loginuser_set.all(id=attrs['user_id'])
        # if not co:
        #     raise ValidationError(detail={'code': 960, 'message': '您未收藏过文章！'})
        return attrs


class EditknowledgeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    k_id = serializers.IntegerField(required=True, help_text='文章id')
    k_title = serializers.CharField(required=False, allow_blank=True, help_text='文章标题, 做删除操作时不用传值')
    k_content = serializers.CharField(required=False, allow_blank=True, help_text='文章内容, 做删除操作时不用传值')

    # k_tag = serializers.CharField(required=False, allow_blank=True, help_text='文章标签')

    class Meta:
        model = Knowledge
        fields = ('user_id', 'k_id', 'k_title', 'k_content')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not Knowledge.objects.filter(id=attrs['k_id']):
            raise ValidationError(detail={'code': 988, 'message': '数据不存在'})
        return attrs


class VerfiySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    k_id = serializers.IntegerField(required=True, help_text='文章id')
    k_verify = serializers.CharField(required=False, allow_blank=True, help_text='文章标题, 做删除操作时不用传值')

    # k_tag = serializers.CharField(required=False, allow_blank=True, help_text='文章标签')

    class Meta:
        model = Knowledge
        fields = ('user_id', 'k_id', 'k_verify')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_type='超级管理员'):
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        if not Knowledge.objects.filter(id=attrs['s_k_id']):
            raise ValidationError(detail={'code': 965, 'message': '文章不存在'})
        return attrs


class WisepasstokenSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True, help_text='用户id')

    class Meta:
        model = LoginUser
        fields = ('id',)

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
                Q(u_type='运营') | Q(u_type='运维') | Q(u_type='客服运营') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


# 超级管理员创建公司管理员
class ManagerCreateStaffSerializerv3(serializers.ModelSerializer):
    """
    超级管理员创建公司管理员
    """
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    staff_name = serializers.CharField(required=True, help_text='员工姓名')
    staff_phone = serializers.CharField(required=True, help_text='员工电话号码')
    staff_password = serializers.CharField(required=True, help_text='员工账号密码')

    class Meta:
        model = LoginUser
        fields = ('user_id', 'staff_name', 'staff_phone', 'staff_password')

    def validate(self, attrs):
        if LoginUser.objects.filter(phone_numbers=attrs['staff_phone']):
            raise ValidationError(detail={'code': 982, 'message': '手机号已注册'})
        if not re_phone(attrs['staff_phone']):
            raise ValidationError(detail={'code': 983, 'message': '手机号码格式错误'})
        if LoginUser.objects.filter(username=attrs['staff_name']):
            raise ValidationError(detail={'code': 980, 'message': '用户名已注册'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': '用户不存在或已停用'})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(u_type='超级管理员'):
            raise ValidationError(detail={'code': 996, 'message': '您无权进行此操作'})
        return attrs


# 添加配件
class AddFittingsSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    f_name = serializers.CharField(required=True, help_text='配件名')
    # f_picture = serializers.FileField(required=False, help_text='配件设备图片',)
    # f_parameter = serializers.ImageField(required=True, help_text='配件参数图片',)
    # f_introduce = serializers.ImageField(required=False, help_text='设备介绍图片',)

    f_subject = serializers.CharField(required=True, help_text='配件种类')
    f_number = serializers.CharField(required=True, help_text='产品编号')
    f_machine = serializers.CharField(required=True, help_text='机组编号')
    f_else = serializers.CharField(required=False, allow_blank=True, help_text='备注信息')

    class Meta:
        model = Fittings
        fields = ('user_id', 'f_name', 'f_subject', 'f_number', 'f_machine', 'f_else',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运维') | Q(u_type='公司管理员') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        if Fittings.objects.filter(f_name=attrs['f_name']):  # 可能这一条修改为同一类下的配件名不能重复更好
            raise ValidationError(detail={'code': 953, 'message': ['配件名已存在，请勿重复添加']})

        return attrs


# 修改配件
class ChangeFittingsSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    f_id = serializers.IntegerField(required=True, help_text='配件id')
    f_name = serializers.CharField(required=True, help_text='配件名')
    # f_picture = serializers.ImageField(required=True, help_text='配件设备图片',)
    # f_parameter = serializers.ImageField(required=True, help_text='配件参数图片',)
    # f_introduce = serializers.ImageField(required=False, help_text='设备介绍图片',)

    f_subject = serializers.CharField(required=True, help_text='配件种类')
    f_number = serializers.CharField(required=True, help_text='产品编号')
    f_machine = serializers.CharField(required=True, help_text='机组编号')
    f_else = serializers.CharField(required=False, help_text='备注信息')

    class Meta:
        model = Fittings
        fields = ('user_id', 'f_name', 'f_subject', 'f_number', 'f_machine', 'f_else', 'f_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运维') | Q(u_type='公司管理员') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        if not Fittings.objects.filter(id=attrs['f_id']):
            raise ValidationError(detail={'code': 992, 'message': ['设备不存在或已停用']})

        return attrs


# 删除配件
class DeleteFittingsSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    f_id = serializers.IntegerField(required=True, help_text='配件id')

    class Meta:
        model = Fittings
        fields = ('user_id', 'f_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运维') | Q(u_type='公司管理员') | Q(u_type="超级管理员")):
            raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        if not Fittings.objects.filter(id=attrs['f_id']):
            raise ValidationError(detail={'code': 992, 'message': ['设备不存在或已停用']})

        return attrs


# 查询配件
class SelectFittingsSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    f_id = serializers.IntegerField(required=True, help_text='配件id')

    class Meta:
        model = Fittings
        fields = ('user_id', 'f_id')

    def validate(self, attrs):
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
        #     raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not Fittings.objects.filter(id=attrs['f_id']):
            raise ValidationError(detail={'code': 992, 'message': ['设备不存在或已停用']})

        return attrs


# 根据配件类查询配件
class SelectFitAccSubSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    sub_id = serializers.IntegerField(required=True, help_text='配件类')

    class Meta:
        model = Fittings
        fields = ('user_id', 'sub_id')

    def validate(self, attrs):
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
        #     raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not FitSub.objects.get(id=attrs['sub_id']):
            raise ValidationError(detail={'code': 951, 'message': ['配件类型不存在']})
        if not Fittings.objects.filter(f_subject_id=attrs['sub_id']):
            raise ValidationError(detail={'code': 953, 'message': ['此配件类下目前没有配件']})

        return attrs


# 查询配件类
class SelectFitSubSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')

    class Meta:
        model = Fittings
        fields = ('user_id',)

    def validate(self, attrs):
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
        #     raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not FitSub.objects.all():
            raise ValidationError(detail={'code': 951, 'message': ['配件类型不存在']})
        return attrs


# 删除配件类
class DeleteFitSubSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    fs_id = serializers.IntegerField(required=True, help_text='配件类id')

    class Meta:
        model = Fittings
        fields = ('user_id', 'fs_id',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not FitSub.objects.filter(id=attrs["fs_id"]):
            raise ValidationError(detail={'code': 951, 'message': ['配件类型不存在']})
        return attrs


# 添加配件类
class AddFitSubSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    f_name = serializers.CharField(required=True, help_text='配件类名')

    class Meta:
        model = FitSub
        fields = ('user_id', 'f_name',)

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运维') | Q(u_type='公司管理员') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        if FitSub.objects.filter(fs_name=attrs['f_name']):
            raise ValidationError(detail={'code': 953, 'message': ['配件类名已存在，请勿重复添加']})

        return attrs


#  查询所有配件类与配件
class SelectAllFitSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')

    class Meta:
        model = FitSub
        fields = ('user_id',)

    def validate(self, attrs):
        pass


# 修改配件类信息
class FixFitSubSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    f_id = serializers.IntegerField(required=True, help_text='配件类id')
    f_name = serializers.CharField(required=True, help_text='配件名')

    # f_picture = serializers.ImageField(required=True, help_text='配件设备图片',)
    # f_parameter = serializers.ImageField(required=True, help_text='配件参数图片',)
    # f_introduce = serializers.ImageField(required=False, help_text='设备介绍图片',)

    class Meta:
        model = Fittings
        fields = ('user_id', 'f_name', 'f_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='运维') | Q(u_type='公司管理员') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        if not FitSub.objects.get(id=attrs['f_id']):
            raise ValidationError(detail={'code': 992, 'message': ['不存在此配件类']})

        return attrs




# 建立公告 发送公告
class SendAnnounceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    head = serializers.CharField(required=True, help_text='公告标题')
    a_content = serializers.CharField(required=True, help_text='公告')
    set_time = serializers.DateTimeField(required=False, help_text='通知发送时间')

    class Meta:
        model = Announce
        fields = ('user_id', 'head','a_content', 'set_time')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(
        #         Q(u_type='运维') | Q(u_type='超级管理员')):
        #     raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})

        return attrs


# 1 查询单个公告     2  所有人根据不同传参 查询到时保养提醒 系统公告
class SelectAnnounceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    a_id = serializers.CharField(required=True, help_text='公告id')

    class Meta:
        model = Announce
        fields = ('user_id', 'a_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(
        #         Q(u_type='运维') | Q(u_type='超级管理员')):
        #     raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        # if not Announce.objects.filter(id=attrs['a_id']):
        #     raise ValidationError(detail={'code': 943, 'message': ['公告不存在']})

        return attrs


# 查询所有公告
class SelectAllAnnounceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    # a_id = serializers.CharField(required=True, help_text='公告')
    keyword = serializers.CharField(required=False, allow_blank=True, help_text="标题关键字")

    class Meta:
        model = Announce
        fields = ('user_id', 'keyword' )

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='员工') | Q(u_type='公司管理员')| Q(u_type='设备管理员')):
            raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        if not Announce.objects.filter():
            raise ValidationError(detail={'code': 943, 'message': ['消息通知不存在']})

        return attrs


# 前台开启或者关闭定时任务
class AboutMessageSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    a_id = serializers.CharField(required=True, help_text='定时任务id')
    option = serializers.CharField(required=True, help_text="开关操作") # 0 ,1 0

    class Meta:
        model = Announce
        fields = ('user_id', 'option','a_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(
                Q(u_type='员工') | Q(u_type='公司管理员') | Q(u_type='设备管理员')):
            raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})


        return attrs


# 超级管理员 运维 查询所有公告
class ASelectAllAnnounceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    # number = serializers.IntegerField(required=True, help_text="用户选择传值") # 0 已发布的系统通知 1 所有的系统通知
    keyword = serializers.CharField(required=False, allow_blank=True, help_text='关键字') # 关键字搜索 关键字

    class Meta:
        model = Announce
        fields = ('user_id', 'keyword')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(Q(u_type='运维') | Q(u_type='超级管理员')):
            raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        if not Announce.objects.all():
            raise ValidationError(detail={'code': 943, 'message': ['公告不存在']})

        return attrs


# 删除单个公告
class DeleteAnnounceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    a_id = serializers.IntegerField(required=True, help_text='消息id')

    class Meta:
        model = Announce
        fields = ('user_id', 'a_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(
        #         Q(u_type='运维') | Q(u_type="超级管理员")):
        #     raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        if not Announce.objects.filter(id=attrs['a_id']):
            raise ValidationError(detail={'code': 941, 'message': ['公告已删除，不可重复删除']})

        return attrs


# 删除全部公告
class DeleteAllAnnounceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')

    class Meta:
        model = Announce
        fields = ('user_id', )

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(
        #         Q(u_type='运维') | Q(u_type="超级管理员")):
        #     raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        if not Announce.objects.all():
            raise ValidationError(detail={'code': 941, 'message': ['公告已删除，不可重复删除']})

        return attrs


# 普通用户一键已读全部公告
class ReadAllMessageSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')

    class Meta:
        model = Announce
        fields = ('user_id', )

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(
        #         Q(u_type='运维') | Q(u_type="超级管理员")):
        #     raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        user = LoginUser.objects.filter(id=attrs['user_id'])  # 获取用户
        announces = user.message.objects.filter(status=3)     # 获取已发送但未读的消息
        if not announces:
            raise ValidationError(detail={'code': 936, 'message': ['暂时无未读消息']})

        return attrs


# 建立公告 发送公告
class EditMessageSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    a_id = serializers.IntegerField(required=True, help_text='消息id')
    head = serializers.CharField(required=True, help_text='公告标题')
    a_content = serializers.CharField(required=True, help_text='公告')

    class Meta:
        model = Announce
        fields = ('user_id', 'head', 'a_content', )

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(
        #         Q(u_type='运维') | Q(u_type='超级管理员')):
        #     raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})

        return attrs


# 完成所有人更改自己发出的提醒公告
class EditMessageSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')
    a_id = serializers.IntegerField(required=True, help_text='消息id')
    head = serializers.CharField(required=True, help_text='公告标题')
    a_content = serializers.CharField(required=True, help_text='公告')
    set_time = serializers.DateTimeField(required=False, allow_null=True, help_text="提醒时间" )

    class Meta:
        model = Announce
        fields = ('user_id', 'head', 'a_content', 'a_id', 'set_time')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(
        #         Q(u_type='运维') | Q(u_type='超级管理员')):
        #     raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})

        return attrs


# 2  所有人根据不同传参 查询到时保养提醒 系统公告
class SelectMessageAloneSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, help_text='操作人id')

    c_id = serializers.IntegerField(required=True,help_text='用户选择') # 0 系统通知 1 定时通知

    class Meta:
        model = Announce
        fields = ('user_id',  'c_id')

    def validate(self, attrs):
        if not LoginUser.objects.filter(id=attrs['user_id']).filter(is_active=1):
            raise ValidationError(detail={'code': 999, 'message': ['用户不存在或已停用']})
        # if not LoginUser.objects.filter(id=attrs['user_id']).filter(
        #         Q(u_type='运维') | Q(u_type='超级管理员')):
        #     raise ValidationError(detail={'code': 996, 'message': ['您无权进行此操作']})
        # if not Announce.objects.filter(id=attrs['a_id']):
        #     raise ValidationError(detail={'code': 943, 'message': ['公告不存在']})

        return attrs