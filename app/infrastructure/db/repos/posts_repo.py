from typing import List, Optional, Tuple

from databases import Database
from sqlalchemy import and_, delete, desc, func, select

from app.infrastructure.db.models.public.posts import POST_REACTIONS, POSTS
from app.infrastructure.db.models.public.theses import THESES
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.schemas import posts


class PostsRepo(IPostsRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, new_post: posts.CreatePostRepoAdapter) -> posts.PostInDB:
        """Create Post"""

        create_post_insert_stmt = POSTS.insert().values(
            user_id=new_post.user_id,
            username=new_post.username,
            thesis_id=new_post.thesis_id,
            title=new_post.title,
            content=new_post.content,
            asset_symbol=new_post.asset_symbol,
            sentiment=new_post.sentiment,
            is_post_comment_on=new_post.is_post_comment_on,
            is_thesis_comment_on=new_post.is_thesis_comment_on,
        )
        post_id = await self.db.execute(create_post_insert_stmt)
        return await self.retrieve_post_with_filter(post_id=post_id)

    async def retrieve_post_with_filter(
        self,
        post_id: int = None,
        thesis_id: int = None,
        user_id: str = None,
        asset_symbol: str = None,
    ) -> Optional[posts.PostInfoFromDB]:
        """Retrieve post."""

        conditions = []

        if post_id:
            conditions.append(POSTS.c.post_id == post_id)

        if thesis_id:
            conditions.append(POSTS.c.thesis_id == thesis_id)

        if user_id:
            conditions.append(POSTS.c.user_id == user_id)

        if asset_symbol:
            conditions.append(POSTS.c.asset_symbol == asset_symbol)

        if len(conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve_post_with_filter()"
            )

        j = POSTS.join(
            THESES,
            POSTS.c.thesis_id == THESES.c.thesis_id,
            isouter=True,
        )

        thesis_columns = [
            column.label("thesis_" + str(column).split(".")[1])
            for column in THESES.columns
        ]

        columns_to_select = [POSTS] + thesis_columns

        query = select(columns_to_select).select_from(j).where(and_(*conditions))

        result = await self.db.fetch_one(query)
        return posts.PostInfoFromDB(**result) if result else None

    async def retrieve_many_with_filter(
        self,
        query_params: posts.PostQueryRepoAdapter,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[posts.PostInfoFromDB], int]:
        """Retrieve many posts based on filter."""

        conditions = []

        if query_params.user_id:
            conditions.append(POSTS.c.user_id == query_params.user_id)

        if query_params.asset_symbol:
            conditions.append(POSTS.c.asset_symbol == query_params.asset_symbol)

        if query_params.sentiment:
            conditions.append(POSTS.c.sentiment == query_params.sentiment)

        if query_params.is_post_comment_on:
            conditions.append(
                POSTS.c.is_post_comment_on == query_params.is_post_comment_on
            )

        if query_params.is_thesis_comment_on:
            conditions.append(
                POSTS.c.is_thesis_comment_on == query_params.is_thesis_comment_on
            )

        j = POSTS.join(
            THESES,
            POSTS.c.thesis_id == THESES.c.thesis_id,
            isouter=True,
        ).join(
            POST_REACTIONS,
            and_(
                POSTS.c.post_id == POST_REACTIONS.c.post_id,
                POST_REACTIONS.c.user_id == query_params.requesting_user_id,
            ),
            isouter=True,
        )

        thesis_columns = [
            column.label("thesis_" + str(column).split(".")[1])
            for column in THESES.columns
        ]

        columns_to_select = [
            POSTS,
            POST_REACTIONS.c.reaction.label("user_reaction_value"),
        ] + thesis_columns

        query = (
            select(columns_to_select)
            .select_from(j)
            .where(and_(*conditions))
            .limit(page_size)
            .offset((page_number - 1) * page_size)
            .order_by(desc(POSTS.c.created_at))
        )

        query_count = select([func.count()]).select_from(j).where(and_(*conditions))

        async with self.db.transaction():
            query_results = await self.db.fetch_all(query)
            count_results = await self.db.fetch_all(query_count)

        theses_list = [posts.PostInfoFromDB(**result) for result in query_results]
        theses_count = count_results[0][0]

        return theses_list, theses_count

    async def delete(self, post_id: int) -> None:
        """Delete a post."""

        delete_statement = delete(POSTS).where(POSTS.c.post_id == post_id)

        await self.db.execute(delete_statement)
