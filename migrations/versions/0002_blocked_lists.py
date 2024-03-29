"""blocked lists

Revision ID: 0002
Revises: 0001
Create Date: 2022-03-22 23:50:46.879438

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users", sa.Column("block_list", sa.ARRAY(sa.Integer()), nullable=True)
    )
    op.add_column(
        "users", sa.Column("blocked_by_list", sa.ARRAY(sa.Integer()), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "blocked_by_list")
    op.drop_column("users", "block_list")
    # ### end Alembic commands ###
