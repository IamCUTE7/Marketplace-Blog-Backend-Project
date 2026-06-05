from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace_blog.db.session import get_db
from marketplace_blog.repositories.categories import CategoryRepository
from marketplace_blog.schemas.category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
)

router = APIRouter()


@router.get("/", response_model=list[CategoryRead])
async def get_categories(db: AsyncSession = Depends(get_db)):
    category_repo = CategoryRepository(db)

    categories = await category_repo.get_categories()

    return [CategoryRead.model_validate(category) for category in categories]


@router.post("/", response_model=CategoryRead, status_code=201)
async def create_category(body: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category_repo = CategoryRepository(db)

    try:
        category = await category_repo.create_category(name=body.name)

        await db.commit()

        logger.info("Category '{}' created", category.name)

    except IntegrityError as err:
        await db.rollback()

        raise HTTPException(status_code=409, detail="Category already exists") from err

    return CategoryRead.model_validate(category)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    category_repo = CategoryRepository(db)

    category = await category_repo.get_category_by_id(category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail=f"Category with id={category_id} not found",
        )

    return CategoryRead.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    body: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    category_repo = CategoryRepository(db)

    updated_data = body.model_dump(exclude_none=True)

    try:
        updated_category_id = await category_repo.update_category(
            category_id=category_id,
            **updated_data,
        )

        if updated_category_id is None:
            raise HTTPException(
                status_code=404,
                detail=f"Category with id={category_id} not found",
            )

        await db.commit()

        logger.info("Category with id={} was updated", updated_category_id)

    except IntegrityError as err:
        await db.rollback()

        raise HTTPException(status_code=409, detail="Category already exists") from err

    category = await category_repo.get_category_by_id(updated_category_id)

    return CategoryRead.model_validate(category)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    category_repo = CategoryRepository(db)

    deleted_category_id = await category_repo.delete_category(
        category_id=category_id,
    )

    if deleted_category_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Category with id={category_id} not found",
        )

    await db.commit()

    logger.info("Category with id={} was deleted", delete_category)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
