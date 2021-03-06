"""empty message

Revision ID: 03f8ee953dc4
Revises: d063acb2dbf7
Create Date: 2018-05-13 02:14:35.342543

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03f8ee953dc4'
down_revision = 'd063acb2dbf7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('employee_time', sa.Column('created', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('employee_time', 'created')
    # ### end Alembic commands ###
