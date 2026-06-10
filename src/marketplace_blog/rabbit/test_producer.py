import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from marketplace_blog.rabbit.producer import send_message


async def main():
    await send_message("Hello RabbitMQ")


asyncio.run(main())
