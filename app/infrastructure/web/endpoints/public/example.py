from datetime import datetime
from fastapi import APIRouter
from app.usecases.schemas import example
from datetime import datetime

example_public_router = APIRouter(tags=["example_public"])


@example_public_router.get(
    "/hello", response_model=example.HelloMessage, summary="Respond with hello world."
)
async def say_hello() -> example.HelloMessage:

    return example.HelloMessage(time=datetime.utcnow(), message="Hello World!")
