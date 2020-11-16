"""
ASGI config for test1 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
from .websocket import websocket_applicaiton
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test1.settings')

http_application = get_asgi_application()


async def application(scope, receive, send):
    print('scope:', scope)
    if scope['type'] == 'http':
        await http_application(scope, receive, send)
    elif scope['type'] == 'websocket':
        await websocket_applicaiton(scope, receive, send)
    else:
        raise Exception('UNKOWN SCOPE TYPE, ' + scope['type'])
