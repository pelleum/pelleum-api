from app.usecases.interfaces.posts_repo import IPostsRepo
from databases import Database
from app.usecases.schemas import posts
from app.infrastructure.db.models.posts import POSTS
from sqlalchemy import and_, desc, func, select, delete
from typing import List, Tuple


class PostsRepo(IPostsRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, new_feed_post: posts.CreatePostRepoAdapter) -> None:

        create_post_insert_stmt = POSTS.insert().values(
            user_id=new_feed_post.user_id,
            thesis_id=new_feed_post.thesis_id,
            title=new_feed_post.title,
            content=new_feed_post.content,
            asset_symbol=new_feed_post.asset_symbol,
            sentiment=new_feed_post.sentiment,
        )

        await self.db.execute(create_post_insert_stmt)

    async def retrieve_post_with_filter(
        self,
        post_id: int = None,
        thesis_id: int = None,
        user_id: str = None,
        asset_symbol: str = None,
    ) -> posts.PostInDB:

        conditions = []

        if post_id:
            conditions.append(POSTS.c.post_id == post_id)

        if thesis_id:
            conditions.append(POSTS.c.thesis_id == thesis_id)

        if user_id:
            conditions.append(POSTS.c.user_id == user_id)

        if asset_symbol:
            conditions.append(POSTS.c.asset_symbol == asset_symbol)

        if len(conditions) > 0:
            query = POSTS.select().where(and_(*conditions))

            result = await self.db.fetch_one(query)
            if result:
                return posts.PostInDB(**result)
        raise Exception(
            "Please pass a condition parameter to query by to the function, retrieve_post_with_filter()"
        )

    async def retrieve_many_with_filter(
        self,
        query_params: posts.PostQueryParams,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[posts.PostInDB], int]:

        conditions = []

        if query_params.user_id:
            conditions.append(POSTS.c.user_id == query_params.user_id)

        if query_params.asset_symbol:
            conditions.append(POSTS.c.asset_symbol == query_params.asset_symbol)

        if query_params.sentiment:
            conditions.append(POSTS.c.sentiment == query_params.sentiment)

        if len(conditions) > 0:
            query = (
                POSTS.select()
                .where(and_(*conditions))
                .limit(page_size)
                .offset((page_number - 1) * page_size)
                .order_by(desc(POSTS.c.created_at))
            )

            query_count = (
                select([func.count()]).select_from(POSTS).where(and_(*conditions))
            )

            async with self.db.transaction():
                query_results = await self.db.fetch_all(query)
                count_results = await self.db.fetch_all(query_count)

            theses_list = [posts.PostInDB(**result) for result in query_results]
            theses_count = count_results[0][0]

            return theses_list, theses_count
        raise Exception(
            "Please pass a condition parameter to query by to the function, retrieve_many_with_filter()"
        )

    async def delete(self, post_id) -> None:

        delete_statement = delete(POSTS).where(POSTS.c.post_id == post_id)

        await self.db.execute(delete_statement)
