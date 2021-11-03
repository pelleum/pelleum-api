from typing import Tuple, List
from abc import ABC, abstractmethod

from app.usecases.schemas import thesis_comments


class IThesesCommentsRepo(ABC):
    @abstractmethod
    async def create(
        self, comment_info: thesis_comments.CreateThesisCommentRepoAdapter
    ) -> None:
        """Saves a new thesis comment"""

    @abstractmethod
    async def retrieve_thesis_comment_by_id(
        self, comment_id: int
    ) -> thesis_comments.ThesisCommentInDB:
        """Retrieves on comment by comment_id"""

    @abstractmethod
    async def update(self, content: str, comment_id: int) -> None:
        """Update a comment by comment_id"""

    @abstractmethod
    async def retrieve_many_with_filter(
        self,
        user_id: int,
        thesis_id: int,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[thesis_comments.ThesisCommentInDB], int]:
        """Retrieve many thesis comments with filter"""

    @abstractmethod
    async def delete(self, comment_id: int) -> None:
        """Deletes a thesis comment by comment_id"""
