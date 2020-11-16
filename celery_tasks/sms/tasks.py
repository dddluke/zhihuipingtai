# 定义任务
from celery_tasks.main import celery_app
from celery_tasks.sms.yuntongxun.ccp_sms import CCP


# 使用装饰器装饰异步任务，保证celery识别任务
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """
    发送短信验证码的任务
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return:成功 200 失败 404
    """
    send_ret = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    return send_ret