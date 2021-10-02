from typing import List, Tuple, Union

import asyncpg
from sqlalchemy import and_, desc, func, select
from databases import Database

from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.schemas import theses
from app.infrastructure.db.models.theses import THESES, THESES_REACTIONS
from app.libraries import pelleum_errors


class ThesesRepo(IThesesRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, thesis: theses.CreateThesisRepoAdapter) -> theses.ThesisInDB:

        create_thesis_insert_stmt = THESES.insert().values(
            user_id=thesis.user_id,
            title=thesis.title,
            content=thesis.content,
            sources=thesis.sources,
            asset_symbol=thesis.asset_symbol,
            sentiment=thesis.sentiment,
            is_authors_current=True,
        )

        try:
            await self.db.execute(create_thesis_insert_stmt)
        except asyncpg.exceptions.UniqueViolationError:
            raise await pelleum_errors.UniqueConstraint(
                detail="A thesis with this title already exists on your account. Please choose a new title."
            ).unique_constraint()

        return await self.retrieve_thesis_with_filter(
            user_id=thesis.user_id, title=thesis.title
        )

    async def retrieve_thesis_with_filter(
        self,
        thesis_id: int = None,
        user_id: str = None,
        asset_symbol: str = None,
        title: str = None,
    ) -> Union[theses.ThesisInDB, None]:

        conditions = []

        if thesis_id:
            conditions.append(THESES.c.thesis_id == thesis_id)

        if user_id:
            conditions.append(THESES.c.user_id == user_id)

        if asset_symbol:
            conditions.append(THESES.c.asset_symbol == asset_symbol)

        if title:
            conditions.append(THESES.c.title == title)

        if len(conditions) > 0:
            query = THESES.select().where(and_(*conditions))

            result = await self.db.fetch_one(query)
            return theses.ThesisInDB(**result) if result else None
        raise Exception(
            "Please pass a condition parameter to query by to the function, retrieve_thesis_with_filter()"
        )

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
        query_params: theses.ThesesQueryParams,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[theses.ThesisInDB], int]:

        conditions = []

        if query_params.user_id:
            conditions.append(THESES.c.user_id == query_params.user_id)

        if query_params.asset_symbol:
            conditions.append(THESES.c.asset_symbol == query_params.asset_symbol)

        if query_params.sentiment:
            conditions.append(THESES.c.sentiment == query_params.sentiment)

        if len(conditions) > 0:
            query = (
                THESES.select()
                .where(and_(*conditions))
                .limit(page_size)
                .offset((page_number - 1) * page_size)
                .order_by(desc(THESES.c.created_at))
            )

            query_count = (
                select([func.count()]).select_from(THESES).where(and_(*conditions))
            )

            async with self.db.transaction():
                query_results = await self.db.fetch_all(query)
                count_results = await self.db.fetch_all(query_count)

            theses_list = [theses.ThesisInDB(**result) for result in query_results]
            theses_count = count_results[0][0]

            return theses_list, theses_count
        raise Exception(
            "Please pass a condition parameter to query by to the function, retrieve_many_with_filter()"
        )
