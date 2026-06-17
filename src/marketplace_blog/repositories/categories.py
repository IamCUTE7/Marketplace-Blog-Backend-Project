from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace_blog.models.category import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_category(
        self,
        name: str,
    ) -> Category:
        category = Category(name=name)

        self.session.add(category)

        await self.session.flush()

        return category

    async def get_category_by_id(
        self,
        category_id: UUID,
    ) -> Category | None:
        query = select(Category).where(
            Category.category_id == category_id, Category.is_deleted.is_(False)
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def get_categories(
        self,
    ) -> list[Category]:
        query = select(Category).where(Category.is_deleted.is_(False))

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def update_category(
        self,
        category_id: UUID,
        **kwargs,
    ) -> UUID | None:
        query = (
            update(Category)
            .where(Category.category_id == category_id, Category.is_deleted.is_(False))
            .values(**kwargs)
            .returning(Category.category_id)
        )

        result = await self.session.execute(query)

        updated_category_id = result.scalar_one_or_none()

        await self.session.flush()

        return updated_category_id

    async def delete_category(
        self,
        category_id: UUID,
    ) -> UUID | None:
        query = (
            update(Category)
            .where(Category.category_id == category_id, Category.is_deleted.is_(False))
            .values(is_deleted=True)
            .returning(Category.category_id)
        )

        result = await self.session.execute(query)

        deleted_category_id = result.scalar_one_or_none()

        await self.session.flush()

        return deleted_category_id
