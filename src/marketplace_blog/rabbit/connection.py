import sys

if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import aio_pika
from loguru import logger

from marketplace_blog.core.config import get_settings

settings = get_settings()


async def get_connection(s):
    logger.info("Connecting to RabbitMQ")

    connection = await aio_pika.connect_robust(settings.rabbitmq_url, timeout=5)

    logger.info("RabbitMQ connection established")

    return connection
