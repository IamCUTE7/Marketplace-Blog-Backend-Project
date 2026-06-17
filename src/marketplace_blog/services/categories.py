from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy.exc import IntegrityError

from marketplace_blog.repositories.categories import CategoryRepository


class CategoryService:
    def __init__(self, db):
        self.category_repo = CategoryRepository(db)

    async def get_category_by_id(self, category_id):
        return await self.category_repo.get_category_by_id(category_id)

    async def get_categories(self):
        return await self.category_repo.get_categories()

    async def create_category(self, body):
        try:
            category = await self.category_repo.create_category(body.name)

            await self.category_repo.session.commit()

            return category

        except IntegrityError as err:
            await self.category_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Category already exists"
            ) from err

    async def update_category(self, category_id, **kwargs):
        try:
            updated_category_id = await self.category_repo.update_category(
                category_id=category_id,
                **kwargs,
            )

            if updated_category_id is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with id={category_id} not found",
                )

            await self.category_repo.session.commit()

            logger.info("Category with id={} was updated", updated_category_id)

            return updated_category_id

        except IntegrityError as err:
            await self.category_repo.session.rollback()

            raise HTTPException(
                status_code=409, detail="Category already exists"
            ) from err

    async def delete_category(self, category_id):
        deleted_category_id = await self.category_repo.delete_category(
            category_id=category_id,
        )

        if deleted_category_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id={category_id} not found",
            )

        await self.category_repo.session.commit()

        logger.info("Category with id={} was deleted", deleted_category_id)

        return deleted_category_id
