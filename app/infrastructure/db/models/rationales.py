import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

RATIONALES = sa.Table(
    "rationales",
    METADATA,
    sa.Column("rationale_id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "thesis_id",
        sa.BigInteger,
        sa.ForeignKey("theses.thesis_id"),
        index=True,
        nullable=False,
    ),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.user_id"),
        index=True,
        nullable=False,
    ),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)

sa.UniqueConstraint(RATIONALES.c.thesis_id, RATIONALES.c.user_id)
