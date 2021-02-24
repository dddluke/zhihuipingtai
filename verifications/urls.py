from django.conf.urls import url

from verifications.views import *

urlpatterns = [
    # 图形验证码
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', ImageCodeView.as_view()),
    # 短信验证码  校验手机号，手机号正确进入视图
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', SMSCodeView.as_view()),
    url(r'^sms_codes1/(?P<mobile>1[3-9]\d{9})/$', SMSCode.as_view())
]
