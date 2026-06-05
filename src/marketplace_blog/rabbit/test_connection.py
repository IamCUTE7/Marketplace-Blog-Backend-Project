import asyncio

import aio_pika


async def main():
    connection = await aio_pika.connect(
        "amqp://bloguser:blogpass@127.0.0.1:5672/%2F",
        timeout=5,
    )
    print("CONNECTED")
    await connection.close()


asyncio.run(main())
