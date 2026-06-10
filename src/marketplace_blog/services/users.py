from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from marketplace_blog.core.hashing import Hasher
from marketplace_blog.repositories.users import UserRepository


class UserService:
    def __init__(self, db):
        self.user_repo = UserRepository(db)

    async def get_user_by_id(self, user_id):
        return await self.user_repo.get_user_by_id(user_id)

    async def create_user(self, body):
        hashed_password = Hasher.get_password_hash(body.password)

        return await self.user_repo.create_user(
            name=body.name,
            surname=body.surname,
            email=body.email,
            hashed_password=hashed_password,
        )

    async def update_user(self, user_id, **kwargs):
        return await self.user_repo.update_user(user_id, **kwargs)

    async def delete_user(self, user_id):
        return await self.user_repo.delete_user(user_id)

    async def get_user_by_email(self, email: str):
        return await self.user_repo.get_user_by_email(email)

    async def authenticate_user(self, email: str, password: str):
        user = await self.get_user_by_email(email)

        if user is None:
            return None

        if not Hasher.verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def handle_integrity_error(error: IntegrityError) -> None:
        if "users_email_key" in str(error.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error"
        )
