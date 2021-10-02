from typing import List, Tuple

from databases import Database
from sqlalchemy import and_, desc, func, select, delete

from app.usecases.interfaces.post_comments_repo import IPostsCommentsRepo
from app.usecases.schemas import post_comments
from app.infrastructure.db.models.posts import POST_COMMENTS


class PostsCommentsRepo(IPostsCommentsRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, post_id: int, user_id: int, content: str) -> None:
        """Saves a new post comment"""

        post_comment_insert_statement = POST_COMMENTS.insert().values(
            post_id=post_id, user_id=user_id, content=content
        )

        await self.db.execute(post_comment_insert_statement)

    async def retrieve_post_comment_by_id(
        self, comment_id: int
    ) -> post_comments.PostCommentInDB:
        """Retrieves on comment by comment_id"""

        query = POST_COMMENTS.select().where(POST_COMMENTS.c.comment_id == comment_id)

        result = await self.db.fetch_one(query)
        if result:
            return post_comments.PostCommentInDB(**result)

    async def update(self, content: str, comment_id: int) -> None:
        """Update a comment by comment_id"""

        comment_update_statemnent = (
            POST_COMMENTS.update()
            .values(content=content)
            .where(POST_COMMENTS.c.comment_id == comment_id)
        )

        await self.db.execute(comment_update_statemnent)

    async def retrieve_many_with_filter(
        self,
        query_params: post_comments.PostsCommentsQueryParams,
        page_number: int = 1,
        page_size: int = 200,
    ) -> Tuple[List[post_comments.PostCommentInDB], int]:
        """Retrieve many post comments with filter"""

        conditions = []

        if query_params.user_id:
            conditions.append(POST_COMMENTS.c.user_id == query_params.user_id)

        if query_params.post_id:
            conditions.append(POST_COMMENTS.c.post_id == query_params.post_id)

        if len(conditions) > 0:
            query = (
                POST_COMMENTS.select()
                .where(and_(*conditions))
                .limit(page_size)
                .offset((page_number - 1) * page_size)
                .order_by(desc(POST_COMMENTS.c.created_at))
            )

            query_count = (
                select([func.count()])
                .select_from(POST_COMMENTS)
                .where(and_(*conditions))
            )

            async with self.db.transaction():
                query_results = await self.db.fetch_all(query)
                count_results = await self.db.fetch_all(query_count)

            post_comments_list = [
                post_comments.PostCommentInDB(**result) for result in query_results
            ]
            post_comments_count = count_results[0][0]

            return post_comments_list, post_comments_count
        raise Exception(
            "Please pass a condition parameter to query by to the function, retrieve_many_with_filter()"
        )

    async def delete(self, comment_id: int) -> None:
        """Deletes a post comment by comment_id"""

        delete_statement = delete(POST_COMMENTS).where(
            POST_COMMENTS.c.comment_id == comment_id
        )

        await self.db.execute(delete_statement)
