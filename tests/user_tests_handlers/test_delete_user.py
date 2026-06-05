from uuid import uuid4

import pytest
from tests.utils import create_test_auth_headers_for_user


@pytest.mark.asyncio
async def test_delete_user(client, create_user_in_database, get_user_from_database):
    user_data = {
        "name": "Joseph",
        "surname": "Stalin",
        "email": "lol@kek.com",
        "hashed_password": "123456",
    }

    user = await create_user_in_database(**user_data)

    response = await client.delete(
        f"/api/v1/users/{user.user_id}",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 204

    user_from_db = await get_user_from_database(user.user_id)

    assert user_from_db.name == user_data["name"]
    assert user_from_db.surname == user_data["surname"]
    assert user_from_db.email == user_data["email"]

    assert user_from_db.is_active is False

    assert user_from_db.user_id == user.user_id


@pytest.mark.asyncio
async def test_delete_user_not_found(client, create_user_in_database):
    user_data = {
        "name": "Auth",
        "surname": "User",
        "email": "auth@test.com",
        "hashed_password": "123456",
    }

    user = await create_user_in_database(**user_data)

    unknown_user_id = uuid4()

    response = await client.delete(
        f"/api/v1/users/{unknown_user_id}",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 404

    assert response.json() == {"detail": f"User with id={unknown_user_id} not found"}


@pytest.mark.asyncio
async def test_delete_user_user_id_validation_error(client, create_user_in_database):
    user = await create_user_in_database(
        name="Auth",
        surname="User",
        email="auth@test.com",
        hashed_password="123456",
    )

    response = await client.delete(
        "/api/v1/users/123",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 422

    assert "user_id" in str(response.json())


@pytest.mark.asyncio
async def test_delete_user_unauth(client):
    response = await client.delete("/api/v1/users/123")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_delete_user_bad_cred(
    client,
    create_user_in_database,
):
    user_data = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "hashed_password": "SampleHashedPass",
    }

    user = await create_user_in_database(**user_data)

    fake_user_id = uuid4()

    resp = await client.delete(
        f"/api/v1/users/{user.user_id}",
        headers=create_test_auth_headers_for_user(str(fake_user_id)),
    )

    assert resp.status_code == 401
    assert resp.json() == {"detail": "Could not validate credentials"}


@pytest.mark.asyncio
async def test_delete_user_no_jwt(client, create_user_in_database):
    user_data = {
        "name": "Joseph",
        "surname": "Stalin",
        "email": "lol@kek.com",
        "hashed_password": "abcd1234",
    }

    user = await create_user_in_database(**user_data)
    response = await client.delete(f"/api/v1/users/{user.user_id}")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
