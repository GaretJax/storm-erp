import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base, declared_attr


Model = declarative_base()


class Entity(Model):
    """
    Base class to represent entities.
    """
    __tablename__ = 'storm_entity_entity'

    id = sa.Column(sa.Integer, primary_key=True)
    entity_type = sa.Column(sa.String(50), nullable=False)

    reference = sa.Column(sa.String(64), unique=True, nullable=True)

    is_customer = sa.Column(sa.Boolean, server_default='0', nullable=False)
    is_supplier = sa.Column(sa.Boolean, server_default='0', nullable=False)
    is_active = sa.Column(sa.Boolean, server_default='0', nullable=False)

    note = sa.Column(sa.Text, nullable=True)

    # TODO: Add a picture field

    __mapper_args__ = {
        'polymorphic_identity': None,
        'polymorphic_on': entity_type,
    }


class Organization(Entity):
    __tablename__ = 'storm_entity_organization'
    __mapper_args__ = {
        'polymorphic_identity': 'organization',
    }

    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Entity.id, onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True
    )

    name = sa.Column(sa.Unicode(255), nullable=False)
    type = sa.Column(sa.Unicode(32))


class Person(Entity):
    __tablename__ = 'storm_entity_person'
    __mapper_args__ = {
        'polymorphic_identity': 'person',
    }

    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Entity.id, onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True
    )

    title = sa.Column(sa.Unicode(32), nullable=True)
    first_name = sa.Column(sa.Unicode(255))
    last_name = sa.Column(sa.Unicode(255))
    organization_id = sa.Column(sa.Integer, sa.ForeignKey(Organization.id),
                                nullable=True)
    position = sa.Column(sa.Unicode(128), nullable=True)


class EntityAttributeBase(Model):
    __abstract__ = True

    id = sa.Column(sa.Integer, primary_key=True)
    label = sa.Column(sa.Unicode(255), nullable=False)

    @declared_attr
    def entity_id(cls):
        return sa.Column(sa.Integer, sa.ForeignKey(Entity.id))


def make_entity_attribute(label):
    class EntityAttribute(EntityAttributeBase):
        __abstract__ = True

        # Adding the constrain in the base class causes SAWarning to be
        # emitted, so we have to do this here.
        __table_args__ = (
            sa.UniqueConstraint('entity_id', 'label'),
        )

        @declared_attr
        def entity(cls):
            return relationship(Entity, backref=backref(
                label,
                collection_class=attribute_mapped_collection('label'),
            ))

        @declared_attr
        def __tablename__(cls):
            return 'storm_entity_{}'.format(label)

    return EntityAttribute


class PhoneNumber(make_entity_attribute('phone_numbers')):
    number = sa.Column(sa.String(64), nullable=False)


class EmailAddress(make_entity_attribute('email_addresses')):
    email = sa.Column(sa.Unicode(255), nullable=False)


class WebAddress(make_entity_attribute('web_addresses')):
    url = sa.Column(sa.String(255), nullable=False)


class Address(make_entity_attribute('addresses')):
    addressee = sa.Column(sa.Unicode(255), nullable=True)
    street1 = sa.Column(sa.Unicode(255), nullable=False)
    street2 = sa.Column(sa.Unicode(255), nullable=True)
    state = sa.Column(sa.Unicode(128), nullable=True)
    city = sa.Column(sa.Unicode(128), nullable=False)
    zip_code = sa.Column(sa.String(32), nullable=False)
    country = sa.Column(sa.Unicode(64), nullable=False)
