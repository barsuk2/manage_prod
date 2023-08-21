"""add table students

Revision ID: 7fdcf652c90a
Revises: 8edd970f8753
Create Date: 2023-08-17 12:37:47.852071

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fdcf652c90a'
down_revision = '8edd970f8753'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('students',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('patronymic', sa.String(), nullable=True),
    sa.Column('surname', sa.String(), nullable=False),
    sa.Column('grade', sa.Integer(), nullable=True),
    sa.Column('birthday', sa.Date(), nullable=False),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('birth_certificate_series', sa.String(), nullable=True),
    sa.Column('birth_certificate_number', sa.String(), nullable=True),
    sa.Column('birth_certificate_date', sa.String(), nullable=True),
    sa.Column('birth_certificate_organization', sa.String(), nullable=True),
    sa.Column('student_passport_series', sa.String(), nullable=True),
    sa.Column('student_passport_number', sa.String(), nullable=True),
    sa.Column('student_passport_date', sa.Date(), nullable=True),
    sa.Column('student_passport_certifying_organization', sa.String(), nullable=True),
    sa.Column('parent_name', sa.String(), nullable=True),
    sa.Column('parent_patronymic', sa.String(), nullable=True),
    sa.Column('parent_surname', sa.String(), nullable=True),
    sa.Column('parent_birthday', sa.Date(), nullable=True),
    sa.Column('parent_passport_number', sa.String(), nullable=True),
    sa.Column('parent_passport_date', sa.Date(), nullable=True),
    sa.Column('parent_passport_certifying_organization', sa.String(), nullable=True),
    sa.Column('parent_email', sa.String(), nullable=True),
    sa.Column('parent_phone', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('students')
    # ### end Alembic commands ###