"""empty message

Revision ID: 6ab8c670a5b8
Revises: 3c2ae4e835b2
Create Date: 2018-04-09 21:14:31.087450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ab8c670a5b8'
down_revision = '3c2ae4e835b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('employee_time', sa.Column('hrs_a_day', sa.Time(), nullable=True))
    op.add_column('employee_time', sa.Column('hrs_a_week', sa.Integer(), nullable=True))
    op.drop_column('employee_time', 'weekly_hours')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('employee_time', sa.Column('weekly_hours', sa.NUMERIC(), autoincrement=False, nullable=True))
    op.drop_column('employee_time', 'hrs_a_week')
    op.drop_column('employee_time', 'hrs_a_day')
    # ### end Alembic commands ###
