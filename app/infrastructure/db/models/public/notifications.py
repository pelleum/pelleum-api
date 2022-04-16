import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

EVENTS = sa.Table(
    "events",
    METADATA,
    sa.Column("event_id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "type",
        sa.String,
        nullable=False,
    ),
    sa.Column(
        "affected_post_id",
        sa.Integer,
        sa.ForeignKey("posts.post_id", ondelete="cascade"),
        nullable=True,
    ),
    sa.Column(
        "affected_thesis_id",
        sa.Integer,
        sa.ForeignKey("theses.thesis_id", ondelete="cascade"),
        nullable=True,
    ),
    sa.Column(
        "comment_id",
        sa.Integer,
        sa.ForeignKey("posts.post_id", ondelete="cascade"),
        nullable=True,
    ),
)

NOTIFICATIONS = sa.Table(
    "notifications",
    METADATA,
    sa.Column("notification_id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "user_to_notify",
        sa.Integer,
        sa.ForeignKey("users.user_id"),
        index=True,
        nullable=False,
    ),
    sa.Column(
        "user_who_fired_event",
        sa.Integer,
        sa.ForeignKey("users.user_id"),
        index=True,
        nullable=False,
    ),
    sa.Column(
        "event_id",
        sa.Integer,
        sa.ForeignKey("events.event_id", ondelete="cascade"),
        nullable=False,
    ),
    sa.Column("acknowledged", sa.Boolean, nullable=False, default=False),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)


# These don't get picked up by alembic's autogenerate, so need to add them in manually
sa.CheckConstraint(
    "NOT(events.type = 'REACTION' AND events.comment_id IS NOT NULL) AND NOT(events.type = 'COMMENT' AND events.comment_id IS NULL)",
    name="either_like_or_comment",
)

sa.CheckConstraint(
    "NOT(events.affected_post_id IS NULL AND events.affected_thesis_id IS NULL) AND NOT(events.affected_post_id IS NOT NULL AND events.affected_thesis_id IS NOT NULL)",
    name="either_thesis_or_post",
)
