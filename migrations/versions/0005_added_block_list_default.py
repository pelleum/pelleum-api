"""Added block list default

Revision ID: 0005
Revises: 0004
Create Date: 2022-03-21 19:57:37.721476

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'block_list',
               existing_type=postgresql.ARRAY(sa.INTEGER()),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'block_list',
               existing_type=postgresql.ARRAY(sa.INTEGER()),
               nullable=False)
    # ### end Alembic commands ###
