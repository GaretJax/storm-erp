"""
add support for warehouses

Revision ID: 790bf4764
Revises: 4eb994a6e98
Create Date: 2014-08-09 08:49:25.227841
"""

# Revision identifiers, used by Alembic.
revision = '790bf4764'
down_revision = '4eb994a6e98'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import lib  # NOQA


def upgrade():
    op.add_column('storm_stock_location',
                  sa.Column('type', sa.String(50), nullable=True))
    op.create_table(
        'storm_stock_warehouse',
        sa.Column(
            'id', sa.Integer(),
            sa.ForeignKey('storm_stock_location.id', onupdate='CASCADE',
                          ondelete='CASCADE'),
            primary_key=True
        )
    )


def downgrade():
    op.drop_table('storm_stock_warehouse')
    op.drop_column('storm_stock_location', 'type')
