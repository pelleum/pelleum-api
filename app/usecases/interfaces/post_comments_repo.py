from typing import Tuple, List
from abc import ABC, abstractmethod

from app.usecases.schemas import post_comments


class IPostsCommentsRepo(ABC):
    @abstractmethod
    async def create(self, post_id: int, user_id: int, content: str) -> None:
        """Saves a new post comment"""

    @abstractmethod
    async def retrieve_post_comment_by_id(
        self, comment_id: int
    ) -> post_comments.PostCommentInDB:
        """Retrieves on comment by comment_id"""

    @abstractmethod
    async def update(self, content: str, comment_id: int) -> None:
        """Update a comment by comment_id"""

    @abstractmethod
    async def retrieve_many_with_filter(
        self,
        user_id: int,
        post_id: int,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[post_comments.PostCommentInDB], int]:
        """Retrieve many post comments with filter"""

    @abstractmethod
    async def delete(self, comment_id: int) -> None:
        """Deletes a post comment by comment_id"""
