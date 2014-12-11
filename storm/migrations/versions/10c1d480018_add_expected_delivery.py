"""
add expected delivery

Revision ID: 10c1d480018
Revises: 103df7e1ecf
Create Date: 2014-10-13 17:10:10.926716
"""

# Revision identifiers, used by Alembic.
revision = '10c1d480018'
down_revision = '103df7e1ecf'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import NULL, lib  # NOQA


def upgrade():
    op.add_column('storm_stock_incoming_shipment',
                  sa.Column('expected_delivery', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('storm_stock_incoming_shipment', 'expected_delivery')
