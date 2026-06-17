import pytest
from sqlalchemy import select

from marketplace_blog.models.category import Category


@pytest.mark.asyncio
async def test_create_category(
    client,
    db_session,
):
    category_data = {
        "name": "Programming",
    }

    response = await client.post(
        "/api/v1/categories/",
        json=category_data,
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["name"] == category_data["name"]

    stmt = select(Category).where(Category.category_id == response_data["category_id"])

    result = await db_session.execute(stmt)

    category = result.scalar_one_or_none()

    assert category is not None

    assert category.name == category_data["name"]


@pytest.mark.asyncio
async def test_create_category_duplicate_name_error(
    client,
):
    category_data = {
        "name": "Programming",
    }

    response = await client.post(
        "/api/v1/categories/",
        json=category_data,
    )

    assert response.status_code == 201

    response = await client.post(
        "/api/v1/categories/",
        json=category_data,
    )

    assert response.status_code == 409


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "category_data, expected_field",
    [
        (
            {},
            "name",
        ),
        (
            {
                "name": "",
            },
            "name",
        ),
        (
            {
                "name": "  ",
            },
            "name",
        ),
    ],
)
async def test_create_category_validation_error(
    client,
    category_data,
    expected_field,
):
    response = await client.post(
        "/api/v1/categories/",
        json=category_data,
    )

    assert response.status_code == 422

    assert expected_field in str(response.json())
