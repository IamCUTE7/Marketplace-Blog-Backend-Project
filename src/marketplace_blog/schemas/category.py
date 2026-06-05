from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: UUID
    name: str

    is_deleted: bool


class CategoryCreate(BaseModel):
    name: str = Field(min_length=3, max_length=80)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Category name cannot be empty")

        return value


class CategoryUpdate(BaseModel):
    name: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Category name cannot be empty")

        return value
