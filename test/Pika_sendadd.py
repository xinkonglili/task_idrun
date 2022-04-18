import asyncio
import aio_pika

async def main():
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/"
    )
    # 生成连接

    async with connection:
        routing_key = "test_queue"
        channel = await connection.channel()
        # 生成通道

        queue = await channel.declare_queue(routing_key, auto_delete=True)
        # 声明队列信息，避免队列不存在

        await channel.default_exchange.publish(
            aio_pika.Message(body="add:1002".encode()),
            routing_key=routing_key,
        )
        # 向指定队列发布消息

if __name__ == "__main__":
    asyncio.run(main())

