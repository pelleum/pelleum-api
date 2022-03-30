from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.usecases.schemas import theses


class IThesesRepo(ABC):
    @abstractmethod
    async def create(self, thesis: theses.CreateThesisRepoAdapter) -> theses.ThesisInDB:
        pass

    @abstractmethod
    async def retrieve_thesis_with_filter(
        self,
        thesis_id: Optional[int] = None,
        user_id: Optional[str] = None,
        asset_symbol: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Optional[theses.ThesisInDB]:
        pass

    @abstractmethod
    async def retrieve_thesis_with_reaction(
        self, thesis_id: int, user_id: int
    ) -> Optional[theses.ThesisWithUserReaction]:
        """Retrieves a thesis with its corresponding user reaction"""

    @abstractmethod
    async def update(
        self,
        updated_thesis: theses.UpdateThesisRepoAdapter,
    ) -> theses.ThesisInDB:
        pass

    @abstractmethod
    async def retrieve_many_with_filter(
        self,
        query_params: theses.ThesesQueryRepoAdapter,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[theses.ThesisInDB], int]:
        pass

    @abstractmethod
    async def delete(self, thesis_id: int) -> None:
        """Delete a thesis. The models that reference thesis_id as a foreign
        key all have ondelete="cascade", so they should also get deleted."""
