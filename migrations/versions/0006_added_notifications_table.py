"""Added notifications table

Revision ID: 0006
Revises: 0005
Create Date: 2022-04-12 14:35:57.850241

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "events",
        sa.Column("event_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("affected_post_id", sa.Integer(), nullable=True),
        sa.Column("affected_thesis_id", sa.Integer(), nullable=True),
        sa.Column("comment_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["affected_post_id"],
            ["posts.post_id"],
        ),
        sa.ForeignKeyConstraint(
            ["affected_thesis_id"],
            ["theses.thesis_id"],
        ),
        sa.ForeignKeyConstraint(
            ["comment_id"],
            ["posts.post_id"],
        ),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_table(
        "notifications",
        sa.Column("notification_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_to_notify", sa.Integer(), nullable=False),
        sa.Column("user_who_fired_event", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("acknowledged", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["event_id"], ["events.event_id"], ondelete="cascade"),
        sa.ForeignKeyConstraint(
            ["user_to_notify"],
            ["users.user_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_who_fired_event"],
            ["users.user_id"],
        ),
        sa.PrimaryKeyConstraint("notification_id"),
    )
    op.create_index(
        op.f("ix_notifications_user_to_notify"),
        "notifications",
        ["user_to_notify"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_user_who_fired_event"),
        "notifications",
        ["user_who_fired_event"],
        unique=False,
    )
    op.create_check_constraint(
        "either_like_or_comment",
        table_name="events",
        condition="NOT(type = 'POST_REACTION' AND comment_id IS NOT NULL) AND NOT(type = 'COMMENT' AND comment_id IS NULL) AND NOT(type = 'THESIS_REACTION' AND comment_id IS NOT NULL)",
    )
    op.create_check_constraint(
        "either_thesis_or_post",
        table_name="events",
        condition="NOT(affected_post_id IS NULL AND affected_thesis_id IS NULL) AND NOT(affected_post_id IS NOT NULL AND affected_thesis_id IS NOT NULL)",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_notifications_user_who_fired_event"), table_name="notifications"
    )
    op.drop_index(op.f("ix_notifications_user_to_notify"), table_name="notifications")
    op.drop_constraint("either_like_or_comment")
    op.drop_constraint("either_thesis_or_post")
    op.drop_table("notifications")
    op.drop_table("events")
    # ### end Alembic commands ###