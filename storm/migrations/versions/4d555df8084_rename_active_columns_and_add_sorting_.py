"""
rename active columns and add sorting column

Revision ID: 4d555df8084
Revises: 1fbb72ab04a
Create Date: 2014-09-01 12:36:58.187119
"""

# Revision identifiers, used by Alembic.
revision = '4d555df8084'
down_revision = '1fbb72ab04a'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import lib  # NOQA


def upgrade():
    op.alter_column('storm_product_category', 'active',
                    new_column_name='is_active')
    op.alter_column('storm_product_product', 'active',
                    new_column_name='is_active')
    op.alter_column('storm_stock_move', 'scheduled',
                    new_column_name='is_scheduled')
    op.alter_column('storm_stock_move', 'executed',
                    new_column_name='is_executed')
    op.add_column(
        'storm_product_category',
        sa.Column('sort_order', sa.Integer(), nullable=False,
                  server_default='0')
    )
    op.add_column(
        'storm_stock_location',
        sa.Column('sort_order', sa.Integer(), nullable=False,
                  server_default='0')
    )


def downgrade():
    op.drop_column('storm_stock_location', 'sort_order')
    op.drop_column('storm_product_category', 'sort_order')
    op.alter_column('storm_product_category', 'is_active',
                    new_column_name='active')
    op.alter_column('storm_product_product', 'is_active',
                    new_column_name='active')
    op.alter_column('storm_stock_move', 'is_scheduled',
                    new_column_name='scheduled')
    op.alter_column('storm_stock_move', 'is_executed',
                    new_column_name='executed')
