from uuid import uuid4

import pytest
from tests.utils import create_test_auth_headers_for_user


@pytest.mark.asyncio
async def test_delete_post(
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
        title="Test title",
        content="Test content",
        author_id=user.user_id,
        category_id=category.category_id,
    )

    response = await client.delete(
        f"/api/v1/posts/{post.post_id}",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 204

    await db_session.refresh(post)

    assert post.is_deleted is True


@pytest.mark.asyncio
async def test_delete_post_not_found(
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

    response = await client.delete(
        f"/api/v1/posts/{unknown_post_id}",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 404

    assert response.json() == {"detail": f"Post with id={unknown_post_id} not found"}


@pytest.mark.asyncio
async def test_delete_post_id_validation_error(
    client,
    create_user_in_database,
):
    user = await create_user_in_database(
        name="Joseph",
        surname="Stalin",
        email="user@test.com",
        hashed_password="123456789",
    )

    response = await client.delete(
        "/api/v1/posts/123",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_post_unauthorized(client):
    response = await client.delete("/api/v1/posts/123")

    assert response.status_code == 401
