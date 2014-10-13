"""
add shipment columns

Revision ID: 103df7e1ecf
Revises: 15db86e9196
Create Date: 2014-10-07 11:07:40.423079
"""

# Revision identifiers, used by Alembic.
revision = '103df7e1ecf'
down_revision = '15db86e9196'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import NULL, lib  # NOQA


def upgrade():
    op.add_column(
        'storm_stock_incoming_shipment',
        sa.Column('destination_warehouse_id', sa.Integer(), nullable=True)
    )
    op.add_column(
        'storm_stock_incoming_shipment',
        sa.Column('supplier_id', sa.Integer(), nullable=False)
    )
    op.add_column(
        'storm_stock_incoming_shipment',
        sa.Column('tracking_number', sa.String(length=255), nullable=True)
    )


def downgrade():
    op.drop_column('storm_stock_incoming_shipment', 'tracking_number')
    op.drop_column('storm_stock_incoming_shipment', 'supplier_id')
    op.drop_column('storm_stock_incoming_shipment', 'destination_warehouse_id')
