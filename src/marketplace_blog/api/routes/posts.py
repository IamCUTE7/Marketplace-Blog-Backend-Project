import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace_blog.api.routes.login import get_current_user_from_token
from marketplace_blog.db.session import get_db
from marketplace_blog.rabbit.producer import send_message
from marketplace_blog.repositories.posts import PostRepository
from marketplace_blog.schemas.post import PostCreate, PostRead, PostUpdate

router = APIRouter()


@router.get("/{post_id}", status_code=200)
async def get_post(post_id: UUID, db: AsyncSession = Depends(get_db)) -> PostRead:
    post_repo = PostRepository(db)

    post = await post_repo.get_post_by_id(post_id=post_id)

    if post is None:
        raise HTTPException(status_code=404, detail=f"Post with id={post_id} not found")

    return PostRead.model_validate(post)


@router.post("/", response_model=PostRead, status_code=201)
async def create_post(
    body: PostCreate,
    current_user=Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
) -> PostRead:
    post_repo = PostRepository(db)

    post = await post_repo.create_post(
        title=body.title,
        content=body.content,
        author_id=current_user.user_id,
        category_id=body.category_id,
    )
    await db.commit()

    logger.info("Post {} was created", post.title)

    await send_message(
        json.dumps(
            {"event": "post_created", "post_id": str(post.post_id), "title": post.title}
        )
    )

    return PostRead.model_validate(post)


@router.patch("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: UUID,
    body: PostUpdate,
    current_user=Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
) -> PostRead:
    post_repo = PostRepository(db)

    updated_data = body.model_dump(exclude_none=True)

    updated_post_id = await post_repo.update_post(post_id=post_id, **updated_data)

    if updated_post_id is None:
        raise HTTPException(status_code=404, detail=f"Post with id={post_id} not found")

    await db.commit()

    logger.info("Post with id={} was updated", updated_post_id)

    await send_message(
        json.dumps({"event": "post_updated", "post_id": str(updated_post_id)})
    )

    updated_post = await post_repo.get_post_by_id(updated_post_id)

    return PostRead.model_validate(updated_post)


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: UUID,
    current_user=Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    post_repo = PostRepository(db)

    deleted_post_id = await post_repo.delete_post(post_id=post_id)

    if deleted_post_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Post with id={post_id} not found",
        )

    await db.commit()

    logger.info("Post with id={} was deleted", deleted_post_id)

    await send_message(
        json.dumps({"event": "post_deleted", "post_id": str(deleted_post_id)})
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/", response_model=list[PostRead])
async def get_posts(
    page_number: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    category_id: UUID | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    post_repo = PostRepository(db)

    posts = await post_repo.get_posts(
        page_number=page_number,
        page_size=page_size,
        category_id=category_id,
        search=search,
    )

    return [PostRead.model_validate(post) for post in posts]
