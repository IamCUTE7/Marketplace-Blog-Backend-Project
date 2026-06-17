from uuid import uuid4

import pytest
from tests.utils import create_test_auth_headers_for_user


@pytest.mark.asyncio
async def test_get_user(
    client,
    get_user_from_database,
):
    user_data = {
        "name": "Joseph",
        "surname": "Stalin",
        "email": "lol@kek.com",
        "password": "123456789",
    }

    create_response = await client.post(
        "/api/v1/users/",
        json=user_data,
    )

    assert create_response.status_code == 201

    created_user = create_response.json()

    response = await client.get(
        f"/api/v1/users/{created_user['user_id']}",
        headers=create_test_auth_headers_for_user(str(created_user["user_id"])),
    )

    data_from_response = response.json()

    assert response.status_code == 200

    assert data_from_response["user_id"] == created_user["user_id"]
    assert data_from_response["name"] == created_user["name"]
    assert data_from_response["surname"] == created_user["surname"]
    assert data_from_response["email"] == created_user["email"]

    user_from_db = await get_user_from_database(created_user["user_id"])

    assert str(user_from_db.user_id) == created_user["user_id"]

    assert user_from_db.name == created_user["name"]
    assert user_from_db.surname == created_user["surname"]
    assert user_from_db.email == created_user["email"]

    assert user_from_db.is_active is True


@pytest.mark.asyncio
async def test_get_user_id_validation_error(
    client,
    create_user_in_database,
):
    auth_user = {
        "name": "Auth",
        "surname": "User",
        "email": "auth@test.com",
        "hashed_password": "123456789",
    }

    auth_user = await create_user_in_database(**auth_user)

    response = await client.get(
        "/api/v1/users/123",
        headers=create_test_auth_headers_for_user(str(auth_user.user_id)),
    )

    assert response.status_code == 422

    assert "user_id" in str(response.json())


@pytest.mark.asyncio
async def test_get_user_not_found(
    client,
    create_user_in_database,
):
    auth_user = {
        "name": "Auth",
        "surname": "User",
        "email": "auth@test.com",
        "hashed_password": "123456789",
    }

    auth_user = await create_user_in_database(**auth_user)

    user_id = uuid4()

    response = await client.get(
        f"/api/v1/users/{user_id}",
        headers=create_test_auth_headers_for_user(str(auth_user.user_id)),
    )

    assert response.status_code == 404

    assert response.json() == {"detail": f"User with id={user_id} not found"}
