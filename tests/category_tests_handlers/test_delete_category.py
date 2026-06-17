from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_delete_category(
    client,
    create_category_in_database,
):
    category = await create_category_in_database(
        name="Programming",
    )

    response = await client.delete(
        f"/api/v1/categories/{category.category_id}",
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_category_not_found(
    client,
):
    unknown_category_id = uuid4()

    response = await client.delete(
        f"/api/v1/categories/{unknown_category_id}",
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (f"Category with id={unknown_category_id} not found")
    }


@pytest.mark.asyncio
async def test_delete_category_id_validation_error(
    client,
):
    response = await client.delete(
        "/api/v1/categories/123",
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_category_twice(
    client,
    create_category_in_database,
):
    category = await create_category_in_database(
        name="Programming",
    )

    response = await client.delete(
        f"/api/v1/categories/{category.category_id}",
    )

    assert response.status_code == 204

    response = await client.delete(
        f"/api/v1/categories/{category.category_id}",
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_category_sets_is_deleted(
    client,
    get_category_from_database,
    create_category_in_database,
):
    category = await create_category_in_database(
        name="Programming",
    )

    response = await client.delete(
        f"/api/v1/categories/{category.category_id}",
    )

    assert response.status_code == 204

    deleted_category = await get_category_from_database(category.category_id)

    assert deleted_category is not None
    assert deleted_category.is_deleted is True
