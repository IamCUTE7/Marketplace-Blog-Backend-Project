from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_get_category(
    client,
    create_category_in_database,
):
    category = await create_category_in_database(
        name="Programming",
    )

    response = await client.get(f"/api/v1/categories/{category.category_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["category_id"] == str(category.category_id)
    assert data["name"] == category.name


@pytest.mark.asyncio
async def test_get_category_not_found(
    client,
):
    unknown_category_id = uuid4()

    response = await client.get(f"/api/v1/categories/{unknown_category_id}")

    assert response.status_code == 404

    assert response.json() == {
        "detail": (f"Category with id={unknown_category_id} not found")
    }


@pytest.mark.asyncio
async def test_get_category_id_validation_error(
    client,
):
    response = await client.get("/api/v1/categories/123")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_categories(
    client,
    create_category_in_database,
):
    await create_category_in_database(
        name="Programming",
    )

    await create_category_in_database(
        name="Databases",
    )

    response = await client.get("/api/v1/categories/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
