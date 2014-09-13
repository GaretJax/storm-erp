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
