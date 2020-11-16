# # 保存图形验证码
# from django_redis import get_redis_connection
#
# redis_conn = get_redis_connection('verify_code')
# # 设置生存时间 redis_conn.setex('key','expire','value')
# redis_conn.setex('a', 300, 'text')

import redis

if __name__=="__main__":
    try:
        rs = redis.Redis()
    except Exception as e:
        print(e)
    result = rs.set("name","itcast")
    print(result)
    # 获取
    name = rs.get("name")
    print(name)

