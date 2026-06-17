import asyncio
import json

from loguru import logger

from marketplace_blog.rabbit.connection import get_connection


async def consume():
    print("start")
    connection = await get_connection()
    print("connected")

    channel = await connection.channel()

    queue = await channel.declare_queue("user_events", durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                payload = json.loads(message.body.decode())

                event = payload["event"]

                if event == "user_registered":
                    print("Registration email successfully sent")
                    logger.info("Registration email sent to {}", payload["email"])

                elif event == "post_created":
                    logger.info("Post created: {}", payload["post_id"])

                elif event == "post_updated":
                    logger.info("Post updated: {}", payload["post_id"])

                elif event == "post_deleted":
                    logger.info("Post deleted: {}", payload["post_id"])


if __name__ == "__main__":
    asyncio.run(consume())
