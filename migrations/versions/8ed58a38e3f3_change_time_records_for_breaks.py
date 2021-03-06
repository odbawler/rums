"""change time_records for breaks

Revision ID: 8ed58a38e3f3
Revises: c6b4f30089fd
Create Date: 2018-03-31 21:36:53.669517

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8ed58a38e3f3'
down_revision = 'c6b4f30089fd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('time_record', sa.Column('end_break', sa.Time(), nullable=True))
    op.add_column('time_record', sa.Column('start_break', sa.Time(), nullable=True))
    op.add_column('time_record', sa.Column('total_break', sa.Time(), nullable=True))
    op.drop_column('time_record', 'break_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('time_record', sa.Column('break_time', postgresql.TIME(), autoincrement=False, nullable=True))
    op.drop_column('time_record', 'total_break')
    op.drop_column('time_record', 'start_break')
    op.drop_column('time_record', 'end_break')
    # ### end Alembic commands ###
