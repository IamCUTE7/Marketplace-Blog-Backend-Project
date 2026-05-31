from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace_blog.api.routes.login import get_current_user_from_token
from marketplace_blog.core.hashing import Hasher
from marketplace_blog.db.session import get_db
from marketplace_blog.repositories.users import UserRepository
from marketplace_blog.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.get("/{user_id}", status_code=200)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_from_token),
) -> UserRead:
    user_repo = UserRepository(db)

    user = await user_repo.get_user_by_id(user_id=user_id)

    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id={user_id} not found")

    return UserRead.model_validate(user)


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    user_repo = UserRepository(db)

    try:
        user = await user_repo.create_user(
            name=body.name,
            surname=body.surname,
            email=body.email,
            hashed_password=Hasher.get_password_hash(body.password),
        )

        await db.commit()

    except IntegrityError as error:
        await db.rollback()
        user_repo.handle_integrity_error(error)

    return UserRead.model_validate(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_from_token),
):
    user_repo = UserRepository(db)

    try:
        deleted_user_id = await user_repo.delete_user(user_id=user_id)

        if deleted_user_id is None:
            raise HTTPException(
                status_code=404, detail=f"User with id={user_id} not found"
            )

        await db.commit()

    except IntegrityError as error:
        await db.rollback()
        user_repo.handle_integrity_error(error)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_from_token),
) -> UserRead:
    user_repo = UserRepository(db)

    update_data = body.model_dump(exclude_none=True)

    try:
        updated_user_id = await user_repo.update_user(user_id=user_id, **update_data)

        if updated_user_id is None:
            raise HTTPException(
                status_code=404, detail=f"User with id={user_id} not found"
            )

        await db.commit()

    except IntegrityError as error:
        await db.rollback()
        user_repo.handle_integrity_error(error)

    updated_user = await user_repo.get_user_by_id(updated_user_id)

    return UserRead.model_validate(updated_user)
