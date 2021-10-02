from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from app.usecases.schemas import posts


class IPostsRepo(ABC):
    @abstractmethod
    async def create(self, new_feed_post: posts.CreatePostRepoAdapter) -> None:
        pass

    @abstractmethod
    async def retrieve_post_with_filter(
        self,
        post_id: int = None,
        thesis_id: int = None,
        user_id: str = None,
        asset_symbol: str = None,
    ) -> Union[posts.PostInDB, None]:
        pass

    @abstractmethod
    async def retrieve_many_with_filter(
        self,
        query_params: posts.PostQueryParams,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[posts.PostInDB], int]:
        pass

    @abstractmethod
    async def delete(self, post_id) -> None:
        pass
