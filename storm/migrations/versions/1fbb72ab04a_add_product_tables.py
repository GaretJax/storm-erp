"""
add product tables

Revision ID: 1fbb72ab04a
Revises: 293576aab47
Create Date: 2014-08-22 23:11:44.005504
"""

# Revision identifiers, used by Alembic.
revision = '1fbb72ab04a'
down_revision = '293576aab47'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import lib  # NOQA


def upgrade():
    op.create_table(
        'storm_product_product',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('upc', sa.String(128), unique=True, nullable=False),
        sa.Column('ean13', sa.Integer(), unique=True),
        sa.Column('active', sa.Boolean(), nullable=False, default=False),
        sa.Column('type', sa.String(50), nullable=True),
        sa.Column('name', sa.Unicode(120), nullable=False),
        sa.Column('description', sa.Text()),
    )

    op.create_table(
        'storm_product_category',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.Unicode(120), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('active', sa.Boolean(), nullable=False, default=False),
        sa.Column('tree_id', sa.Integer()),
        sa.Column('parent_id', sa.Integer(),
                  sa.ForeignKey('storm_product_category.id')),
        sa.Column('level', sa.Integer(), nullable=False, index=True,
                  default=0),
        sa.Column('lft', sa.Integer(), nullable=False, index=True),
        sa.Column('rgt', sa.Integer(), nullable=False, index=True),
        sa.UniqueConstraint('parent_id', 'name'),
    )

    op.create_table(
        'storm_product_categories',
        sa.Column(
            'product_id',
            sa.Integer,
            sa.ForeignKey('storm_product_product.id'),
            primary_key=True
        ),
        sa.Column(
            'category_id',
            sa.Integer,
            sa.ForeignKey('storm_product_category.id'),
            primary_key=True
        ),
    )


def downgrade():
    op.drop_table('storm_product_categories')
    op.drop_table('storm_product_category')
    op.drop_table('storm_product_product')
