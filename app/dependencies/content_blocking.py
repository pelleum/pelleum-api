from fastapi import Depends

from app.dependencies import (  # pylint: disable = cyclic-import
    get_current_active_user,
    get_users_repo,
)
from app.usecases.interfaces.user_repo import IUsersRepo
from app.usecases.schemas.users import BlockData, UserInDB


async def get_block_data(
    authorized_user: UserInDB = Depends(get_current_active_user),
    users_repo: IUsersRepo = Depends(get_users_repo),
) -> BlockData:

    user_blocks = await users_repo.retrieve_blocks(
        initiating_user_id=authorized_user.user_id
    )
    user_blocked_by = await users_repo.retrieve_blocks(
        receiving_user_id=authorized_user.user_id
    )

    user_ids_blocked_by_user = [
        block_data.blocked_user_id for block_data in user_blocks
    ]
    user_ids_that_blocked_user = [block_data.user_id for block_data in user_blocked_by]

    return BlockData(
        user_blocks=user_ids_blocked_by_user, user_blocked_by=user_ids_that_blocked_user
    )
