import uuid
import json
import threading
import logging
from django import http
from django.utils.deprecation import MiddlewareMixin
from rest_framework import response as rest_response

logger = logging.getLogger(__name__)
local = threading.local()    # 获取当前线程对象


class RequestLogFilter(logging.Filter):
    """
    日志过滤器，将当前请求线程的request信息保存到日志的record上下文
    record带有formater需要的信息。
    """
    def filter(self, record):
        try:
            record.request_id = getattr(local, 'request_id', None)
            record.name = record.name.split('.')[-1]
        except:
            pass
        return True


class WechatyApiMiddleware(MiddlewareMixin):

    def process_request(self, request, **kwargs):
        """ 该方法在请求到来的时候调用 请求参数写入日志 """

        local.request_id = str(uuid.uuid1())[:8]    # 线程对象里面加入uuid

        # 以下逻辑是 实现请求进来打印 相关请求参数
        body = request.body.decode()
        if body:
            try:
                body = json.loads(body)
            except:
                pass

        request_info = {
            'method': request.method,
            'path':  request.path_info,
            'params': request.GET.dict(),
            'body': body
        }

        logger.info(f'requests: {json.dumps(request_info, ensure_ascii=False)}')

    def process_response(self, request, response):
        """
        在执行完View函数准备将响应发到客户端前被执行 / 响应结果写入日志
        这里是打印 响应数据的日志，多加了几个 if 判断
        """
        path = request.path_info

        if isinstance(response, rest_response.Response) or isinstance(response, http.JsonResponse):
            if response.content and path not in filter_path:
                logger.info(f'response: {response.content.decode("utf-8")}')
        elif isinstance(response, http.HttpResponseNotFound):
            # 资源不存在
            error_data = {
                'status': 'error',
                'message': f'not found "{path}"'
            }
            logger.error(json.dumps(error_data, ensure_ascii=False))
            response = http.JsonResponse(data=error_data)
        else:
            # 未处理异常
            error_data = {
                'status': 'error',
                'message': '{0}'.format(str(response))
            }
            logger.error(json.dumps(error_data, ensure_ascii=False))
            response = http.JsonResponse(data=error_data)
        return response