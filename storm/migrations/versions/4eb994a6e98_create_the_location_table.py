"""
create the location table

Revision ID: 4eb994a6e98
Revises: None
Create Date: 2014-08-08 16:24:55.010467
"""

# Revision identifiers, used by Alembic.
revision = '4eb994a6e98'
down_revision = None


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import lib  # NOQA


def upgrade():
    op.create_table(
        'storm_stock_location',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('tree_id', sa.Integer()),
        sa.Column('parent_id', sa.Integer(),
                  sa.ForeignKey('storm_stock_location.id')),
        sa.Column('level', sa.Integer(), nullable=False, index=True,
                  default=0),
        sa.Column('lft', sa.Integer(), nullable=False, index=True),
        sa.Column('rgt', sa.Integer(), nullable=False, index=True),
    )


def downgrade():
    op.drop_table('storm_stock_location')
