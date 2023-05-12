"""Изменил рамерность поля task.comments

Revision ID: ea5258f0e5fd
Revises: b2f4d4b1c9df
Create Date: 2023-05-11 12:09:41.377709

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ea5258f0e5fd'
down_revision = 'b2f4d4b1c9df'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tasks', 'comments',
               existing_type=postgresql.ARRAY(sa.VARCHAR(length=32)),
               type_=postgresql.ARRAY(sa.Text(), zero_indexes=True),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tasks', 'comments',
               existing_type=postgresql.ARRAY(sa.Text(), zero_indexes=True),
               type_=postgresql.ARRAY(sa.VARCHAR(length=32)),
               existing_nullable=True)
    # ### end Alembic commands ###
