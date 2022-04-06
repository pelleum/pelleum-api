from typing import List, Optional, Tuple

import asyncpg
from databases import Database
from sqlalchemy import and_, delete, desc, func, select

from app.infrastructure.db.models.public.rationales import RATIONALES
from app.infrastructure.db.models.public.theses import THESES, THESES_REACTIONS
from app.libraries import pelleum_errors
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.schemas import theses


class ThesesRepo(IThesesRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, thesis: theses.CreateThesisRepoAdapter) -> theses.ThesisInDB:

        create_thesis_insert_stmt = THESES.insert().values(
            user_id=thesis.user_id,
            username=thesis.username,
            title=thesis.title,
            content=thesis.content,
            sources=thesis.sources,
            asset_symbol=thesis.asset_symbol,
            sentiment=thesis.sentiment,
            is_authors_current=True,
        )

        try:
            thesis_id = await self.db.execute(create_thesis_insert_stmt)
        except asyncpg.exceptions.UniqueViolationError:
            raise await pelleum_errors.PelleumErrors(
                detail="A thesis with this title already exists on your account. Please choose a new title."
            ).unique_constraint()

        return await self.retrieve_thesis_with_filter(thesis_id=thesis_id)

    async def retrieve_thesis_with_filter(
        self,
        thesis_id: Optional[int] = None,
        user_id: Optional[str] = None,
        asset_symbol: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Optional[theses.ThesisInDB]:
        """Retrieve Thesis object from database"""

        conditions = []

        if thesis_id:
            conditions.append(THESES.c.thesis_id == thesis_id)

        if user_id:
            conditions.append(THESES.c.user_id == user_id)

        if asset_symbol:
            conditions.append(THESES.c.asset_symbol == asset_symbol)

        if title:
            conditions.append(THESES.c.title == title)

        if len(conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve_thesis_with_filter()"
            )

        query = THESES.select().where(and_(*conditions))

        result = await self.db.fetch_one(query)
        return theses.ThesisInDB(**result) if result else None

    async def retrieve_thesis_with_reaction(
        self, thesis_id: int, user_id: int
    ) -> Optional[theses.ThesisWithInteractionData]:
        """Retrieves a thesis with its corresponding user reaction"""

        j = THESES.join(
            THESES_REACTIONS,
            and_(
                THESES.c.thesis_id == THESES_REACTIONS.c.thesis_id,
                THESES_REACTIONS.c.user_id == user_id,
            ),
            isouter=True,
        )

        thesis_query = (
            select([THESES, THESES_REACTIONS.c.reaction.label("user_reaction_value")])
            .select_from(j)
            .where(THESES.c.thesis_id == thesis_id)
            .subquery()
        )

        # Gets number of likes per post
        likes_count_query = (
            select([func.count(THESES_REACTIONS.table_valued())])
            .where(and_(
                THESES_REACTIONS.c.thesis_id == thesis_query.c.thesis_id,
                THESES_REACTIONS.c.reaction == 1
                )   
            )
            .scalar_subquery()
            .label("like_count")
        )

        # Gets number of dislikes per post
        dislikes_count_query = (
            select([func.count(THESES_REACTIONS.table_valued())])
            .where(and_(
                THESES_REACTIONS.c.thesis_id == thesis_query.c.thesis_id,
                THESES_REACTIONS.c.reaction == -1
                )
            )
            .scalar_subquery()
            .label("dislike_count")
        )

        # Gets number of comments per post
        save_count_query = (
            select([func.count(RATIONALES.table_valued())])
            .where(RATIONALES.c.thesis_id == thesis_query.c.thesis_id)
            .scalar_subquery()
            .label("save_count")
        )

        compiled_query = select(
            [thesis_query, likes_count_query, dislikes_count_query, save_count_query]
        )

        query_result = await self.db.fetch_one(compiled_query)

        return theses.ThesisWithInteractionData(**query_result) if query_result else None

    async def update(
        self,
        updated_thesis: theses.UpdateThesisRepoAdapter,
    ) -> theses.ThesisInDB:

        query = THESES.update()

        updated_thesis_raw = updated_thesis.dict()
        update_thesis_dict = {}

        for key, value in updated_thesis_raw.items():
            if value is not None:
                update_thesis_dict[key] = value

        query = query.values(update_thesis_dict)

        user_update_stmt = query.where(THESES.c.thesis_id == updated_thesis.thesis_id)

        await self.db.execute(user_update_stmt)

        return await self.retrieve_thesis_with_filter(
            thesis_id=updated_thesis.thesis_id
        )

    async def retrieve_many_with_filter(
        self,
        query_params: theses.ThesesQueryRepoAdapter,
        user_id: int,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[theses.ThesisWithInteractionData], int]:

        conditions = []

        if query_params.user_id:
            conditions.append(THESES.c.user_id == query_params.user_id)

        if query_params.asset_symbol:
            conditions.append(THESES.c.asset_symbol == query_params.asset_symbol)

        if query_params.sentiment:
            conditions.append(THESES.c.sentiment == query_params.sentiment)

        j = THESES.join(
            THESES_REACTIONS,
            and_(
                THESES.c.thesis_id == THESES_REACTIONS.c.thesis_id,
                THESES_REACTIONS.c.user_id == user_id,
            ),
            isouter=True,
        )

        # Gets posts
        theses_query = (
            select([THESES, THESES_REACTIONS.c.reaction.label("user_reaction_value")])
            .select_from(j)
            .where(and_(*conditions))
            .limit(page_size)
            .offset((page_number - 1) * page_size)
            .order_by(desc(THESES.c.created_at))
            .subquery()
        )

        # Gets number of likes per post
        likes_count_query = (
            select([func.count(THESES_REACTIONS.table_valued())])
            .where(and_(
                THESES_REACTIONS.c.thesis_id == theses_query.c.thesis_id,
                THESES_REACTIONS.c.reaction == 1
                )   
            )
            .scalar_subquery()
            .label("like_count")
        )

        # Gets number of dislikes per post
        dislikes_count_query = (
            select([func.count(THESES_REACTIONS.table_valued())])
            .where(and_(
                THESES_REACTIONS.c.thesis_id == theses_query.c.thesis_id,
                THESES_REACTIONS.c.reaction == -1
                )
            )
            .scalar_subquery()
            .label("dislike_count")
        )

        # Gets number of comments per post
        save_count_query = (
            select([func.count(RATIONALES.table_valued())])
            .where(RATIONALES.c.thesis_id == theses_query.c.thesis_id)
            .scalar_subquery()
            .label("save_count")
        )

        compiled_query = select(
            [theses_query, likes_count_query, dislikes_count_query, save_count_query]
        )

        query_count = (
            select([func.count()]).select_from(THESES).where(and_(*conditions))
        )

        async with self.db.transaction():
            query_results = await self.db.fetch_all(compiled_query)
            count_results = await self.db.fetch_all(query_count)

        theses_list = [theses.ThesisWithInteractionData(**result) for result in query_results]
        theses_count = count_results[0][0]

        return theses_list, theses_count

    async def delete(self, thesis_id: int) -> None:
        """Delete a thesis. The models that reference thesis_id as a foreign
        key all have ondelete="cascade", so they should also get deleted."""

        delete_statement = delete(THESES).where(THESES.c.thesis_id == thesis_id)

        await self.db.execute(delete_statement)
