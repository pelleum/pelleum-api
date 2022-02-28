import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

POSTS = sa.Table(
    "posts",
    METADATA,
    sa.Column("post_id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.user_id"),
        index=True,
    ),
    sa.Column("username", sa.String, nullable=False, index=True),
    sa.Column(
        "thesis_id",
        sa.BigInteger,
        sa.ForeignKey("theses.thesis_id"),
        index=True,
        nullable=True,
    ),
    sa.Column("title", sa.String, nullable=True),
    sa.Column("content", sa.Text, nullable=False),
    sa.Column("asset_symbol", sa.String, nullable=True, index=True),
    sa.Column("sentiment", sa.String, nullable=True),
    sa.Column("is_post_comment_on", sa.BigInteger, nullable=True, index=True),
    sa.Column("is_thesis_comment_on", sa.BigInteger, nullable=True, index=True),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)

POST_REACTIONS = sa.Table(
    "post_reactions",
    METADATA,
    sa.Column(
        "post_id",
        sa.BigInteger,
        sa.ForeignKey("posts.post_id", ondelete="cascade"),
        primary_key=True,
        index=True,
    ),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.user_id"),
        primary_key=True,
        index=True,
    ),
    sa.Column("reaction", sa.SmallInteger, nullable=False),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)
