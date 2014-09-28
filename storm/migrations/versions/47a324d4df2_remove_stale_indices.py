"""
remove stale indices

Revision ID: 47a324d4df2
Revises: 3707bf4a448
Create Date: 2014-09-26 07:06:10.958447
"""

# Revision identifiers, used by Alembic.
revision = '47a324d4df2'
down_revision = '3707bf4a448'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import NULL, lib  # NOQA


def upgrade():
    op.drop_index('ix_storm_stock_move_batch_id', 'storm_stock_move')
    op.drop_index('ix_storm_stock_move_lot_id', 'storm_stock_move')
    op.drop_index('ix_storm_stock_move_source_location_id', 'storm_stock_move')
    op.drop_index('ix_storm_stock_move_stock_unit_id', 'storm_stock_move')
    op.drop_index('ix_storm_stock_move_target_location_id', 'storm_stock_move')
    op.drop_index('ix_storm_stock_quant_location_id', 'storm_stock_quant')
    op.drop_index('ix_storm_stock_quant_lot_id', 'storm_stock_quant')


def downgrade():
    op.create_index('ix_storm_stock_quant_lot_id', 'storm_stock_quant',
                    ['lot_id'], unique=False)
    op.create_index('ix_storm_stock_quant_location_id', 'storm_stock_quant',
                    ['location_id'], unique=False)
    op.create_index('ix_storm_stock_move_target_location_id',
                    'storm_stock_move',
                    ['target_location_id'], unique=False)
    op.create_index('ix_storm_stock_move_stock_unit_id', 'storm_stock_move',
                    ['stock_unit_id'], unique=False)
    op.create_index('ix_storm_stock_move_source_location_id',
                    'storm_stock_move',
                    ['source_location_id'], unique=False)
    op.create_index('ix_storm_stock_move_lot_id', 'storm_stock_move',
                    ['lot_id'], unique=False)
    op.create_index('ix_storm_stock_move_batch_id', 'storm_stock_move',
                    ['batch_id'], unique=False)
