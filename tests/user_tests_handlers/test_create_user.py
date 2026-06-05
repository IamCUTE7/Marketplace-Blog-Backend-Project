import pytest
from sqlalchemy import select

from marketplace_blog.models.user import User


@pytest.mark.asyncio
async def test_create_user(client, db_session):
    user_data = {
        "name": "Joseph",
        "surname": "Stalin",
        "email": "lol@kek.com",
        "password": "123456789",
    }

    response = await client.post("api/v1/users/", json=user_data)

    response_data = response.json()

    assert response.status_code == 201

    assert response_data["name"] == user_data["name"]
    assert response_data["surname"] == user_data["surname"]
    assert response_data["email"] == user_data["email"]

    stmt = select(User).where(User.email == user_data["email"])

    result = await db_session.execute(stmt)

    user = result.scalar_one_or_none()

    assert user is not None

    assert user.name == user_data["name"]
    assert user.surname == user_data["surname"]
    assert user.email == user_data["email"]


@pytest.mark.asyncio
async def test_create_user_duplicate_email_error(client):
    user_data = {
        "name": "Joseph",
        "surname": "Stalin",
        "email": "lol@kek.com",
        "password": "123456789",
    }

    user_data_same_email = {
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "lol@kek.com",
        "password": "123456789",
    }

    response = await client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 201

    response = await client.post("/api/v1/users/", json=user_data_same_email)

    assert response.status_code == 409

    assert response.json() == {"detail": "Email already exists"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_data, expected_field",
    [
        (
            {
                "name": "Joseph",
                "surname": "Stalin",
                "email": "lol@kek.com",
            },
            "password",
        ),
        (
            {
                "surname": "Stalin",
                "email": "lol@kek.com",
                "password": "123456789",
            },
            "name",
        ),
        (
            {
                "name": "Joseph",
                "email": "lol@kek.com",
                "password": "123456789",
            },
            "surname",
        ),
        (
            {
                "name": "Joseph",
                "surname": "Stalin",
                "password": "123456789",
            },
            "email",
        ),
    ],
)
async def test_create_user_validation_error(client, user_data, expected_field):
    response = await client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 422
    assert expected_field in str(response.json())
