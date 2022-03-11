from typing import List, Tuple

import asyncpg
from databases import Database
from sqlalchemy import and_, between, delete, desc, func, select

from app.infrastructure.db.models.public.posts import POST_REACTIONS, POSTS
from app.libraries import pelleum_errors
from app.usecases.interfaces.post_reaction_repo import IPostReactionRepo
from app.usecases.schemas import post_reactions


class PostReactionRepo(IPostReactionRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(
        self, post_reaction: post_reactions.PostReactionRepoAdapter
    ) -> None:
        """Create reaction"""

        insert_statement = POST_REACTIONS.insert().values(
            post_id=post_reaction.post_id,
            user_id=post_reaction.user_id,
            reaction=post_reaction.reaction,
        )

        try:
            await self.db.execute(insert_statement)
        except asyncpg.exceptions.UniqueViolationError:
            raise await pelleum_errors.PelleumErrors(
                detail="User has already liked this post."
            ).unique_constraint()

    async def delete(self, post_id: int, user_id: int) -> None:
        """Delete reaction"""

        delete_statement = delete(POST_REACTIONS).where(
            and_(
                POST_REACTIONS.c.user_id == user_id,
                POST_REACTIONS.c.post_id == post_id,
            )
        )

        await self.db.execute(delete_statement)

    async def retrieve_many_with_filter(
        self,
        query_params: post_reactions.PostsReactionsQueryParams,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[post_reactions.PostReactionInDB], int]:
        """Retrieve many reactions"""

        conditions = []

        if query_params.user_id:
            conditions.append(POST_REACTIONS.c.user_id == query_params.user_id)

        if query_params.post_id:
            conditions.append(POST_REACTIONS.c.post_id == query_params.post_id)

        if query_params.reaction:
            conditions.append(POST_REACTIONS.c.reaction == query_params.reaction)

        if query_params.time_range:
            conditions.append(
                between(
                    POSTS.c.created_at,
                    query_params.time_range.start_time,
                    query_params.time_range.end_time,
                )
            )

        if len(conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve_many_with_filter()"
            )

        j = POST_REACTIONS.join(POSTS, POST_REACTIONS.c.post_id == POSTS.c.post_id)

        query = (
            select([POST_REACTIONS])
            .select_from(j)
            .where(and_(*conditions))
            .limit(page_size)
            .offset((page_number - 1) * page_size)
            .order_by(desc(POST_REACTIONS.c.created_at))
        )

        query_count = select([func.count()]).select_from(j).where(and_(*conditions))

        async with self.db.transaction():
            query_results = await self.db.fetch_all(query)
            count_results = await self.db.fetch_all(query_count)

        posts_reactions_list = [
            post_reactions.PostReactionInDB(**result) for result in query_results
        ]
        posts_reactions_count = count_results[0][0]

        return posts_reactions_list, posts_reactions_count
