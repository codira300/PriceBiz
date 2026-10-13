from typing import Optional

from app.services import comments as comments_service


async def create_comment(
    *,
    post_id: str,
    author_id: str,
    content: str,
    parent_comment_id: Optional[str] = None,
):
    return await comments_service.create_comment(
        post_id=post_id,
        author_id=author_id,
        content=content,
        parent_comment_id=parent_comment_id,
    )


async def get_comment(
    *,
    comment_id: str,
):
    return await comments_service.get_comment(
        comment_id=comment_id,
    )


async def get_post_comments(
    *,
    post_id: str,
    limit: int = 50,
):
    return await comments_service.get_post_comments(
        post_id=post_id,
        limit=limit,
    )


async def get_comment_replies(
    *,
    comment_id: str,
    limit: int = 50,
):
    return await comments_service.get_comment_replies(
        comment_id=comment_id,
        limit=limit,
    )


async def get_user_comments(
    *,
    user_id: str,
    limit: int = 50,
):
    return await comments_service.get_user_comments(
        user_id=user_id,
        limit=limit,
    )


async def update_comment(
    *,
    comment_id: str,
    author_id: str,
    content: str,
):
    return await comments_service.update_comment(
        comment_id=comment_id,
        author_id=author_id,
        content=content,
    )


async def delete_comment(
    *,
    comment_id: str,
    author_id: str,
):
    return await comments_service.delete_comment(
        comment_id=comment_id,
        author_id=author_id,
    )