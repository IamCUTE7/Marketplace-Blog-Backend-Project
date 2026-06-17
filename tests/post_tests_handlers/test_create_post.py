import pytest
from sqlalchemy import select
from tests.utils import create_test_auth_headers_for_user

from marketplace_blog.models.post import Post


@pytest.mark.asyncio
async def test_create_post(
    client,
    db_session,
    create_user_in_database,
    create_category_in_database,
):
    user = await create_user_in_database(
        name="Joseph",
        surname="Stalin",
        email="lol@kek.com",
        hashed_password="123456789",
    )

    category = await create_category_in_database(
        name="Programming",
    )

    post_data = {
        "title": "FastAPI Guide",
        "content": "This is a test article about FastAPI framework",
        "category_id": str(category.category_id),
    }

    response = await client.post(
        "/api/v1/posts/",
        json=post_data,
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["title"] == post_data["title"]
    assert response_data["content"] == post_data["content"]

    assert response_data["author_id"] == str(user.user_id)

    assert response_data["category_id"] == str(category.category_id)

    stmt = select(Post).where(Post.post_id == response_data["post_id"])

    result = await db_session.execute(stmt)

    post = result.scalar_one_or_none()

    assert post is not None

    assert post.title == post_data["title"]
    assert post.content == post_data["content"]

    assert post.author_id == user.user_id
    assert post.category_id == category.category_id

    assert response_data["is_deleted"] is False
