"""Add col abstract

Revision ID: 5250bcdd9fc7
Revises: e91309a56154
Create Date: 2023-06-09 11:35:18.793489

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5250bcdd9fc7'
down_revision = 'e91309a56154'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cards', sa.Column('abstract', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cards', 'abstract')
    # ### end Alembic commands ###