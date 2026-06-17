import json

from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy.exc import IntegrityError

from marketplace_blog.core.hashing import Hasher
from marketplace_blog.rabbit.producer import send_message
from marketplace_blog.repositories.users import UserRepository


class UserService:
    def __init__(self, db):
        self.user_repo = UserRepository(db)

    async def get_user_by_id(self, user_id):
        return await self.user_repo.get_user_by_id(user_id)

    async def create_user(self, body):
        hashed_password = Hasher.get_password_hash(body.password)

        try:
            user = await self.user_repo.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email,
                hashed_password=hashed_password,
            )

            await self.user_repo.session.commit()

            logger.info("User {} created", user.email)

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

            return user

        except IntegrityError as error:
            await self.user_repo.session.rollback()
            self.handle_integrity_error(error)

    async def update_user(self, user_id, **kwargs):
        try:
            updated_user_id = await self.user_repo.update_user(user_id, **kwargs)

            if updated_user_id is None:
                return None

            await self.user_repo.session.commit()

            logger.info("User with id={} was updated", updated_user_id)

            updated_user = await self.user_repo.get_user_by_id(updated_user_id)

            return updated_user

        except IntegrityError as error:
            await self.user_repo.session.rollback()
            self.handle_integrity_error(error)

    async def delete_user(self, user_id):
        deleted_user_id = await self.user_repo.delete_user(user_id)

        if deleted_user_id is None:
            return None

        await self.user_repo.session.commit()

        logger.info("User with id={} was deleted", deleted_user_id)

        return deleted_user_id

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
