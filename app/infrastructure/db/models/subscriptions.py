import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

SUBSCRIPTIONS = sa.Table(
    "subscriptions",
    METADATA,
    sa.Column("subscription_id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    ),    
    sa.Column(
        "subscription_tier", 
        sa.String,
        nullable=False,
    ),
    sa.Column("stripe_customer_id", sa.String, nullable=False, unique=True),
    sa.Column("is_active", sa.Boolean, nullable=False, default=True),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)