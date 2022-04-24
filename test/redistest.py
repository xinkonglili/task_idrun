import redis
# 实现一个连接池
pool = redis.ConnectionPool(host='127.0.0.1')

r = redis.Redis(connection_pool=pool)
r.set('foo', 'bar')
if r.get('foo') != "None":
    print(r.get('foo').decode())
r.delete('foo')
print(r.get('foo'))

keyname = "pika_redis_add_key"
r.delete(keyname)
r.rpush(keyname, 1003, 1004)
print(r.lrange(keyname,0,-1))

key_vals = r.lrange(keyname, 0, -1)
for index in range(len(key_vals)):
    print(key_vals[index].decode())

#r.rpush(keyname, str('1001;1002'))

#r.set('1001', 1)
if __name__ =="__main__":
    pass