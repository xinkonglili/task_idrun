import redis
# 实现一个连接池
pool = redis.ConnectionPool(host='127.0.0.1')

r = redis.Redis(connection_pool=pool)
r.set('foo', 'bar')
if r.get('foo') != None:
    print(r.get('foo').decode())
r.delete('foo')
print(r.get('foo'))
if __name__ =="__main__":
    pass