import redis
# 实现一个连接池
pool = redis.ConnectionPool(host='127.0.0.1')

r = redis.Redis(connection_pool=pool)
r.set('foo', 'bar')
if r.get('foo') != None:
    print(r.get('foo').decode())
r.delete('foo')
print(r.get('foo'))

keyname = "pika_redis_add_key"
r.set(keyname, str('1001;1002'))

pika_redis_value = r.get(keyname).decode()
msg_split = str(pika_redis_value).split(";", -1)
print("msg_split:", msg_split)

r.set('1001', 1)



if __name__ =="__main__":
    pass