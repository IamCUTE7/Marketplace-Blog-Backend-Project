from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    post_id: UUID
    title: str
    content: str

    author_id: UUID
    category_id: UUID

    created_at: datetime
    updated_at: datetime

    is_deleted: bool


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=60)
    content: str = Field(min_length=10, max_length=2000)

    category_id: UUID

    @field_validator("title", "content")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")
        return value


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category_id: UUID | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value

    @field_validator("title", "content")
    @classmethod
    def validate_content(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")

        return value
