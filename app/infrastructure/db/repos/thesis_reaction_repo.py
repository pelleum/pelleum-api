from typing import List, Optional, Tuple

import asyncpg
from databases import Database
from sqlalchemy import and_, between, delete, desc, func, select

from app.infrastructure.db.models.theses import THESES, THESES_REACTIONS
from app.libraries import pelleum_errors
from app.usecases.interfaces.thesis_reaction_repo import IThesisReactionRepo
from app.usecases.schemas import thesis_reactions


class ThesisReactionRepo(IThesisReactionRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(
        self, thesis_reaction: thesis_reactions.ThesisReactionRepoAdapter
    ) -> None:
        """Create reaction"""

        insert_statement = THESES_REACTIONS.insert().values(
            thesis_id=thesis_reaction.thesis_id,
            user_id=thesis_reaction.user_id,
            reaction=thesis_reaction.reaction,
        )

        try:
            await self.db.execute(insert_statement)
        except asyncpg.exceptions.UniqueViolationError:
            raise await pelleum_errors.PelleumErrors(
                detail="User has already liked this thesis."
            ).unique_constraint()

    async def update(
        self, thesis_reaction_update: thesis_reactions.ThesisReactionRepoAdapter
    ) -> None:
        """Update reaction"""

        update_statement = (
            THESES_REACTIONS.update()
            .values(reaction=thesis_reaction_update.reaction)
            .where(
                and_(
                    THESES_REACTIONS.c.user_id == thesis_reaction_update.user_id,
                    THESES_REACTIONS.c.thesis_id == thesis_reaction_update.thesis_id,
                )
            )
        )

        await self.db.execute(update_statement)

    async def delete(self, thesis_id: int, user_id: int) -> None:
        """Delete reaction"""

        delete_statement = delete(THESES_REACTIONS).where(
            and_(
                THESES_REACTIONS.c.user_id == user_id,
                THESES_REACTIONS.c.thesis_id == thesis_id,
            )
        )

        await self.db.execute(delete_statement)

    async def retrieve_many_with_filter(
        self,
        query_params: thesis_reactions.ThesisReactionsQueryParams,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[thesis_reactions.ThesisReactionInDB], int]:
        """Retrieve many reactions"""

        conditions = []

        if query_params.user_id:
            conditions.append(THESES_REACTIONS.c.user_id == query_params.user_id)

        if query_params.thesis_id:
            conditions.append(THESES_REACTIONS.c.thesis_id == query_params.thesis_id)

        if query_params.reaction:
            conditions.append(THESES_REACTIONS.c.reaction == query_params.reaction)

        if query_params.time_range:
            conditions.append(
                between(
                    THESES.c.created_at,
                    query_params.time_range.start_time,
                    query_params.time_range.end_time,
                )
            )

        if len(conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve_many_with_filter()"
            )

        j = THESES_REACTIONS.join(
            THESES, THESES_REACTIONS.c.thesis_id == THESES.c.thesis_id
        )

        query = (
            select([THESES_REACTIONS])
            .select_from(j)
            .where(and_(*conditions))
            .limit(page_size)
            .offset((page_number - 1) * page_size)
            .order_by(desc(THESES_REACTIONS.c.created_at))
        )

        query_count = select([func.count()]).select_from(j).where(and_(*conditions))

        async with self.db.transaction():
            query_results = await self.db.fetch_all(query)
            count_results = await self.db.fetch_all(query_count)

        theses_reactions_list = [
            thesis_reactions.ThesisReactionInDB(**result) for result in query_results
        ]
        theses_reactions_count = count_results[0][0]

        return theses_reactions_list, theses_reactions_count

    async def retrieve_single(
        self, thesis_id: int, user_id: int
    ) -> Optional[thesis_reactions.ThesisReactionInDB]:
        """Retrieves single thesis reaction"""

        query = THESES_REACTIONS.select().where(
            and_(
                THESES_REACTIONS.c.thesis_id == thesis_id,
                THESES_REACTIONS.c.user_id == user_id,
            )
        )

        result = await self.db.fetch_one(query)
        return thesis_reactions.ThesisReactionInDB(**result) if result else None
