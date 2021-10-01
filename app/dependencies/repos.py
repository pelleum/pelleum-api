from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.user_repo import UsersRepo
from app.infrastructure.db.repos.theses_repo import ThesesRepo
from app.infrastructure.db.repos.posts_repo import PostsRepo
from app.infrastructure.db.repos.thesis_reaction_repo import ThesisReactionRepo
from app.infrastructure.db.repos.post_reaction_repo import PostReactionRepo


async def get_users_repo():
    database = await get_or_create_database()
    return UsersRepo(db=database)


async def get_theses_repo():
    database = await get_or_create_database()
    return ThesesRepo(db=database)


async def get_posts_repo():
    database = await get_or_create_database()
    return PostsRepo(db=database)


async def get_thesis_reactions_repo():
    database = await get_or_create_database()
    return ThesisReactionRepo(db=database)


async def get_post_reactions_repo():
    database = await get_or_create_database()
    return PostReactionRepo(db=database)
