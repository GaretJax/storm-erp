"""
add product attributes and images

Revision ID: 214f7a1c7cb
Revises: 41a6bc07c4e
Create Date: 2014-09-26 06:54:51.029974
"""

# Revision identifiers, used by Alembic.
revision = '214f7a1c7cb'
down_revision = '41a6bc07c4e'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import NULL, lib  # NOQA


def upgrade():
    op.create_table(
        'storm_product_attributetype',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=120), nullable=False),
        sa.Column('name', sa.Unicode(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key'),
        sa.UniqueConstraint('key')
    )
    op.create_table(
        'storm_product_image',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'storm_product_attributes',
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('attribute_type_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Unicode(length=255), nullable=True),
        sa.ForeignKeyConstraint(['attribute_type_id'],
                                ['storm_product_attributetype.id']),
        sa.ForeignKeyConstraint(['product_id'], ['storm_product_product.id']),
        sa.PrimaryKeyConstraint('product_id', 'attribute_type_id')
    )


def downgrade():
    op.drop_table('storm_product_attributes')
    op.drop_table('storm_product_image')
    op.drop_table('storm_product_attributetype')
