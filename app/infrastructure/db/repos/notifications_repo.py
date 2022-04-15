from typing import List, Optional, Tuple

from databases import Database
from sqlalchemy import and_, desc, select

from app.infrastructure.db.models.public.notifications import EVENTS, NOTIFICATIONS
from app.infrastructure.db.models.public.users import USERS
from app.usecases.interfaces.notifications_repo import INotificationsRepo
from app.usecases.schemas import notifications


class NotificationsRepo(INotificationsRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, new_event: notifications.NewEventRepoAdapter) -> None:
        """Create reaction"""

        event_insert_statement = EVENTS.insert().values(
            type=new_event.type,
            affected_post_id=new_event.affected_post_id,
            affected_thesis_id=new_event.affected_thesis_id,
            comment_id=new_event.comment_id,
        )

        async with self.db.transaction():

            event_id = await self.db.execute(event_insert_statement)

            notification_insert_statement = NOTIFICATIONS.insert().values(
                user_to_notify=new_event.user_to_notify,
                user_who_fired_event=new_event.user_who_fired_event,
                event_id=event_id,
                acknowledged=False,
            )

            await self.db.execute(notification_insert_statement)

    async def update(self, notification_id: int) -> None:
        """Update notification acknowledgement."""

        update_statement = (
            NOTIFICATIONS.update()
            .values(acknowledged=True)
            .where(NOTIFICATIONS.c.notification_id == notification_id)
        )

        await self.db.execute(update_statement)

    async def retrieve_many(
        self,
        user_id: int,
        page_number: int = 1,
        page_size: int = 200,
    ) -> List[notifications.NotificationDbInfo]:
        """Retrieve many reactions"""

        j = NOTIFICATIONS.join(
            EVENTS, NOTIFICATIONS.c.event_id == EVENTS.c.event_id
        ).join(USERS, NOTIFICATIONS.c.user_who_fired_event == USERS.c.user_id)

        columns_to_select = [
            NOTIFICATIONS.c.notification_id,
            EVENTS,
            USERS.c.username,
            USERS.c.user_id,
        ]

        query = (
            select(columns_to_select)
            .select_from(j)
            .where(
                and_(
                    NOTIFICATIONS.c.acknowledged == False,
                    NOTIFICATIONS.c.user_to_notify == user_id,
                )
            )
            .limit(page_size)
            .offset((page_number - 1) * page_size)
            .order_by(desc(NOTIFICATIONS.c.created_at))
        )

        query_results = await self.db.fetch_all(query)

        return [notifications.NotificationDbInfo(**result) for result in query_results]

    async def retrieve_single(
        self,
        notification_id: int,
    ) -> Optional[notifications.NotificationInDb]:
        """Retrieves a single notification."""

        query = NOTIFICATIONS.select().where(
            NOTIFICATIONS.c.notification_id == notification_id
        )

        result = await self.db.fetch_one(query)
        return notifications.NotificationInDb(**result) if result else None
