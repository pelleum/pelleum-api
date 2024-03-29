from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.usecases.schemas import thesis_reactions


class IThesisReactionRepo(ABC):
    @abstractmethod
    async def create(
        self, thesis_reaction: thesis_reactions.ThesisReactionRepoAdapter
    ) -> None:
        """Create reaction"""

    @abstractmethod
    async def update(
        self, thesis_reaction_update: thesis_reactions.ThesisReactionRepoAdapter
    ) -> None:
        """Update reaction"""

    @abstractmethod
    async def delete(self, thesis_id: int, user_id: int) -> None:
        """Delete reaction"""

    @abstractmethod
    async def retrieve_many_with_filter(
        self,
        query_params: thesis_reactions.ThesisReactionsQueryParams,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[thesis_reactions.ThesisReactionInDB], int]:
        """Retrieve many reactions"""

    @abstractmethod
    async def retrieve_single(
        self, thesis_id: int, user_id: int
    ) -> Optional[thesis_reactions.ThesisReactionInDB]:
        """Retrieves single thesis reaction"""
