from app.usecases.services.user_manager import UserManager
from passlib.context import CryptContext
from app.infrastructure.db.repos.user_repo import UsersRepo
from app.dependencies import get_users_repo




async def get_user_manager_service():
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    users_repo: UsersRepo = await get_users_repo()
    return UserManager(users_repo=users_repo, password_context=password_context)
