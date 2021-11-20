from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.user_repo import UsersRepo

from app.infrastructure.db.repos.theses_repo import ThesesRepo
from app.infrastructure.db.repos.thesis_reaction_repo import ThesisReactionRepo
from app.infrastructure.db.repos.thesis_comments_repo import ThesesCommentsRepo
from app.infrastructure.db.repos.posts_repo import PostsRepo
from app.infrastructure.db.repos.post_reaction_repo import PostReactionRepo
from app.infrastructure.db.repos.post_comments_repo import PostsCommentsRepo
from app.infrastructure.db.repos.portfolio_repo import PortfolioRepo

from app.usecases.interfaces.portfolio_repo import IPortfolioRepo
from app.usecases.interfaces.post_comments_repo import IPostsCommentsRepo
from app.usecases.interfaces.post_reaction_repo import IPostReactionRepo
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.interfaces.thesis_comments_repo import IThesesCommentsRepo
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.interfaces.user_repo import IUserRepo


async def get_users_repo() -> IUserRepo:
    database = await get_or_create_database()
    return UsersRepo(db=database)


async def get_theses_repo() -> IThesesRepo:
    database = await get_or_create_database()
    return ThesesRepo(db=database)


async def get_posts_repo() -> IPostsRepo:
    database = await get_or_create_database()
    return PostsRepo(db=database)


async def get_thesis_reactions_repo() -> ThesisReactionRepo:
    database = await get_or_create_database()
    return ThesisReactionRepo(db=database)


async def get_post_reactions_repo() -> IPostReactionRepo:
    database = await get_or_create_database()
    return PostReactionRepo(db=database)


async def get_thesis_comments_repo() -> IThesesCommentsRepo:
    database = await get_or_create_database()
    return ThesesCommentsRepo(db=database)


async def get_post_comments_repo() -> IPostsCommentsRepo:
    database = await get_or_create_database()
    return PostsCommentsRepo(db=database)


async def get_portfolio_repo() -> IPortfolioRepo:
    database = await get_or_create_database()
    return PortfolioRepo(db=database)
