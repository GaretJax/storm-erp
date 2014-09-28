"""
add warehouse input/output docks

Revision ID: 15db86e9196
Revises: 47a324d4df2
Create Date: 2014-09-26 18:42:41.366407
"""

# Revision identifiers, used by Alembic.
revision = '15db86e9196'
down_revision = '47a324d4df2'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import NULL, lib  # NOQA


def upgrade():
    op.add_column('storm_stock_warehouse',
                  sa.Column('input_dock_id', sa.Integer(), nullable=True))
    op.add_column('storm_stock_warehouse',
                  sa.Column('output_dock_id', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('storm_stock_warehouse', 'output_dock_id')
    op.drop_column('storm_stock_warehouse', 'input_dock_id')
