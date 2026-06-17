from fastapi import APIRouter

from marketplace_blog.api.routes import categories, login, posts, users

api_router = APIRouter()

api_router.include_router(
    login.login_router,
    prefix="/login",
    tags=["login"],
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)

api_router.include_router(
    posts.router,
    prefix="/posts",
    tags=["posts"],
)

api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["categories"],
)
