"""
add unit tables

Revision ID: 22e91d7248e
Revises: 790bf4764
Create Date: 2014-08-11 13:55:54.197858
"""

# Revision identifiers, used by Alembic.
revision = '22e91d7248e'
down_revision = '790bf4764'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import lib  # NOQA


def upgrade():
    op.create_table(
        'storm_stock_unit',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sku', sa.String(64), nullable=False, unique=True),
    )

    op.create_table(
        'storm_stock_lot',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('stock_unit_id', sa.Integer(),
                  sa.ForeignKey('storm_stock_unit.id'),
                  nullable=False, index=True),
        sa.Column('serial', sa.String(120), nullable=True),
        sa.Column('quantity', sa.Numeric(18, 6), nullable=False),
        sa.UniqueConstraint('stock_unit_id', 'serial'),
    )


def downgrade():
    op.drop_table('storm_stock_lot')
    op.drop_table('storm_stock_unit')
