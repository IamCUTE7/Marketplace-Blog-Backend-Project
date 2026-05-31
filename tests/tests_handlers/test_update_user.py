import pytest
from tests.utils import create_test_auth_headers_for_user


@pytest.mark.asyncio
async def test_update_user(
    client,
    create_user_in_database,
    get_user_from_database,
):
    user_data = {
        "name": "Joseph",
        "surname": "Stalin",
        "email": "lol@kek.com",
        "hashed_password": "123456789",
    }

    user_data_updated = {
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "kek@lol.com",
    }

    user = await create_user_in_database(**user_data)

    response = await client.patch(
        f"/api/v1/users/{user.user_id}",
        json=user_data_updated,
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )
    assert response.status_code == 200

    response_data = response.json()

    assert response_data["name"] == user_data_updated["name"]
    assert response_data["surname"] == user_data_updated["surname"]
    assert response_data["email"] == user_data_updated["email"]

    user_from_db = await get_user_from_database(user.user_id)

    assert user_from_db.name == user_data_updated["name"]
    assert user_from_db.surname == user_data_updated["surname"]
    assert user_from_db.email == user_data_updated["email"]

    assert user_from_db.is_active is True


@pytest.mark.asyncio
async def test_update_particular_user(
    client,
    create_user_in_database,
    get_user_from_database,
):
    user_1 = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "nikolai@kek.com",
        "hashed_password": "123456789",
    }

    user_2 = {
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "ivan@kek.com",
        "hashed_password": "123456789",
    }

    updated_data = {"name": "Petr", "surname": "Petrov", "email": "petr@kek.com"}

    user_1 = await create_user_in_database(**user_1)
    user_2 = await create_user_in_database(**user_2)

    response = await client.patch(
        f"/api/v1/users/{user_1.user_id}",
        json=updated_data,
        headers=create_test_auth_headers_for_user(str(user_1.user_id)),
    )
    assert response.status_code == 200

    updated_user = await get_user_from_database(user_1.user_id)

    assert updated_user.name == updated_data["name"]
    assert updated_user.email == updated_data["email"]

    untouched_user = await get_user_from_database(user_2.user_id)

    assert untouched_user.name == "Ivan"
    assert untouched_user.email == "ivan@kek.com"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_data_updated, expected_status_code, expected_detail",
    [
        (
            {"name": "123"},
            422,
            {"detail": "Name should contains only letters"},
        ),
        (
            {"surname": "123"},
            422,
            {"detail": "Surname should contains only letters"},
        ),
    ],
)
async def test_update_user_error(
    client,
    create_user_in_database,
    user_data_updated,
    expected_status_code,
    expected_detail,
):
    user_data = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "hashed_password": "123456789",
    }

    user = await create_user_in_database(**user_data)

    response = await client.patch(
        f"/api/v1/users/{user.user_id}",
        json=user_data_updated,
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == expected_status_code
    assert "Must only contain letters" in str(response.json())


@pytest.mark.asyncio
async def test_update_user_id_validation_error(client, create_user_in_database):
    user_data = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "hashed_password": "123456789",
    }

    user = await create_user_in_database(**user_data)

    user_data_updated = {
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "cheburek@kek.com",
    }

    response = await client.patch(
        "/api/v1/users/123",
        json=user_data_updated,
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 422
    assert "user_id" in str(response.json())


@pytest.mark.asyncio
async def test_user_duplicate_email_error(
    client,
    create_user_in_database,
):
    user_data_1 = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "hashed_password": "123456789",
    }

    user_data_2 = {
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "ivan@kek.com",
        "hashed_password": "123456789",
    }

    user_data_updated = {"email": user_data_2["email"]}

    user_1 = await create_user_in_database(**user_data_1)

    response = await client.patch(
        f"/api/v1/users/{user_1.user_id}",
        json=user_data_updated,
        headers=create_test_auth_headers_for_user(str(user_1.user_id)),
    )

    assert response.status_code == 409

    assert response.json() == {"detail": "Email already exists"}
