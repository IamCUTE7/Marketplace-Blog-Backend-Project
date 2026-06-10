import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace_blog.api.routes.login import get_current_user_from_token
from marketplace_blog.db.session import get_db
from marketplace_blog.rabbit.producer import send_message
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

    try:
        user = await service.create_user(body)

        await send_message(
            json.dumps(
                {
                    "event": "user_registered",
                    "user_id": str(user.user_id),
                    "email": user.email,
                    "name": user.name,
                }
            )
        )

        await db.commit()

        logger.info("User {} created", user.email)

    except IntegrityError as error:
        await db.rollback()
        service.handle_integrity_error(error)

    return UserRead.model_validate(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_from_token),
):
    service = UserService(db)

    try:
        deleted_user_id = await service.delete_user(user_id)

        if deleted_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={user_id} not found",
            )

        await db.commit()

        logger.info("User with id={} was deleted", user_id)

    except IntegrityError as error:
        await db.rollback()
        service.handle_integrity_error(error)

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

    try:
        updated_user_id = await service.update_user(user_id, **updated_data)

        if updated_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={user_id} not found",
            )

        await db.commit()

        logger.info("User with id={} was updated", user_id)

    except IntegrityError as error:
        await db.rollback()
        service.handle_integrity_error(error)

    updated_user = await service.get_user_by_id(updated_user_id)

    return UserRead.model_validate(updated_user)
