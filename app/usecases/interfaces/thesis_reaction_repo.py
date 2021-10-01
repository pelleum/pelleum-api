from abc import ABC, abstractmethod
from typing import List

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
    ) -> List[thesis_reactions.ThesisReactionInDB]:
        """Retrieve many reactions"""
