"""rename_table - history

Revision ID: 48d00da5c1b2
Revises: 2e4dfd40bde8
Create Date: 2023-05-05 11:34:57.751555

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48d00da5c1b2'
down_revision = '2e4dfd40bde8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('history', sa.Column('title', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('history', 'title')
    # ### end Alembic commands ###