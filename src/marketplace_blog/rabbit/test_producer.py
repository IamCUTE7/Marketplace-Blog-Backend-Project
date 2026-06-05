import asyncio

from marketplace_blog.rabbit.producer import (
    send_message,
)


async def main():
    await send_message("Hello RabbitMQ")


asyncio.run(main())
