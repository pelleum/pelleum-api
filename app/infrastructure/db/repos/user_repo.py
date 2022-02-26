from typing import Optional

from databases import Database
from passlib.context import CryptContext
from sqlalchemy import and_

from app.infrastructure.db.models.public.users import USERS
from app.usecases.interfaces.user_repo import IUsersRepo
from app.usecases.schemas import users


class UsersRepo(IUsersRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(
        self, new_user: users.UserCreate, password_context: CryptContext
    ) -> users.UserInDB:

        hashed_password = password_context.hash(new_user.password)

        create_user_insert_stmt = USERS.insert().values(
            email=new_user.email,
            username=new_user.username,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )

        await self.db.execute(create_user_insert_stmt)

        return await self.retrieve_user_with_filter(username=new_user.username)

    async def retrieve_user_with_filter(
        self,
        user_id: str = None,
        email: str = None,
        username: str = None,
    ) -> Optional[users.UserInDB]:

        conditions = []

        if user_id:
            conditions.append(USERS.c.user_id == user_id)

        if email:
            conditions.append(USERS.c.email == email)

        if username:
            conditions.append(USERS.c.username == username)

        if len(conditions) == 0:
            raise Exception(
                "Please pass a parameter to query by to the function, retrieve_user_with_filter()"
            )

        query = USERS.select().where(and_(*conditions))

        result = await self.db.fetch_one(query)
        return users.UserInDB(**result) if result else None

    async def update(
        self,
        updated_user: users.UserUpdate,
        user_id: str,
        password_context: CryptContext,
    ) -> users.UserInDB:

        if updated_user.password:
            hashed_password = password_context.hash(updated_user.password)
            updated_user.password = hashed_password

        query = USERS.update()

        updated_user_raw = updated_user.dict()
        updated_user_raw["hashed_password"] = updated_user.password
        del updated_user_raw["password"]
        update_user_dict = {}

        for key, value in updated_user_raw.items():
            if value is not None:
                update_user_dict[key] = value

        query = query.values(update_user_dict)

        user_update_stmt = query.where(USERS.c.user_id == user_id)

        await self.db.execute(user_update_stmt)

        return await self.retrieve_user_with_filter(user_id=user_id)
