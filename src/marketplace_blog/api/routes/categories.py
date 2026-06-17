from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace_blog.db.session import get_db
from marketplace_blog.schemas.category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
)
from marketplace_blog.services.categories import CategoryService

router = APIRouter()


@router.get("/", response_model=list[CategoryRead])
async def get_categories(db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)

    categories = await service.get_categories()

    return [CategoryRead.model_validate(category) for category in categories]


@router.post("/", response_model=CategoryRead, status_code=201)
async def create_category(body: CategoryCreate, db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)

    category = await service.create_category(body)

    return CategoryRead.model_validate(category)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)

    category = await service.get_category_by_id(category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id={category_id} not found",
        )

    return CategoryRead.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    body: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)

    updated_data = body.model_dump(exclude_none=True)

    updated_category_id = await service.update_category(
        category_id=category_id,
        **updated_data,
    )

    if updated_category_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id={category_id} not found",
        )

    category = await service.get_category_by_id(updated_category_id)

    return CategoryRead.model_validate(category)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)

    deleted_category_id = await service.delete_category(
        category_id=category_id,
    )

    if deleted_category_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id={category_id} not found",
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
