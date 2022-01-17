from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas import rationales


class IRationalesRepo(ABC):
    @abstractmethod
    async def create(self, thesis_id: int, user_id: int) -> rationales.RationaleInDb:
        """Create a rationale"""

    @abstractmethod
    async def retrieve_rationale_with_filter(
        self,
        rationale_id: Optional[int] = None,
        asset_symbol: Optional[str] = None,
        thesis_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Optional[rationales.ThesisWithRationaleId]:
        """Retrive a rationale"""

    @abstractmethod
    async def retrieve_many_rationales_with_filter(
        self,
        query_params: rationales.RationaleQueryRepoAdapter,
        page_number: int = 1,
        page_size: int = 200,
    ) -> List[rationales.ThesisWithRationaleId]:
        """Retrieve many rationales"""

    @abstractmethod
    async def delete(self, rationale_id: int) -> None:
        """Delete rationale"""
