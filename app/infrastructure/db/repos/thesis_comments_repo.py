from typing import List, Tuple

from databases import Database
from sqlalchemy import and_, desc, func, select, delete

from app.usecases.interfaces.thesis_comments_repo import IThesesCommentsRepo
from app.usecases.schemas import thesis_comments
from app.infrastructure.db.models.theses import THESES_COMMENTS


class ThesesCommentsRepo(IThesesCommentsRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, thesis_id: int, user_id: int, content: str) -> None:
        """Saves a new thesis comment"""

        thesis_comment_insert_statement = THESES_COMMENTS.insert().values(
            thesis_id=thesis_id, user_id=user_id, content=content
        )

        await self.db.execute(thesis_comment_insert_statement)

    async def retrieve_thesis_comment_by_id(
        self, comment_id: int
    ) -> thesis_comments.ThesisCommentInDB:
        """Retrieves on comment by comment_id"""

        query = THESES_COMMENTS.select().where(
            THESES_COMMENTS.c.comment_id == comment_id
        )

        result = await self.db.fetch_one(query)
        if result:
            return thesis_comments.ThesisCommentInDB(**result)

    async def update(self, content: str, comment_id: int) -> None:
        """Update a comment by comment_id"""

        comment_update_statemnent = (
            THESES_COMMENTS.update()
            .values(content=content)
            .where(THESES_COMMENTS.c.comment_id == comment_id)
        )

        await self.db.execute(comment_update_statemnent)

    async def retrieve_many_with_filter(
        self,
        query_params: thesis_comments.ThesisCommentsQueryParams,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[thesis_comments.ThesisCommentInDB], int]:
        """Retrieve many thesis comments with filter"""

        conditions = []

        if query_params.user_id:
            conditions.append(THESES_COMMENTS.c.user_id == query_params.user_id)

        if query_params.thesis_id:
            conditions.append(THESES_COMMENTS.c.thesis_id == query_params.thesis_id)

        if len(conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve_many_with_filter()"
            )
        query = (
            THESES_COMMENTS.select()
            .where(and_(*conditions))
            .limit(page_size)
            .offset((page_number - 1) * page_size)
            .order_by(desc(THESES_COMMENTS.c.created_at))
        )

        query_count = (
            select([func.count()]).select_from(THESES_COMMENTS).where(and_(*conditions))
        )

        async with self.db.transaction():
            query_results = await self.db.fetch_all(query)
            count_results = await self.db.fetch_all(query_count)

        thesis_comments_list = [
            thesis_comments.ThesisCommentInDB(**result) for result in query_results
        ]
        thesis_comments_count = count_results[0][0]

        return thesis_comments_list, thesis_comments_count

    async def delete(self, comment_id: int) -> None:
        """Deletes a thesis comment by comment_id"""

        delete_statement = delete(THESES_COMMENTS).where(
            THESES_COMMENTS.c.comment_id == comment_id
        )

        await self.db.execute(delete_statement)
