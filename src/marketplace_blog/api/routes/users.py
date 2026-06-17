from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace_blog.api.routes.login import get_current_user_from_token
from marketplace_blog.db.session import get_db
from marketplace_blog.schemas.user import UserCreate, UserRead, UserUpdate
from marketplace_blog.services.users import UserService

router = APIRouter()


@router.get("/{user_id}", status_code=200)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_from_token),
) -> UserRead:
    service = UserService(db)

    user = await service.get_user_by_id(user_id=user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found",
        )

    return UserRead.model_validate(user)


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    service = UserService(db)

    user = await service.create_user(body)

    return UserRead.model_validate(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_from_token),
):
    service = UserService(db)

    deleted_user_id = await service.delete_user(user_id)

    if deleted_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_from_token),
) -> UserRead:
    service = UserService(db)

    updated_data = body.model_dump(exclude_none=True)

    updated_user = await service.update_user(user_id, **updated_data)

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found",
        )

    return UserRead.model_validate(updated_user)
