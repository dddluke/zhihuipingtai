import os
import json
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import *

def index(request):

    return render(request, 'index.html')

# def login(request):
#     try:
#         if request.method != 'POST':
#             raise Exception('无效请求')
#
#         # 获取数据
#         data = request.body.decode()
#
#         data = json.loads(data)
#         username = data.get('username', '')
#         if username == '':
#             raise Exception('缺少必要参数')
#
#         # 数据验证，返回auth
#         auth = username
#         return JsonResponse({'code': 200, 'auth': auth})
#     except Exception as e:
#         return JsonResponse({'code': 0, 'message': str(e)})

# def blogin(request):
#     try:
#         if request.method != 'POST':
#             raise Exception('无效请求')
#
#         # 获取数据
#         data = request.body.decode()
#
#         data = json.loads(data)
#         # data = {'data': data}
#         # print(data)
#         username = data.get('username', '')
#         if username == '':
#             raise Exception('缺少必要参数')
#
#         # 数据验证，返回auth
#         auth = username
#         return JsonResponse({'code': 200, 'auth': auth})
#     except Exception as e:
#         return JsonResponse({'code': 0, 'message': str(e)})

#  用户登录
# class LoginView(GenericAPIView):
#     authentication_classes = []
#     permission_classes = []
#     serializer_class = LoginSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = LoginUser.objects.get(
#                 Q(username=serializer.data['ph']) | Q(phone_numbers=serializer.data['ph']) | Q(
#                     email=serializer.data['ph']))
#             # for user in users:
#             #     jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
#             #     jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
#             #     # 往添加token的数据
#             #     payload = jwt_payload_handler(user=user)  # 这里需要修改为自己的数据
#             #     # 生成对token进行加密
#             #     token = jwt_encode_handler(payload)
#             #     UserToken.objects.update_or_create(user=user, defaults={'token': token})
#             # user_id = user.id
#             # loginuser = LoginUser.objects.get(id=user.id)
#             # user_id = loginuser.id
#             # response = {
#             #     'message': ['登录成功'],
#             #     'code': ["200"]
#             #     'user_id': [user_id],
#             #     # 'token':token
#             #     # 'loginuser': loginuser,
#             #     # 'user_username': loginuser.username,
#             #     # 'user_id': [loginuser.id],
#             # }
#             # return Response(response, status=200)
#             objJson = serialize("json", LoginUser.objects.filter(id=user.id))
#             objStr = json.loads(objJson)
#             response_data = {'code': ["200"], 'data': objStr}
#             return HttpResponse(json.dumps(response_data))
#         return Response(serializer.errors, status=200)
