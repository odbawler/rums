"""empty message

Revision ID: c6b4f30089fd
Revises: ea850c0182b5
Create Date: 2018-03-07 19:46:43.272233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6b4f30089fd'
down_revision = 'ea850c0182b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('employee', sa.Column('is_admin', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('employee', 'is_admin')
    # ### end Alembic commands ###
