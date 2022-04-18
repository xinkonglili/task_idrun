import asyncio
import pika_server

def main():
    asyncio.run(pika_server.start_aio_pika())


if __name__ == "__main__":
    main()