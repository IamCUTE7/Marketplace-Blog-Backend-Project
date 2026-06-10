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
        return await self.post_repo.create_post(title, content, author_id, category_id)

    async def update_post(self, post_id, **kwaargs):
        return await self.post_repo.update_post(post_id, **kwaargs)

    async def delete_post(self, post_id):
        return await self.post_repo.delete_post(post_id)
