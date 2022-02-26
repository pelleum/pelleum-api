import os
from typing import List

import pytest_asyncio
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient
from passlib.context import CryptContext

from app.dependencies import get_current_active_user
from app.infrastructure.db.repos.portfolio_repo import PortfolioRepo
from app.infrastructure.db.repos.post_reaction_repo import PostReactionRepo
from app.infrastructure.db.repos.posts_repo import PostsRepo
from app.infrastructure.db.repos.rationales_repo import RationalesRepo
from app.infrastructure.db.repos.theses_repo import ThesesRepo
from app.infrastructure.db.repos.thesis_reaction_repo import ThesisReactionRepo
from app.infrastructure.db.repos.user_repo import UsersRepo
from app.infrastructure.web.setup import setup_app
from app.usecases.interfaces.portfolio_repo import IPortfolioRepo
from app.usecases.interfaces.post_reaction_repo import IPostReactionRepo
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.interfaces.rationales_repo import IRationalesRepo
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.interfaces.thesis_reaction_repo import IThesisReactionRepo
from app.usecases.interfaces.user_repo import IUsersRepo
from app.usecases.schemas import posts, theses, users


# Database Connection
@pytest_asyncio.fixture
async def test_db_url():
    return "postgres://{username}:{password}@{host}:{port}/{database_name}".format(
        username=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5444"),
        database_name=os.getenv("POSTGRES_DB", "pelleum-dev-test"),
    )


@pytest_asyncio.fixture
async def test_db(test_db_url) -> Database:
    test_db = Database(url=test_db_url, min_size=5)

    await test_db.connect()
    yield test_db
    await test_db.execute("TRUNCATE assets CASCADE")
    await test_db.execute("TRUNCATE post_reactions CASCADE")
    await test_db.execute("TRUNCATE posts CASCADE")
    await test_db.execute("TRUNCATE rationales CASCADE")
    await test_db.execute("TRUNCATE theses CASCADE")
    await test_db.execute("TRUNCATE theses_reactions CASCADE")
    await test_db.execute("TRUNCATE users CASCADE")
    await test_db.execute("TRUNCATE account_connections.institutions CASCADE")
    await test_db.disconnect()


# Repos (Database Gateways)
@pytest_asyncio.fixture
async def posts_repo(test_db: Database) -> IPostsRepo:
    return PostsRepo(db=test_db)


@pytest_asyncio.fixture
async def theses_repo(test_db: Database) -> IThesesRepo:
    return ThesesRepo(db=test_db)


@pytest_asyncio.fixture
async def post_reaction_repo(test_db: Database) -> IPostReactionRepo:
    return PostReactionRepo(db=test_db)


@pytest_asyncio.fixture
async def thesis_reaction_repo(test_db: Database) -> IThesisReactionRepo:
    return ThesisReactionRepo(db=test_db)


@pytest_asyncio.fixture
async def rationales_repo(test_db: Database) -> IRationalesRepo:
    return RationalesRepo(db=test_db)


@pytest_asyncio.fixture
async def portfolio_repo(test_db: Database) -> IPortfolioRepo:
    return PortfolioRepo(db=test_db)


@pytest_asyncio.fixture
async def user_repo(test_db: Database) -> IUsersRepo:
    return UsersRepo(db=test_db)


# Database-inserted Objects
@pytest_asyncio.fixture
async def inserted_user_object(
    user_repo: IUsersRepo,
) -> users.UserInDB:
    """Inserts a user object into the database for other tests."""
    return await user_repo.create(
        new_user=users.UserCreate(
            email="inserted@test.com",
            username="inserted_name",
            password="inserted_password",
        ),
        password_context=CryptContext(schemes=["bcrypt"], deprecated="auto"),
    )


@pytest_asyncio.fixture
async def inserted_post_object(
    inserted_user_object: users.UserInDB,
    posts_repo: IPostsRepo,
) -> posts.PostInDB:
    """Inserts a post object into the database for other tests."""

    return await posts_repo.create(
        new_post=posts.CreatePostRepoAdapter(
            content="This is an inserted test post!",
            asset_symbol="TSLA",
            sentiment=posts.Sentiment.BULL,
            user_id=inserted_user_object.user_id,
            username=inserted_user_object.username,
        )
    )


thesis_title = "Test Thesis Title"


@pytest_asyncio.fixture
async def inserted_thesis_object(
    inserted_user_object: users.UserInDB,
    theses_repo: IThesesRepo,
) -> theses.ThesisInDB:
    """Inserts a thesis object into the database for other tests."""
    global thesis_title

    thesis_title += "1"

    return await theses_repo.create(
        thesis=theses.CreateThesisRepoAdapter(
            title=thesis_title,
            content="This is a test thesis on a test asset.",
            asset_symbol="BTC",
            sentiment=theses.Sentiment.BULL,
            sources=["https://www.pelleum.com", "https://www.youtube.com"],
            user_id=inserted_user_object.user_id,
            username=inserted_user_object.username,
        )
    )


@pytest_asyncio.fixture
async def many_inserted_theses(
    theses_repo: IThesesRepo, create_thesis_object: theses.CreateThesisRepoAdapter
) -> List[theses.ThesisInDB]:

    created_theses = []
    for i, _ in enumerate(range(3)):
        create_thesis_object.title += str(i)

        created_theses.append(await theses_repo.create(thesis=create_thesis_object))

    return created_theses


# Place repo fixtures here
@pytest_asyncio.fixture
def test_active_user() -> users.UserInDB:
    return users.UserInDB(
        user_id=1,
        hashed_password="some-password",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )


@pytest_asyncio.fixture
def test_app(
    test_active_user: users.UserInDB,
) -> FastAPI:
    app = setup_app()
    app.dependency_overrides[get_current_active_user] = lambda: test_active_user
    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")
