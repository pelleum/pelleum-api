import os

import pytest
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

from app.infrastructure.web.setup import setup_app


@pytest.fixture
async def test_db_url():
    return (
        "postgresql+aiopg://{username}:{password}@{host}:{port}/{database_name}".format(
            username=os.getenv("POSTGRES_HOST", "localhost"),
            password=os.getenv("POSTGRES_PASSWORD", "5432"),
            host=os.getenv("POSTGRES_HOST", "postgres"),
            port=os.getenv("POSTGRES_PORT", "postgres"),
            database_name=os.getenv("POSTGRES_DB", "pelleum-dev-test"),
        )
    )


@pytest.fixture
async def test_db(test_db_url) -> Database:
    test_db = Database(url=test_db_url)

    await test_db.connect()
    yield test_db
    await test_db.execute("TRUNCATE assets CASCADE")
    await test_db.execute("TRUNCATE post_reactions CASCADE")
    await test_db.execute("TRUNCATE posts CASCADE")
    await test_db.execute("TRUNCATE rationales CASCADE")
    await test_db.execute("TRUNCATE theses CASCADE")
    await test_db.execute("TRUNCATE theses_reactions CASCADE")
    await test_db.execute("TRUNCATE users CASCADE")
    await test_db.disconnect()


# Place repo fixtures here


@pytest.fixture
def test_app(test_db: Database) -> FastAPI:
    app = setup_app()
    # Add in dependency overrides here
    return app


@pytest.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")
