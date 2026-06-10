# import asyncio
# from marketplace_blog.core.config import Settings
# import aio_pika

# settings = Settings()
# print(settings.rabbitmq_url)

# async def main():
#     connection = await aio_pika.connect(
#         settings.rabbitmq_url,
#         timeout=5,
#     )
#     print("CONNECTED")
#     await connection.close()


# asyncio.run(main())

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import aio_pika


async def main():
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1:5672/",
        timeout=5,
    )
    print("CONNECTED")
    await connection.close()


asyncio.run(main())
