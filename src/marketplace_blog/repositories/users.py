from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace_blog.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: UUID) -> User:
        query = select(User).where(User.user_id == user_id)

        result = await self.session.execute(query)

        user = result.scalar_one_or_none()

        return user

    async def create_user(
        self, name: str, surname: str, email: str, hashed_password: str
    ) -> User:
        user = User(
            name=name, surname=surname, email=email, hashed_password=hashed_password
        )

        self.session.add(user)

        await self.session.flush()

        return user

    async def delete_user(self, user_id: UUID) -> UUID | None:
        query = (
            update(User)
            .where(User.user_id == user_id, User.is_active.is_(True))
            .values(is_active=False)
            .returning(User.user_id)
        )

        result = await self.session.execute(query)

        deleted_user_id = result.scalar_one_or_none()

        await self.session.flush()

        return deleted_user_id

    async def update_user(self, user_id: UUID, **kwargs) -> UUID | None:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active.is_(True)))
            .values(**kwargs)
            .returning(User.user_id)
        )

        result = await self.session.execute(query)

        updated_user_id = result.fetchone()

        if updated_user_id is not None:
            return updated_user_id[0]

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    @staticmethod
    def handle_integrity_error(error: IntegrityError) -> None:
        if "users_email_key" in str(error.orig):
            raise HTTPException(status_code=409, detail="Email already exists")

        raise HTTPException(status_code=500, detail="Database error")
