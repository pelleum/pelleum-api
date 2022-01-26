from typing import List, Optional

import asyncpg
from databases import Database
from sqlalchemy import and_, delete, desc, func, select

from app.infrastructure.db.models.rationales import RATIONALES
from app.infrastructure.db.models.theses import THESES, THESES_REACTIONS
from app.libraries import pelleum_errors
from app.usecases.interfaces.rationales_repo import IRationalesRepo
from app.usecases.schemas import rationales


class RationalesRepo(IRationalesRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(
        self, thesis_id: int, user_id: int
    ) -> rationales.RationaleWithThesis:
        """Creates a rationale in the rationales table"""

        create_rationale_insert_stmt = RATIONALES.insert().values(
            thesis_id=thesis_id, user_id=user_id
        )

        try:
            newly_created_rationale_id = await self.db.execute(
                create_rationale_insert_stmt
            )
        except asyncpg.exceptions.UniqueViolationError:
            raise await pelleum_errors.PelleumErrors(
                detail="This thesis already exists in the user's rationale library."
            ).unique_constraint()

        return await self.retrieve_rationale_with_filter(
            rationale_id=newly_created_rationale_id
        )

    async def retrieve_rationale_with_filter(
        self,
        rationale_id: Optional[int] = None,
        asset_symbol: Optional[str] = None,
        thesis_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Optional[rationales.RationaleWithThesis]:
        """Retrieve a rationale by function parameters"""

        conditions = []

        if rationale_id:
            conditions.append(RATIONALES.c.rationale_id == rationale_id)

        if thesis_id:
            conditions.append(RATIONALES.c.thesis_id == thesis_id)

        if user_id:
            conditions.append(RATIONALES.c.user_id == user_id)

        if asset_symbol:
            conditions.append(THESES.c.asset_symbol == asset_symbol)

        if len(conditions) == 0:
            raise Exception(
                "Please pass a parameter to query by to the function, retrieve_user_with_filter()"
            )

        j = RATIONALES.join(THESES, RATIONALES.c.thesis_id == THESES.c.thesis_id)

        thesis_columns = [
            column.label("thesis_" + str(column).split(".")[1])
            for column in THESES.columns
        ]

        columns_to_select = [RATIONALES] + thesis_columns

        query = select(columns_to_select).select_from(j).where(and_(*conditions))

        result = await self.db.fetch_one(query)

        return rationales.RationaleWithThesis(**result) if result else None

    async def retrieve_many_rationales_with_filter(
        self,
        query_params: rationales.RationaleQueryRepoAdapter,
        page_number: int = 1,
        page_size: int = 200,
    ) -> List[rationales.RationaleWithThesis]:
        """Retrieve many rationales by function parameters"""

        conditions = []

        if query_params.thesis_id:
            conditions.append(RATIONALES.c.thesis_id == query_params.thesis_id)

        if query_params.user_id:
            conditions.append(RATIONALES.c.user_id == query_params.user_id)

        if query_params.asset_symbol:
            conditions.append(THESES.c.asset_symbol == query_params.asset_symbol)

        if query_params.sentiment:
            conditions.append((THESES.c.sentiment == query_params.sentiment))

        if len(conditions) == 0:
            raise Exception(
                "Please pass a parameter to query by to the function, retrieve_user_with_filter()"
            )

        j = RATIONALES.join(THESES, RATIONALES.c.thesis_id == THESES.c.thesis_id).join(
            THESES_REACTIONS,
            and_(
                THESES.c.thesis_id == THESES_REACTIONS.c.thesis_id,
                THESES_REACTIONS.c.user_id == query_params.user_id,
            ),
            isouter=True,
        )

        thesis_columns = [
            column.label("thesis_" + str(column).split(".")[1])
            for column in THESES.columns
        ]

        columns_to_select = [
            RATIONALES,
            THESES_REACTIONS.c.reaction.label("user_reaction_value"),
        ] + thesis_columns

        query = (
            select(columns_to_select)
            .select_from(j)
            .where(and_(*conditions))
            .limit(page_size)
            .offset((page_number - 1) * page_size)
            .order_by(desc(RATIONALES.c.created_at))
        )

        query_count = select([func.count()]).select_from(j).where(and_(*conditions))

        async with self.db.transaction():
            query_results = await self.db.fetch_all(query)
            count_results = await self.db.fetch_all(query_count)

        rationales_list = [
            rationales.RationaleWithThesis(**result) for result in query_results
        ]
        rationales_count = count_results[0][0]

        return rationales_list, rationales_count

    async def delete(self, rationale_id: int) -> None:
        """Deletes a rationale"""

        delete_statement = delete(RATIONALES).where(
            RATIONALES.c.rationale_id == rationale_id
        )

        await self.db.execute(delete_statement)
