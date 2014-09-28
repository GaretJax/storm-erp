"""
add batch subtypes

Revision ID: 3707bf4a448
Revises: 214f7a1c7cb
Create Date: 2014-09-26 06:58:46.953951
"""

# Revision identifiers, used by Alembic.
revision = '3707bf4a448'
down_revision = '214f7a1c7cb'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import NULL, lib  # NOQA


def upgrade():
    op.create_table(
        'storm_stock_physical_inventory',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['storm_stock_batch.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'storm_stock_incoming_shipment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['storm_stock_batch.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'storm_stock_delivery_order',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['storm_stock_batch.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('storm_stock_batch',
                  sa.Column('type', sa.String(length=50), nullable=True))

    op.drop_index('batch_id_w_lot', table_name='storm_stock_move')
    op.create_index('batch_id_w_lot', 'storm_stock_move',
                    ['source_location_id', 'target_location_id',
                     'stock_unit_id', 'lot_id'],
                    unique=True,
                    postgresql_where=sa.text('lot_id IS NOT NULL'))

    op.drop_index('batch_id_wo_lot', table_name='storm_stock_move')
    op.create_index('batch_id_wo_lot', 'storm_stock_move',
                    ['source_location_id', 'target_location_id',
                     'stock_unit_id'],
                    unique=True, postgresql_where=sa.text('lot_id IS NULL'))


def downgrade():
    op.drop_index('batch_id_wo_lot', table_name='storm_stock_move')
    op.create_index('batch_id_wo_lot', 'storm_stock_move',
                    ['source_location_id', 'target_location_id',
                     'stock_unit_id', 'lot_id'], unique=True)
    op.drop_index('batch_id_w_lot', table_name='storm_stock_move')
    op.create_index('batch_id_w_lot', 'storm_stock_move',
                    ['source_location_id', 'target_location_id',
                     'stock_unit_id'], unique=True)
    op.drop_column('storm_stock_batch', 'type')
    op.drop_table('storm_stock_delivery_order')
    op.drop_table('storm_stock_incoming_shipment')
    op.drop_table('storm_stock_physical_inventory')
