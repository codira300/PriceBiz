from typing import Optional

from app.config import (
    MAX_COMMENT_LENGTH,
    DEFAULT_LIMIT,
    MAX_LIMIT,
) 
from app.database import comments as comments_db
from app.utils import get_object_id


MAX_COMMENT_LENGTH = 1000

DEFAULT_LIMIT = 50

MAX_LIMIT = 100


class CommentServiceError(Exception):
    pass


class InvalidCommentError(CommentServiceError):
    pass


class CommentNotFoundError(CommentServiceError):
    pass


class CommentAuthorizationError(CommentServiceError):
    pass


def _validate_content(
    content: str,
) -> str:
    if not isinstance(content, str):
        raise InvalidCommentError(
            "Comment content must be a string."
        )

    content = content.strip()

    if not content:
        raise InvalidCommentError(
            "Comment content cannot be empty."
        )

    if len(content) > MAX_COMMENT_LENGTH:
        raise InvalidCommentError(
            f"Comment cannot exceed "
            f"{MAX_COMMENT_LENGTH} characters."
        )

    return content


def _validate_id(
    value: str,
    resource: str,
) -> str:
    if not isinstance(value, str):
        raise InvalidCommentError(
            f"{resource.title()} ID must be a string."
        )

    value = value.strip()

    if not value:
        raise InvalidCommentError(
            f"{resource.title()} ID is required."
        )

    try:
        get_object_id(value, resource)
    except Exception as exc:
        raise InvalidCommentError(
            f"Invalid {resource} ID."
        ) from exc

    return value


def _validate_limit(
    limit: int,
) -> int:
    if not isinstance(limit, int):
        raise InvalidCommentError(
            "Limit must be an integer."
        )

    if limit < 1:
        raise InvalidCommentError(
            "Limit must be at least 1."
        )

    if limit > MAX_LIMIT:
        raise InvalidCommentError(
            f"Limit cannot exceed {MAX_LIMIT}."
        )

    return limit


async def create_comment(
    *,
    post_id: str,
    author_id: str,
    content: str,
    parent_comment_id: Optional[str] = None,
):
    """
    Create a comment on a post.

    If parent_comment_id is supplied,
    the comment becomes a reply to that comment.
    """

    post_id = _validate_id(
        post_id,
        "post",
    )

    author_id = _validate_id(
        author_id,
        "user",
    )

    content = _validate_content(content)

    if parent_comment_id is not None:
        parent_comment_id = _validate_id(
            parent_comment_id,
            "parent comment",
        )

    comment = await comments_db.create_comment(
        post_id=post_id,
        author_id=author_id,
        content=content,
        parent_comment_id=parent_comment_id,
    )

    if comment is None:
        raise CommentServiceError(
            "Unable to create comment."
        )

    return comment


async def get_comment(
    *,
    comment_id: str,
):
    comment_id = _validate_id(
        comment_id,
        "comment",
    )

    comment = await comments_db.get_comment_by_id(
        comment_id
    )

    if comment is None:
        raise CommentNotFoundError(
            "Comment not found."
        )

    return comment


async def get_post_comments(
    *,
    post_id: str,
    limit: int = DEFAULT_LIMIT,
):
    """
    Get top-level comments belonging to a post.
    """

    post_id = _validate_id(
        post_id,
        "post",
    )

    limit = _validate_limit(limit)

    return await comments_db.get_post_comments(
        post_id=post_id,
        limit=limit,
    )


async def get_comment_replies(
    *,
    comment_id: str,
    limit: int = DEFAULT_LIMIT,
):
    """
    Get replies belonging to a comment.
    """

    comment_id = _validate_id(
        comment_id,
        "comment",
    )

    limit = _validate_limit(limit)

    comment = await comments_db.get_comment_by_id(
        comment_id
    )

    if comment is None:
        raise CommentNotFoundError(
            "Comment not found."
        )

    return await comments_db.get_comment_replies(
        comment_id=comment_id,
        limit=limit,
    )


async def get_user_comments(
    *,
    user_id: str,
    limit: int = DEFAULT_LIMIT,
):
    """
    Get comments created by a user.
    """

    user_id = _validate_id(
        user_id,
        "user",
    )

    limit = _validate_limit(limit)

    return await comments_db.get_comments_by_user(
        user_id=user_id,
        limit=limit,
    )


async def update_comment(
    *,
    comment_id: str,
    author_id: str,
    content: str,
):
    """
    Update a comment.

    Only the author of the comment can update it.
    """

    comment_id = _validate_id(
        comment_id,
        "comment",
    )

    author_id = _validate_id(
        author_id,
        "user",
    )

    content = _validate_content(content)

    comment = await comments_db.get_comment_by_id(
        comment_id
    )

    if comment is None:
        raise CommentNotFoundError(
            "Comment not found."
        )

    if str(comment["author_id"]) != author_id:
        raise CommentAuthorizationError(
            "You are not allowed to update this comment."
        )

    updated_comment = await comments_db.update_comment(
        comment_id=comment_id,
        content=content,
    )

    if updated_comment is None:
        raise CommentNotFoundError(
            "Comment not found."
        )

    return updated_comment


async def delete_comment(
    *,
    comment_id: str,
    author_id: str,
):
    """
    Delete a comment.

    Only the author of the comment can delete it.
    """

    comment_id = _validate_id(
        comment_id,
        "comment",
    )

    author_id = _validate_id(
        author_id,
        "user",
    )

    comment = await comments_db.get_comment_by_id(
        comment_id
    )

    if comment is None:
        raise CommentNotFoundError(
            "Comment not found."
        )

    if str(comment["author_id"]) != author_id:
        raise CommentAuthorizationError(
            "You are not allowed to delete this comment."
        )

    deleted_comment = await comments_db.delete_comment(
        comment_id=comment_id,
    )

    if deleted_comment is None:
        raise CommentNotFoundError(
            "Comment not found."
        )

    return deleted_comment