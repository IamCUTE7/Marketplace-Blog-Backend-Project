from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    surname: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name", "surname")
    @classmethod
    def validate_only_letters(cls, value: str) -> str:
        normalized = value.replace("-", "").replace(" ", "")
        if not normalized.isalpha():
            raise ValueError("Must only contain letters")
        return value


class UserUpdate(BaseModel):
    name: str | None = None
    surname: str | None = None
    email: EmailStr | None = None

    @field_validator("name", "surname")
    @classmethod
    def validate_only_letters(cls, value: str | None):
        if value is None:
            return value

        normalized = value.replace("-", "").replace(" ", "")

        if not normalized.isalpha():
            raise ValueError("Must only contain letters")

        return value
