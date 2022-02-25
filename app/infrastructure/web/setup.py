import click
import uvicorn
from fastapi import FastAPI

from app.dependencies import get_client_session, get_event_loop
from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.web.endpoints import health
from app.infrastructure.web.endpoints.private import example as example_private
from app.infrastructure.web.endpoints.public import (
    account_connections,
    auth,
    portfolio,
    post_reactions,
    posts,
    rationales,
    theses,
    thesis_reactions,
    payments
)
from app.settings import settings


def setup_app():
    app = FastAPI(
        title="Pelleum Backend API",
        description="The following are endpoints for the Pelleum mobile appliaction to utilize.",
        openapi_url=settings.openapi_url,
    )
    app.include_router(auth.auth_router, prefix="/public/auth/users")

    app.include_router(theses.theses_router, prefix="/public/theses")
    app.include_router(
        thesis_reactions.thesis_reactions_router, prefix="/public/theses/reactions"
    )
    app.include_router(rationales.rationale_router, prefix="/public/theses/rationales")
    app.include_router(posts.posts_router, prefix="/public/posts")
    app.include_router(
        post_reactions.post_reactions_router, prefix="/public/posts/reactions"
    )
    app.include_router(portfolio.portfolio_router, prefix="/public/portfolio")
    app.include_router(
        account_connections.institution_router, prefix="/public/institutions"
    )
    app.include_router(example_private.example_private_router, prefix="/private")
    app.include_router(health.health_router, prefix="/health")
    app.include_router(payments.payments_router, prefix="/public/payments")

    return app


fastapi_app = setup_app()


@fastapi_app.on_event("startup")
async def startup_event():
    await get_event_loop()
    await get_client_session()
    await get_or_create_database()


@fastapi_app.on_event("shutdown")
async def shutdown_event():
    # Close client session
    client_session = await get_client_session()
    await client_session.close()

    # Close database connection once db exists
    DATABASE = await get_or_create_database()
    if DATABASE.is_connected:
        await DATABASE.disconnect()


@click.command()
@click.option("--reload", is_flag=True)
def main(reload=False):

    kwargs = {"reload": reload}

    uvicorn.run(
        "app.infrastructure.web.setup:fastapi_app",
        loop="uvloop",
        host=settings.server_host,
        port=settings.server_port,
        **kwargs,
    )
