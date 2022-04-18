import asyncio
import aio_pika

import urllib.request

def http_get(url):
    response = urllib.request.urlopen(url)
    res_Content = response.read()

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
                    message_contents = message.body.decode()
                    msg_content = message_contents.split(' ', 1)

                    msg_split = message_contents.split(':', 1)
                    msg_type = msg_split[0]
                    msg_param = msg_split[1]
                    print(" msg_type: ", msg_type)
                    print(" msg_param: ",  msg_param)
                    send_url = ""
                    if msg_type == "add":
                        send_url = "http://127.0.0.1:8000/add/" + msg_param
                    elif msg_type == "setstatus":
                        send_url = "http://127.0.0.1:8000/setstatus/" + msg_param

                    http_get(send_url)

if __name__ == "__main__":
    asyncio.run(start_aio_pika())
