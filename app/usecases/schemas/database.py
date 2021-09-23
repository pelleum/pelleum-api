from typing import Optional
from datetime import datetime
from app.usecases.schemas.users import UserBase


class UserInDB(UserBase):
    """Database Model"""

    user_id: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
