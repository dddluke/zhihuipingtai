# from One import models
# from .models import *
import re
import urllib
CONNECTIONS = {}

async def websocket_applicaiton(scope, receive, send):
    while True:
        event = await receive()
        print('[event]', event)
        # 接收websocket链接消息
        if event['type'] == 'websocket.connect':
            await send({'type': 'websocket.accept'})
            # 得到auth
            query_string = scope.get('query_string').decode()
            auth = query_string.split('=')[1]

            # 记录send对象
            CONNECTIONS[auth] = send
        # 接收断开消息
        elif event['type'] == 'websocket.disconnect':
            break

        # elif event['type'] == 'websocket.receive':
        #     if event['text'] == '在吗':
        #         await send({
        #             'type': 'websocket.send',
        #             'text': '不在'
        #         })
        elif event['type'] == 'websocket.receive':
                if event['text'] == '在吗':
                    await send({
                        'type': 'websocket.send',
                        'text': '不在'
                    })

                else:
                    await send({
                            'type': 'websocket.send',
                            'text': '聊天功能目前维护中，联系客服请加微信：pcl75456'
                        })
        # 消息
        else:
            await send({
                'type': 'websocket.send',
                'text': '聊天功能目前开发中，请加客服微信：pcl75456'
            })

    print('[disconnect]')