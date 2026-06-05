from uuid import uuid4

import pytest
from sqlalchemy import update
from tests.utils import create_test_auth_headers_for_user

from marketplace_blog.models.post import Post


@pytest.mark.asyncio
async def test_get_post(
    client,
    create_user_in_database,
    create_category_in_database,
    create_post_in_database,
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

    post = await create_post_in_database(
        title="FastAPI Guide",
        content="This is a FastAPI article",
        author_id=user.user_id,
        category_id=category.category_id,
    )

    response = await client.get(
        f"/api/v1/posts/{post.post_id}",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["post_id"] == str(post.post_id)
    assert data["title"] == post.title
    assert data["content"] == post.content


@pytest.mark.asyncio
async def test_get_post_id_validation_error(
    client,
    create_user_in_database,
):
    user = await create_user_in_database(
        name="Joseph",
        surname="Stalin",
        email="lol@kek.com",
        hashed_password="123456789",
    )

    response = await client.get(
        "/api/v1/posts/123",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 422

    assert "post_id" in str(response.json())


@pytest.mark.asyncio
async def test_get_post_not_found(
    client,
    create_user_in_database,
):
    user = await create_user_in_database(
        name="Joseph",
        surname="Stalin",
        email="lol@kek.com",
        hashed_password="123456789",
    )

    unknown_post_id = uuid4()

    response = await client.get(
        f"/api/v1/posts/{unknown_post_id}",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 404

    assert response.json() == {"detail": f"Post with id={unknown_post_id} not found"}


@pytest.mark.asyncio
async def test_get_posts(
    client,
    create_post_in_database,
    create_category_in_database,
    create_user_in_database,
):
    user = await create_user_in_database(
        name="Mike", surname="Ivanov", email="lol@kek.com", hashed_password="123456789"
    )

    category = await create_category_in_database(name="Programming")

    await create_post_in_database(
        title="FastAPI Authentication Guide",
        content="This article explains JWT authentication in FastAPI applications",
        author_id=user.user_id,
        category_id=category.category_id,
    )

    await create_post_in_database(
        title="Django Authentication Guide",
        content="This article is an intro to Django basics",
        author_id=user.user_id,
        category_id=category.category_id,
    )

    response = await client.get(
        "/api/v1/posts/", headers=create_test_auth_headers_for_user(str(user.user_id))
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    titles = [post["title"] for post in data]

    assert "FastAPI Authentication Guide" in titles
    assert "Django Authentication Guide" in titles


@pytest.mark.asyncio
async def test_get_posts_empty(client, create_user_in_database):
    user = await create_user_in_database(
        name="Mike", surname="Ivanov", email="lol@kek.com", hashed_password="123456789"
    )
    response = await client.get(
        "/api/v1/posts/", headers=create_test_auth_headers_for_user(str(user.user_id))
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_posts_excludes_deleted(
    client,
    db_session,
    create_post_in_database,
    create_category_in_database,
    create_user_in_database,
):
    user = await create_user_in_database(
        name="Mike", surname="Ivanov", email="lol@kek.com", hashed_password="123456789"
    )

    category = await create_category_in_database(name="Programming")

    post_1 = await create_post_in_database(
        title="FastAPI Authentication Guide",
        content="This article explains JWT authentication in FastAPI applications",
        author_id=user.user_id,
        category_id=category.category_id,
    )

    post_2 = await create_post_in_database(
        title="Django Authentication Guide",
        content="This article is an intro to Django basics",
        author_id=user.user_id,
        category_id=category.category_id,
    )

    await db_session.execute(
        update(Post).where(Post.post_id == post_2.post_id).values(is_deleted=True)
    )

    await db_session.commit()

    response = await client.get(
        "/api/v1/posts/", headers=create_test_auth_headers_for_user(str(user.user_id))
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["post_id"] == str(post_1.post_id)


@pytest.mark.asyncio
async def test_get_posts_pagination(
    client,
    create_post_in_database,
    create_category_in_database,
    create_user_in_database,
):
    user = await create_user_in_database(
        name="Mike", surname="Ivanov", email="lol@kek.com", hashed_password="123456789"
    )
    category = await create_category_in_database(name="Programming")

    for i in range(15):
        await create_post_in_database(
            title=f"Post {i}",
            content=f"Content {i} long enough for validation",
            author_id=user.user_id,
            category_id=category.category_id,
        )

    response = await client.get(
        "/api/v1/posts/?page_number=1&page_size=10",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 10


@pytest.mark.asyncio
async def test_get_posts_second_page(
    client,
    create_post_in_database,
    create_category_in_database,
    create_user_in_database,
):
    user = await create_user_in_database(
        name="Mike", surname="Ivanov", email="lol@kek.com", hashed_password="123456789"
    )
    category = await create_category_in_database(name="Programming")

    for i in range(15):
        await create_post_in_database(
            title=f"Post {i}",
            content=f"Content {i} long enough for validation",
            author_id=user.user_id,
            category_id=category.category_id,
        )

    response = await client.get(
        "/api/v1/posts/?page_number=2&page_size=10",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 5


@pytest.mark.asyncio
async def test_get_posts_filter_by_category(
    client,
    create_post_in_database,
    create_category_in_database,
    create_user_in_database,
):
    programming = await create_category_in_database(name="Programming")

    databases = await create_category_in_database(name="Databases")

    user = await create_user_in_database(
        name="Mike",
        surname="Ivanov",
        email="lol@kek.com",
        hashed_password="123456789",
    )

    await create_post_in_database(
        title="FastAPI",
        content="FastAPI content",
        author_id=user.user_id,
        category_id=programming.category_id,
    )

    await create_post_in_database(
        title="Django",
        content="Django content",
        author_id=user.user_id,
        category_id=programming.category_id,
    )

    await create_post_in_database(
        title="PostgreSQL",
        content="PostgreSQL content",
        author_id=user.user_id,
        category_id=databases.category_id,
    )

    response = await client.get(
        f"/api/v1/posts/?category_id={programming.category_id}",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    for post in data:
        assert post["category_id"] == str(programming.category_id)


@pytest.mark.asyncio
async def test_get_post_search(
    client,
    create_post_in_database,
    create_category_in_database,
    create_user_in_database,
):
    user = await create_user_in_database(
        name="Mike",
        surname="Ivanov",
        email="lol@kek.com",
        hashed_password="123456789",
    )

    programming = await create_category_in_database(name="Programming")

    databases = await create_category_in_database(name="Databases")

    await create_post_in_database(
        title="FastAPI",
        content="FastAPI content",
        author_id=user.user_id,
        category_id=programming.category_id,
    )

    await create_post_in_database(
        title="Django",
        content="Django content",
        author_id=user.user_id,
        category_id=programming.category_id,
    )

    await create_post_in_database(
        title="PostgreSQL",
        content="PostgreSQL content",
        author_id=user.user_id,
        category_id=databases.category_id,
    )

    response = await client.get(
        "/api/v1/posts/?search=fastapi",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "FastAPI"


@pytest.mark.asyncio
async def test_get_search_content(
    client,
    create_post_in_database,
    create_category_in_database,
    create_user_in_database,
):
    user = await create_user_in_database(
        name="Mike",
        surname="Ivanov",
        email="lol@kek.com",
        hashed_password="123456789",
    )

    programming = await create_category_in_database(name="Programming")

    databases = await create_category_in_database(name="Databases")

    await create_post_in_database(
        title="Random title",
        content="This article explains JWT authentication",
        author_id=user.user_id,
        category_id=programming.category_id,
    )

    await create_post_in_database(
        title="Django",
        content="Django content",
        author_id=user.user_id,
        category_id=programming.category_id,
    )

    await create_post_in_database(
        title="PostgreSQL",
        content="PostgreSQL content",
        author_id=user.user_id,
        category_id=databases.category_id,
    )

    response = await client.get(
        "/api/v1/posts/?search=jwt",
        headers=create_test_auth_headers_for_user(str(user.user_id)),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Random title"
