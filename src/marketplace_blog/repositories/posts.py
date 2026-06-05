from uuid import UUID

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace_blog.models.post import Post


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(
        self, title: str, content: str, author_id: UUID, category_id: UUID
    ) -> Post:
        post = Post(
            title=title, content=content, author_id=author_id, category_id=category_id
        )

        self.session.add(post)

        await self.session.flush()

        return post

    async def get_post_by_id(self, post_id: UUID) -> Post:
        query = select(Post).where(Post.post_id == post_id, Post.is_deleted.is_(False))

        result = await self.session.execute(query)

        post = result.scalar_one_or_none()

        return post

    async def update_post(self, post_id: UUID, **kwargs) -> UUID | None:
        query = (
            update(Post)
            .where(Post.post_id == post_id, Post.is_deleted.is_(False))
            .values(**kwargs)
            .returning(Post.post_id)
        )

        result = await self.session.execute(query)

        updated_post_id = result.scalar_one_or_none()

        return updated_post_id

    async def delete_post(self, post_id: UUID) -> UUID | None:
        query = (
            update(Post)
            .where(Post.post_id == post_id, Post.is_deleted.is_(False))
            .values(is_deleted=True)
            .returning(Post.post_id)
        )

        result = await self.session.execute(query)

        deleted_post_id = result.scalar_one_or_none()

        await self.session.flush()

        return deleted_post_id

    async def get_posts(
        self,
        page_number: int,
        page_size: int,
        category_id: UUID | None = None,
        search: str | None = None,
    ) -> list[Post]:
        query = select(Post).where(Post.is_deleted.is_(False))

        if category_id is not None:
            query = query.where(Post.category_id == category_id)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Post.title.ilike(search_pattern), Post.content.ilike(search_pattern)
                )
            )

        query = query.order_by(Post.created_at.desc())

        query = query.offset((page_number - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)

        return list(result.scalars().all())
