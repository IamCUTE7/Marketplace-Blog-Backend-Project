from uuid import uuid4

import pytest
from tests.utils import create_test_auth_headers_for_user


@pytest.mark.asyncio
async def test_update_post(
    client,
    db_session,
    create_user_in_database,
    create_category_in_database,
    create_post_in_database,
):
    user = await create_user_in_database(
        name="Joseph",
        surname="Stalin",
        email="user@test.com",
        hashed_password="123456789",
    )

    category = await create_category_in_database(
        name="Programming",
    )

    post = await create_post_in_database(
        title="Old title",
        content="Old content for article",
        author_id=user.user_id,
        category_id=category.category_id,
    )

    updated_data = {
        "title": "New title",
        "content": "New content for article",
    }

    response = await client.patch(
        f"/api/v1/posts/{post.post_id}",
        json=updated_data,
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == updated_data["title"]
    assert data["content"] == updated_data["content"]


@pytest.mark.asyncio
async def test_update_particular_post(
    client,
    create_user_in_database,
    create_category_in_database,
    create_post_in_database,
):
    user = await create_user_in_database(
        name="Joseph",
        surname="Stalin",
        email="user@test.com",
        hashed_password="123456789",
    )

    category = await create_category_in_database(
        name="Programming",
    )

    post = await create_post_in_database(
        title="Old title",
        content="Old content",
        author_id=user.user_id,
        category_id=category.category_id,
    )

    response = await client.patch(
        f"/api/v1/posts/{post.post_id}",
        json={"title": "Updated title"},
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated title"
    assert data["content"] == "Old content"


@pytest.mark.asyncio
async def test_update_post_not_found(
    client,
    create_user_in_database,
):
    user = await create_user_in_database(
        name="Joseph",
        surname="Stalin",
        email="user@test.com",
        hashed_password="123456789",
    )

    unknown_post_id = uuid4()

    response = await client.patch(
        f"/api/v1/posts/{unknown_post_id}",
        json={"title": "Updated"},
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 404

    assert response.json() == {"detail": f"Post with id={unknown_post_id} not found"}


@pytest.mark.asyncio
async def test_update_post_validation_error(
    client,
    create_user_in_database,
    create_category_in_database,
    create_post_in_database,
):
    user = await create_user_in_database(
        name="Joseph",
        surname="Stalin",
        email="user@test.com",
        hashed_password="123456789",
    )

    category = await create_category_in_database(
        name="Programming",
    )

    post = await create_post_in_database(
        title="Old title",
        content="Old content",
        author_id=user.user_id,
        category_id=category.category_id,
    )

    response = await client.patch(
        f"/api/v1/posts/{post.post_id}",
        json={"title": "   "},
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 422
