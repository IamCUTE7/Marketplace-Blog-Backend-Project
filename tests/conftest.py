import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from marketplace_blog.core.config import get_settings
from marketplace_blog.db.base import Base
from marketplace_blog.db.session import get_db
from marketplace_blog.main import app
from marketplace_blog.models.category import Category
from marketplace_blog.models.post import Post
from marketplace_blog.repositories.users import UserRepository

settings = get_settings()
test_engine = create_async_engine(
    settings.test_database_url, echo=False, poolclass=NullPool
)
test_async_session = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)

CLEAN_TABLES = ["users", "categories", "posts"]


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client():
    async def override_get_db():
        session = test_async_session()

        try:
            yield session
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_tables():
    async with test_engine.begin() as conn:
        for table_name in CLEAN_TABLES:
            await conn.execute(
                text(f"TRUNCATE TABLE {table_name} " "RESTART IDENTITY CASCADE;")
            )
    yield
    async with test_engine.begin() as conn:
        for table_name in CLEAN_TABLES:
            await conn.execute(
                text(f"TRUNCATE TABLE {table_name} " "RESTART IDENTITY CASCADE;")
            )


@pytest_asyncio.fixture
async def db_session():
    async with test_async_session() as session:
        yield session


@pytest_asyncio.fixture
async def create_user_in_database(db_session):
    async def _create_user(**kwargs):
        user_repo = UserRepository(db_session)
        user = await user_repo.create_user(**kwargs)
        await db_session.commit()
        return user

    return _create_user


@pytest_asyncio.fixture
async def get_user_from_database():
    async def _get_user(user_id):
        async with test_async_session() as session:
            user_repo = UserRepository(session)
            return await user_repo.get_user_by_id(user_id)

    return _get_user


@pytest_asyncio.fixture
async def get_category_from_database():
    async def _get_category(category_id):
        async with test_async_session() as session:
            stmt = select(Category).where(Category.category_id == category_id)

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

    return _get_category


@pytest_asyncio.fixture
async def create_category_in_database(db_session):
    async def _create_category(**kwargs):
        category = Category(**kwargs)

        db_session.add(category)

        await db_session.commit()

        return category

    return _create_category


@pytest_asyncio.fixture
async def create_post_in_database(db_session):
    async def _create_post(**kwargs):
        post = Post(**kwargs)

        db_session.add(post)

        await db_session.commit()

        return post

    return _create_post
