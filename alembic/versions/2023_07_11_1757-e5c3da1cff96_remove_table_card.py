"""remove table card

Revision ID: e5c3da1cff96
Revises: 3cd75dcaa1a4
Create Date: 2023-07-11 17:57:51.952438

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5c3da1cff96'
down_revision = '3cd75dcaa1a4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('cards')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cards',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('questions', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('response', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('subcategory', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('abstract', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='cards_pkey')
    )
    # ### end Alembic commands ###