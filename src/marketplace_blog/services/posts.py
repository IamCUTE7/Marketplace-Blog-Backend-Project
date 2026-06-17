import json

from loguru import logger

from marketplace_blog.rabbit.producer import send_message
from marketplace_blog.repositories.posts import PostRepository


class PostService:
    def __init__(self, db):
        self.post_repo = PostRepository(db)

    async def get_post_by_id(self, post_id):
        return await self.post_repo.get_post_by_id(post_id)

    async def get_posts(self, page_number, page_size, category_id, search):
        return await self.post_repo.get_posts(
            page_number, page_size, category_id, search
        )

    async def create_post(self, title, content, author_id, category_id):
        post = await self.post_repo.create_post(
            title=title,
            content=content,
            author_id=author_id,
            category_id=category_id,
        )
        await self.post_repo.session.commit()

        logger.info("Post {} was created", post.title)

        await send_message(
            json.dumps(
                {
                    "event": "post_created",
                    "post_id": str(post.post_id),
                    "title": post.title,
                }
            )
        )
        return post

    async def update_post(self, post_id, **kwargs):
        updated_post_id = await self.post_repo.update_post(post_id=post_id, **kwargs)

        if updated_post_id is None:
            return None

        await self.post_repo.session.commit()

        logger.info("Post with id={} was updated", updated_post_id)

        await send_message(
            json.dumps({"event": "post_updated", "post_id": str(updated_post_id)})
        )

        updated_post = await self.post_repo.get_post_by_id(updated_post_id)

        return updated_post

    async def delete_post(self, post_id):
        deleted_post_id = await self.post_repo.delete_post(post_id=post_id)

        if deleted_post_id is None:
            return None

        await self.post_repo.session.commit()

        logger.info("Post with id={} was deleted", deleted_post_id)

        await send_message(
            json.dumps({"event": "post_deleted", "post_id": str(deleted_post_id)})
        )

        return deleted_post_id
