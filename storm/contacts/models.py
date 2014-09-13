import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base, declared_attr


Model = declarative_base()


class Contact(Model):
    """
    Base class to represent contacts.
    """
    __tablename__ = 'storm_contact_contact'

    id = sa.Column(sa.Integer, primary_key=True)
    contact_type = sa.Column(sa.String(50), nullable=False)

    reference = sa.Column(sa.String(64), unique=True, nullable=True)

    is_customer = sa.Column(sa.Boolean, server_default='0', nullable=False)
    is_supplier = sa.Column(sa.Boolean, server_default='0', nullable=False)
    is_active = sa.Column(sa.Boolean, server_default='0', nullable=False)

    note = sa.Column(sa.Text, nullable=True)

    # TODO: Add a picture field

    __mapper_args__ = {
        'polymorphic_idcontact': None,
        'polymorphic_on': contact_type,
    }


class Organization(Contact):
    __tablename__ = 'storm_contact_organization'
    __mapper_args__ = {
        'polymorphic_idcontact': 'organization',
    }

    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Contact.id, onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True
    )

    name = sa.Column(sa.Unicode(255), nullable=False)
    type = sa.Column(sa.Unicode(32))


class Person(Contact):
    __tablename__ = 'storm_contact_person'
    __mapper_args__ = {
        'polymorphic_idcontact': 'person',
    }

    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Contact.id, onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True
    )

    title = sa.Column(sa.Unicode(32), nullable=True)
    first_name = sa.Column(sa.Unicode(255))
    last_name = sa.Column(sa.Unicode(255))
    organization_id = sa.Column(sa.Integer, sa.ForeignKey(Organization.id),
                                nullable=True)
    position = sa.Column(sa.Unicode(128), nullable=True)


class ContactAttributeBase(Model):
    __abstract__ = True

    id = sa.Column(sa.Integer, primary_key=True)
    label = sa.Column(sa.Unicode(255), nullable=False)

    @declared_attr
    def contact_id(cls):
        return sa.Column(sa.Integer, sa.ForeignKey(Contact.id))


def make_contact_attribute(label):
    class ContactAttribute(ContactAttributeBase):
        __abstract__ = True

        # Adding the constrain in the base class causes SAWarning to be
        # emitted, so we have to do this here.
        __table_args__ = (
            sa.UniqueConstraint('contact_id', 'label'),
        )

        @declared_attr
        def contact(cls):
            return relationship(Contact, backref=backref(
                label,
                collection_class=attribute_mapped_collection('label'),
            ))

        @declared_attr
        def __tablename__(cls):
            return 'storm_contact_{}'.format(label)

    return ContactAttribute


class PhoneNumber(make_contact_attribute('phone_numbers')):
    number = sa.Column(sa.String(64), nullable=False)


class EmailAddress(make_contact_attribute('email_addresses')):
    email = sa.Column(sa.Unicode(255), nullable=False)


class WebAddress(make_contact_attribute('web_addresses')):
    url = sa.Column(sa.String(255), nullable=False)


class Address(make_contact_attribute('addresses')):
    addressee = sa.Column(sa.Unicode(255), nullable=True)
    street1 = sa.Column(sa.Unicode(255), nullable=False)
    street2 = sa.Column(sa.Unicode(255), nullable=True)
    state = sa.Column(sa.Unicode(128), nullable=True)
    city = sa.Column(sa.Unicode(128), nullable=False)
    zip_code = sa.Column(sa.String(32), nullable=False)
    country = sa.Column(sa.Unicode(64), nullable=False)
