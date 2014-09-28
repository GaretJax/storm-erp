"""
rename indices

Revision ID: 41a6bc07c4e
Revises: fb31c6d7e2
Create Date: 2014-09-26 06:51:31.956687
"""

# Revision identifiers, used by Alembic.
revision = '41a6bc07c4e'
down_revision = 'fb31c6d7e2'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import NULL, lib  # NOQA


def upgrade():
    op.create_index('storm_product_category_level_idx',
                    'storm_product_category', ['level'], unique=False)
    op.create_index('storm_product_category_lft_idx',
                    'storm_product_category', ['lft'], unique=False)
    op.create_index('storm_product_category_rgt_idx',
                    'storm_product_category', ['rgt'], unique=False)

    op.drop_index('ix_storm_product_category_level', 'storm_product_category')
    op.drop_index('ix_storm_product_category_lft', 'storm_product_category')
    op.drop_index('ix_storm_product_category_rgt', 'storm_product_category')

    op.create_index('storm_stock_location_level_idx',
                    'storm_stock_location', ['level'], unique=False)
    op.create_index('storm_stock_location_lft_idx',
                    'storm_stock_location', ['lft'], unique=False)
    op.create_index('storm_stock_location_rgt_idx',
                    'storm_stock_location', ['rgt'], unique=False)

    op.drop_index('ix_storm_stock_location_level', 'storm_stock_location')
    op.drop_index('ix_storm_stock_location_lft', 'storm_stock_location')
    op.drop_index('ix_storm_stock_location_rgt', 'storm_stock_location')


def downgrade():
    op.create_index('ix_storm_stock_location_rgt',
                    'storm_stock_location', ['rgt'], unique=False)
    op.create_index('ix_storm_stock_location_lft',
                    'storm_stock_location', ['lft'], unique=False)
    op.create_index('ix_storm_stock_location_level',
                    'storm_stock_location', ['level'], unique=False)

    op.drop_index('storm_stock_location_rgt_idx', 'storm_stock_location')
    op.drop_index('storm_stock_location_lft_idx', 'storm_stock_location')
    op.drop_index('storm_stock_location_level_idx', 'storm_stock_location')

    op.create_index('ix_storm_product_category_rgt',
                    'storm_product_category', ['rgt'], unique=False)
    op.create_index('ix_storm_product_category_lft',
                    'storm_product_category', ['lft'], unique=False)
    op.create_index('ix_storm_product_category_level',
                    'storm_product_category', ['level'], unique=False)

    op.drop_index('storm_product_category_rgt_idx', 'storm_product_category')
    op.drop_index('storm_product_category_lft_idx', 'storm_product_category')
    op.drop_index('storm_product_category_level_idx', 'storm_product_category')
