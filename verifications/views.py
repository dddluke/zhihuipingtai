import random
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http

from verifications.libs.captcha.captcha import captcha
from verifications.libs.yuntongxun.ccp_sms import CCP
from celery_tasks.sms.tasks import send_sms_code


class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):
        """
        :param mobile: 手机号
        :return: JSON
        """
        # 接收参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        print(uuid)
        # 校验参数
        if not all([mobile, image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 创建链接到redis的对象
        redis_conn = get_redis_connection('verify_code')

        # 判断用户是否频繁发送短信验证码
        # 提取发送短信验证码的标记
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        if send_flag:
            return http.JsonResponse({'code': 971, 'errmsg': '发送短信过于频繁'})

        # 提取图形验证码
        uuid = 'img_' + uuid
        image_code_server = redis_conn.get(uuid)
        if image_code_server is None:
            return http.JsonResponse({'code': 972, 'errmsg': '图形验证码已失效'})
        # 删除图形验证码
        redis_conn.delete(uuid)
        # 对比图形验证码
        image_code_server = image_code_server.decode()  # 将bytes转字符串 再比较
        if image_code_client.lower() != image_code_server.lower():  # 转小写 再比较
            return http.JsonResponse({'code': 972, 'errmsg': '图形验证码输入错误'})

        # 生成短信验证码：随机6位数字，000007
        sms_code = '%06d' % random.randint(0, 999999)
        print(sms_code)

        # # 保存短信验证码
        # redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        #
        # # 保存发送短信验证码的标记
        # redis_conn.setex('send_flag_%s' % mobile, 60, 1)

        # 创建redis管道
        pl = redis_conn.pipeline()

        # 将命令添加到队列中
        # 保存短信验证码
        pl.setex('sms_%s' % mobile, 300, sms_code)
        # 保存发送短信验证码的标记
        pl.setex('send_flag_%s' % mobile, 60, 1)

        # 执行
        pl.execute()

        # # 发送短信验证码
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # 使用celery发送短信验证码
        # send_sms_code(mobile,sms_code) # 错误写法
        send_sms_code.delay(mobile, sms_code)  # 千万不要忘记写delay

        # 响应结果
        return http.JsonResponse({'code': 200, 'msg': '发送短信成功', 'getCode': sms_code})


class ImageCodeView(View):
    """
    图形验证码
    """
    def get(self, request, uuid):
        """
        :param request:
        :param uuid:通用唯一识别码 用于唯一标识该图形验证码属于哪个用户
        :return:image/jpg
        """
        # 实现主体业务逻辑：生成，保存，响应图片验证码

        # 生成图形验证码
        text, image = captcha.generate_captcha()
        print(text)
        # 保存图形验证码
        redis_conn = get_redis_connection('verify_code')
        # pl = redis_conn.pipeline()
        # 设置生存时间 redis_conn.setex('key','expire','value')
        redis_conn.setex(uuid, 300, text)
        # pl.execute()
        # 响应图形验证码 http.HttpResponse('响应体', '数据类型')
        return http.HttpResponse(image, content_type='image/jpg')

    # def get(self, request, uuid):
    #     """
    #     :param uuid:通用唯一识别码 用于唯一标识该图形验证码属于哪个用户
    #     :return:image/jpg
    #     """
    #     # 实现主题业务逻辑：生成，保存，响应图片验证码
    #     print(uuid)
    #     # 生成图形验证码
    #     text, image = captcha.generate_captcha()
    #
    #     # 保存图形验证码
    #     redis_conn = get_redis_connection('verify_code')
    #     # 设置生存时间 redis_conn.setex('key','expire','value')
    #     redis_conn.setex('img_%s' % uuid, '300', 'text')
    #
    #     # 响应图形验证码 http.HttpResponse('响应体', '数据类型')
    #     return http.HttpResponse(image, content_type='image/jpg')
