from abc import ABC, abstractmethod
from typing import List, Tuple

from app.usecases.schemas import theses


class IThesesRepo(ABC):
    @abstractmethod
    async def create(self, thesis: theses.CreateThesisRepoAdapter) -> theses.ThesisInDB:
        pass

    @abstractmethod
    async def retrieve_thesis_with_filter(
        self,
        thesis_id: int = None,
        user_id: str = None,
        asset_symbol: str = None,
        title: str = None,
    ) -> theses.ThesisInDB:
        pass

    @abstractmethod
    async def update(
        self,
        updated_thesis: theses.UpdateThesisRepoAdapter,
    ) -> theses.ThesisInDB:
        pass

    @abstractmethod
    async def retrieve_many_with_filter(
        self,
        query_params: theses.ThesesQueryParams,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[theses.ThesisInDB], int]:
        pass
