import aio_pika
from loguru import logger

from marketplace_blog.rabbit.connection import get_connection


async def send_message(message: str):
    connection = await get_connection()

    async with connection:
        channel = await connection.channel()

        queue = await channel.declare_queue("user_events", durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()), routing_key=queue.name
        )

        logger.info("Published message to queue {}", queue.name, message)
