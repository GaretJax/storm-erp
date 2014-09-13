"""
add moves tables

Revision ID: 293576aab47
Revises: 22e91d7248e
Create Date: 2014-08-11 14:07:35.771266
"""

# Revision identifiers, used by Alembic.
revision = '293576aab47'
down_revision = '22e91d7248e'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import NULL, lib  # NOQA


def upgrade():
    op.create_table(
        'storm_stock_batch',
        sa.Column('id', sa.Integer(), primary_key=True),
    )

    op.create_table(
        'storm_stock_move',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('batch_id', sa.Integer(),
                  sa.ForeignKey('storm_stock_batch.id',
                                onupdate='CASCADE', ondelete='CASCADE'),
                  index=True, nullable=False),
        sa.Column('source_location_id', sa.Integer(),
                  sa.ForeignKey('storm_stock_location.id'),
                  nullable=False, index=True),
        sa.Column('target_location_id', sa.Integer(),
                  sa.ForeignKey('storm_stock_location.id'),
                  nullable=False, index=True),
        sa.Column('stock_unit_id', sa.Integer(),
                  sa.ForeignKey('storm_stock_unit.id'),
                  nullable=False, index=True),
        sa.Column('lot_id', sa.Integer(), sa.ForeignKey('storm_stock_lot.id'),
                  nullable=True, index=True),
        sa.Column('quantity', sa.Numeric(18, 6), nullable=False),
        sa.Column('scheduled', sa.Boolean(), default=False),
        sa.Column('executed', sa.Boolean(), default=False),
        sa.Index('batch_id_wo_lot',
                 'source_location_id', 'target_location_id',
                 'stock_unit_id', 'lot_id',
                 postgresql_where=sa.text('lot_id IS NOT NULL'),
                 unique=True),
        sa.Index('batch_id_w_lot',
                 'source_location_id', 'target_location_id',
                 'stock_unit_id',
                 postgresql_where=sa.text('lot_id IS NULL'),
                 unique=True),
    )

    op.create_table(
        'storm_stock_quant',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('location_id', sa.Integer(),
                  sa.ForeignKey('storm_stock_location.id'),
                  index=True, nullable=False),
        sa.Column('lot_id', sa.Integer(), sa.ForeignKey('storm_stock_lot.id'),
                  nullable=True, index=True),
        sa.Column('quantity', sa.Numeric(18, 6), nullable=False),
        sa.UniqueConstraint('location_id', 'lot_id'),
    )


def downgrade():
    op.drop_table('storm_stock_quant')
    op.drop_table('storm_stock_move')
    op.drop_table('storm_stock_batch')
