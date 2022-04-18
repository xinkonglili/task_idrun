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
                    taskID = message_contents.split(' ',1)
                    print(int(taskID[0]))
                    # 获取消息
                    url = "http://127.0.0.1:8000/add/" + taskID[0]
                    http_get(url)

if __name__ == "__main__":
    asyncio.run(start_aio_pika())
