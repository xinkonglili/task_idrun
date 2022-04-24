import asyncio
import redis
import aio_pika
import urllib.request
from threading import Thread
from requests import get, post


request_methods = {
    'get': get,
    'post': post,
}

Redis_taskAdd_keyname = "pika_redis_add_key"
Fastapi_taskAdd_url = "http://127.0.0.1:8000/add/"
Fastapi_taskStatus_url = "http://127.0.0.1:8000/setstatus/"

def sync_http_get(url):
    response = urllib.request.urlopen(url)
    res_content = response.read()
    print("响应内容---->：", res_content)

def async_http_get(method, *args, callback=None, timeout=15, **kwargs):
    method = request_methods[method.lower()]
    '''
    if callback:
        def callback_with_args(response, *args, **kwargs):
            callback(response)
        kwargs['hooks'] = {'response': callback_with_args} '''

    kwargs['timeout'] = timeout
    thread = Thread(target=method, args=args, kwargs=kwargs)
    thread.start()

def use_http_send(msg_type, msg_param):
    if msg_type == "add":
        send_url = Fastapi_taskAdd_url + msg_param
    elif msg_type == "setstatus":
        send_url = Fastapi_taskStatus_url + msg_param
    sync_http_get(send_url)

    ''' 耗时：10.492367029190063
    print("sync_http_get:", finish_sync_time - begin_sync_time)
    begin_async_time = time.time()
    finish_async_time = time.time()
    # 耗时：0.0009777545928955078
    print("async_http_get:", finish_async_time - begin_async_time) '''

def use_redis_send(msg_type, msg_param):
    # 实现一个连接池
    pool = redis.ConnectionPool(host='127.0.0.1')
    r = redis.Redis(connection_pool=pool)
    if msg_type == "add":
        r.rpush(Redis_taskAdd_keyname, msg_param)
    elif msg_type == "setstatus":
        msg_split = msg_param.split("=", 1)
        taskid_key = msg_split[0]
        taskid_value = msg_split[1]
        r.set(taskid_key, int(taskid_value))

# 建立连接
async def start_aio_pika():
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/"
    )
    queue_name = "test_queue"
    async with connection:
        # 上下文管理，退出时自动关闭connection
        channel = await connection.channel()
        # 创建channel
        # Declaring queue
        queue = await channel.declare_queue(queue_name, auto_delete=True)
        # auto_delete 通道关闭时是否删除队列
        # 声明队列
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print(message.body)
                    msg_split = message.body.decode().split(':', 1)
                    msg_type = msg_split[0]
                    msg_param = msg_split[1]
                    print(" msg_type: ", msg_type)
                    print(" msg_param: ",  msg_param)
                    use_http_send(msg_type, msg_param)
                    use_redis_send(msg_type, msg_param)
if __name__ == "__main__":
    asyncio.run(start_aio_pika())
