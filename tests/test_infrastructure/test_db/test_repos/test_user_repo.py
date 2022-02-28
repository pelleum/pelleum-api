import pytest
import pytest_asyncio
from passlib.context import CryptContext

from app.usecases.interfaces.user_repo import IUsersRepo
from app.usecases.schemas.users import UserCreate, UserInDB, UserUpdate


@pytest_asyncio.fixture
def create_user_object() -> UserCreate:
    return UserCreate(
        email="test@test.com", username="test_username", password="test_password"
    )


@pytest_asyncio.fixture
def update_user_object() -> UserUpdate:
    """Only update username and password for test."""
    return UserUpdate(password="updated_password", username="updated_name")


@pytest_asyncio.fixture
def password_context() -> CryptContext:
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.mark.asyncio
async def test_create(
    user_repo: IUsersRepo,
    create_user_object: UserCreate,
    password_context: CryptContext,
):

    test_user = await user_repo.create(
        new_user=create_user_object, password_context=password_context
    )

    assert isinstance(test_user, UserInDB)
    assert test_user.email == create_user_object.email
    assert test_user.username == create_user_object.username
    assert test_user.hashed_password != create_user_object.password


@pytest.mark.asyncio
async def test_retrieve_user_with_filter(
    user_repo: IUsersRepo, inserted_user_object: UserInDB
):

    test_user = await user_repo.retrieve_user_with_filter(
        user_id=inserted_user_object.user_id
    )

    assert isinstance(test_user, UserInDB)
    assert test_user.email == inserted_user_object.email
    assert test_user.username == inserted_user_object.username
    assert test_user.hashed_password == inserted_user_object.hashed_password


@pytest.mark.asyncio
async def test_update(
    user_repo: IUsersRepo,
    update_user_object: UserUpdate,
    password_context: CryptContext,
    inserted_user_object: UserInDB,
):

    test_updated_user = await user_repo.update(
        updated_user=update_user_object,
        user_id=inserted_user_object.user_id,
        password_context=password_context,
    )

    assert isinstance(test_updated_user, UserInDB)
    assert test_updated_user.email == inserted_user_object.email
    assert test_updated_user.username == update_user_object.username
    assert test_updated_user.hashed_password != inserted_user_object.hashed_password
