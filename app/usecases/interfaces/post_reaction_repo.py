from abc import ABC, abstractmethod
from typing import List, Tuple

from app.usecases.schemas import post_reactions


class IPostReactionRepo(ABC):
    @abstractmethod
    async def create(
        self, post_reaction: post_reactions.PostReactionRepoAdapter
    ) -> None:
        """Create reaction"""

    @abstractmethod
    async def delete(self, thesis_id: int, user_id: int) -> None:
        """Delete reaction"""

    @abstractmethod
    async def retrieve_many_with_filter(
        self,
        query_params: post_reactions.PostsReactionsQueryParams,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[post_reactions.PostReactionInDB], int]:
        """Retrieve many reactions"""
