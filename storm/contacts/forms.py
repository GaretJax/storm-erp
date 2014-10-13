from wtforms.ext.sqlalchemy.fields import QuerySelectField

from storm.web.forms import ModelForm
from storm.database import session

from . import models


class OrganizationForm(ModelForm):
    class Meta:
        model = models.Organization
        only = [
            'name',
            'reference',
            'is_supplier', 'is_customer',
            'note'
        ]


def organizations_query():
    return session.query(models.Organization)


def organization_label(org):
    return org.name


def suppliers_query():
    return (session.query(models.Contact)
            .filter(models.Contact.is_supplier == True)
            .filter(models.Contact.is_active == True)
            .order_by(models.Contact.name))


def contact_label(contact):
    return contact.name


def supplier_selector(allow_blank=False):
    return QuerySelectField(query_factory=suppliers_query,
                            blank_text='--- No supplier ---',
                            get_label=contact_label,
                            allow_blank=allow_blank)


class PersonForm(ModelForm):
    organization = QuerySelectField(query_factory=organizations_query,
                                    blank_text='--- No organization ---',
                                    get_label=organization_label,
                                    allow_blank=True)

    class Meta:
        model = models.Person
        only = [
            'title',
            'last_name', 'first_name',
            'position',
            'reference',
            'is_supplier', 'is_customer',
            'note'
        ]
