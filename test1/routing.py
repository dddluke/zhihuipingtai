from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from One.consumers import ChatConsumer

application = ProtocolTypeRouter({
    # 'websocket':AuthMiddlewareStack(  #认证
    #     URLRouter([
    #             path('ws/<str:username>/',ChatConsumer)  #相当于urls.py的作用，给这个websocket请求相应的Consumer处理
    #         ])
    #     )

})
