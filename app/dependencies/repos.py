from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.notifications_repo import NotificationsRepo
from app.infrastructure.db.repos.portfolio_repo import PortfolioRepo
from app.infrastructure.db.repos.post_reaction_repo import PostReactionRepo
from app.infrastructure.db.repos.posts_repo import PostsRepo
from app.infrastructure.db.repos.rationales_repo import RationalesRepo
from app.infrastructure.db.repos.subscriptions_repo import SubscriptionsRepo
from app.infrastructure.db.repos.theses_repo import ThesesRepo
from app.infrastructure.db.repos.thesis_reaction_repo import ThesisReactionRepo
from app.infrastructure.db.repos.user_repo import UsersRepo
from app.usecases.interfaces.notifications_repo import INotificationsRepo
from app.usecases.interfaces.portfolio_repo import IPortfolioRepo
from app.usecases.interfaces.post_reaction_repo import IPostReactionRepo
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.interfaces.rationales_repo import IRationalesRepo
from app.usecases.interfaces.subscriptions_repo import ISubscriptionsRepo
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.interfaces.user_repo import IUsersRepo


async def get_users_repo() -> IUsersRepo:
    return UsersRepo(db=await get_or_create_database())


async def get_theses_repo() -> IThesesRepo:
    return ThesesRepo(db=await get_or_create_database())


async def get_posts_repo() -> IPostsRepo:
    return PostsRepo(db=await get_or_create_database())


async def get_thesis_reactions_repo() -> ThesisReactionRepo:
    return ThesisReactionRepo(db=await get_or_create_database())


async def get_post_reactions_repo() -> IPostReactionRepo:
    return PostReactionRepo(db=await get_or_create_database())


async def get_portfolio_repo() -> IPortfolioRepo:
    return PortfolioRepo(db=await get_or_create_database())


async def get_rationales_repo() -> IRationalesRepo:
    return RationalesRepo(db=await get_or_create_database())


async def get_subscriptions_repo() -> ISubscriptionsRepo:
    return SubscriptionsRepo(db=await get_or_create_database())


async def get_notifications_repo() -> INotificationsRepo:
    return NotificationsRepo(db=await get_or_create_database())
