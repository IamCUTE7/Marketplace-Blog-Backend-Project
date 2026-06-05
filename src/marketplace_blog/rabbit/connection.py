import aio_pika
from loguru import logger

from marketplace_blog.core.config import get_settings

settings = get_settings()


async def get_connection():
    logger.info("Connecting to RabbitMQ")

    connection = await aio_pika.connect(settings.rabbitmq_url, timeout=5)

    logger.info("RabbitMQ connection established")

    return connection
