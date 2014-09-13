"""
add contacts tables

Revision ID: fb31c6d7e2
Revises: 4d555df8084
Create Date: 2014-09-13 14:03:37.004838
"""

# Revision identifiers, used by Alembic.
revision = 'fb31c6d7e2'
down_revision = '4d555df8084'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from storm.migrations import NULL, lib  # NOQA


def upgrade():
    op.create_table(
        'storm_contact_contact',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.Unicode(length=255), nullable=False),
        sa.Column('reference', sa.String(length=64), nullable=True),
        sa.Column('is_customer', sa.Boolean(), server_default='0',
                  nullable=False),
        sa.Column('is_supplier', sa.Boolean(), server_default='0',
                  nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='0',
                  nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference'),
        sa.UniqueConstraint('reference')
    )
    op.create_table(
        'storm_contact_organization',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Unicode(length=32), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['storm_contact_contact.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'storm_contact_phone_numbers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.Unicode(length=255), nullable=False),
        sa.Column('number', sa.String(length=64), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['storm_contact_contact.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_id', 'label')
    )
    op.create_table(
        'storm_contact_addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.Unicode(length=255), nullable=False),
        sa.Column('addressee', sa.Unicode(length=255), nullable=True),
        sa.Column('street1', sa.Unicode(length=255), nullable=False),
        sa.Column('street2', sa.Unicode(length=255), nullable=True),
        sa.Column('state', sa.Unicode(length=128), nullable=True),
        sa.Column('city', sa.Unicode(length=128), nullable=False),
        sa.Column('zip_code', sa.String(length=32), nullable=False),
        sa.Column('country', sa.Unicode(length=64), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['storm_contact_contact.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_id', 'label')
    )
    op.create_table(
        'storm_contact_email_addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.Unicode(length=255), nullable=False),
        sa.Column('email', sa.Unicode(length=255), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['storm_contact_contact.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_id', 'label')
    )
    op.create_table(
        'storm_contact_web_addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.Unicode(length=255), nullable=False),
        sa.Column('url', sa.String(length=255), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['storm_contact_contact.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_id', 'label')
    )
    op.create_table(
        'storm_contact_person',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Unicode(length=32), nullable=True),
        sa.Column('first_name', sa.Unicode(length=255), nullable=True),
        sa.Column('last_name', sa.Unicode(length=255), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('position', sa.Unicode(length=128), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['storm_contact_contact.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['organization_id'],
            ['storm_contact_organization.id']
        ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('storm_contact_person')
    op.drop_table('storm_contact_web_addresses')
    op.drop_table('storm_contact_email_addresses')
    op.drop_table('storm_contact_addresses')
    op.drop_table('storm_contact_phone_numbers')
    op.drop_table('storm_contact_organization')
    op.drop_table('storm_contact_contact')
