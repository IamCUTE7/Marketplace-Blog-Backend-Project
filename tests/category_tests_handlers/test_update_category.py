from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_update_category(
    client,
    create_category_in_database,
):
    category = await create_category_in_database(
        name="Programming",
    )

    response = await client.patch(
        f"/api/v1/categories/{category.category_id}",
        json={
            "name": "Backend",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Backend"


@pytest.mark.asyncio
async def test_update_category_not_found(
    client,
):
    unknown_category_id = uuid4()

    response = await client.patch(
        f"/api/v1/categories/{unknown_category_id}",
        json={
            "name": "Backend",
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (f"Category with id={unknown_category_id} not found")
    }


@pytest.mark.asyncio
async def test_update_category_id_validation_error(
    client,
):
    response = await client.patch(
        "/api/v1/categories/123",
        json={
            "name": "Backend",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_category_validation_error(
    client,
    create_category_in_database,
):
    category = await create_category_in_database(
        name="Programming",
    )

    response = await client.patch(
        f"/api/v1/categories/{category.category_id}",
        json={
            "name": "   ",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_category_duplicate_name(
    client,
    create_category_in_database,
):
    category_1 = await create_category_in_database(
        name="Programming",
    )

    category_2 = await create_category_in_database(
        name="Backend",
    )

    response = await client.patch(
        f"/api/v1/categories/{category_2.category_id}",
        json={
            "name": category_1.name,
        },
    )

    assert response.status_code == 409
