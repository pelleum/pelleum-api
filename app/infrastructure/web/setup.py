from fastapi import FastAPI
import uvicorn
import click

from app.infrastructure.web.endpoints.public import (
    auth,
    theses,
    thesis_reactions,
    thesis_comments,
    posts,
    post_reactions,
    post_comments,
    portfolio,
)
from app.infrastructure.web.endpoints.private import example as example_private
from app.infrastructure.web.endpoints import health
from app.infrastructure.db.core import get_or_create_database
from app.dependencies import get_event_loop, get_client_session


from app.settings import settings


def setup_app():
    app = FastAPI(
        title="Pelleum Backend API",
        description="The following are endpoints for the Pelleum mobile appliaction to utilize.",
    )
    app.include_router(auth.auth_router, prefix="/public/auth/users")

    app.include_router(theses.theses_router, prefix="/public/theses")
    app.include_router(
        thesis_reactions.thesis_reactions_router, prefix="/public/theses/reactions"
    )
    app.include_router(
        thesis_comments.thesis_comments_router, prefix="/public/theses/comments"
    )

    app.include_router(posts.posts_router, prefix="/public/posts")
    app.include_router(
        post_reactions.post_reactions_router, prefix="/public/posts/reactions"
    )
    app.include_router(
        post_comments.post_comments_router, prefix="/public/posts/comments"
    )
    app.include_router(portfolio.portfolio_router, prefix="/public/portfolio")
    app.include_router(example_private.example_private_router, prefix="/private")
    app.include_router(health.health_router, prefix="/health")

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
