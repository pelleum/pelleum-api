# NOTE: This object mirrors the database object handled elsewhere
import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

INSTITUTIONS = sa.Table(
    "institutions",
    METADATA,
    sa.Column("institution_id", sa.String, primary_key=True),
    sa.Column("name", sa.String, nullable=False),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
    schema="account_connections",
)
