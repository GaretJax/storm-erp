from flask import Blueprint, flash, url_for

from storm.database import session
from storm.web.views import ListView, SidebarMixin, EditView

from . import models, forms
from .menu import main_menu_item, contacts_menu


contacts_frontend = Blueprint('contacts', __name__,
                              template_folder='templates')


@contacts_frontend.record_once
def register_menuitem(state):
    state.app.main_menu.add(main_menu_item)


class ListContacts(SidebarMixin, ListView):
    sidebar_menu = contacts_menu
    template_name = 'contacts/contacts.html'

    def dispatch_request(self, scope=None):
        self.scope = scope
        return super().dispatch_request()

    def get_objects(self):
        query = (session.query(models.Contact)
                 .order_by(models.Contact.name))

        if self.scope:
            query = query.filter(models.Contact.contact_type == self.scope)

        return query

    def get_context_data(self, **kwargs):
        kwargs.update({'scope': self.scope})
        return super().get_context_data(**kwargs)


contacts_frontend.add_url_rule(
    '/', view_func=ListContacts.as_view('list_contacts'))
contacts_frontend.add_url_rule(
    '/organizations/',
    view_func=ListContacts.as_view('list_organizations'),
    defaults={'scope': 'organization'},
)
contacts_frontend.add_url_rule(
    '/people/',
    view_func=ListContacts.as_view('list_people'),
    defaults={'scope': 'people'},
)


class EditOrganization(SidebarMixin, EditView):
    model = models.Organization
    form_class = forms.OrganizationForm
    template_name = 'contacts/edit_organization.html'
    sidebar_menu = contacts_menu

    def get_success_url(self):
        return url_for('.list_contacts')

    def save_changes(self, form, object):
        flash('The organization was correctly updated.', 'success')
        r = super().create_object(form, object)
        if not object.reference:
            object.reference = None
        return r

    def create_object(self, form, object):
        flash('The organization was correctly created.', 'success')
        object.is_active = True
        r = super().create_object(form, object)
        if not object.reference:
            object.reference = None
        return r

contacts_frontend.add_url_rule(
    '/organization/add/', methods=['GET', 'POST'],
    view_func=EditOrganization.as_view('add_organization')
)
contacts_frontend.add_url_rule(
    '/organization/<int:object_id>/', methods=['GET', 'POST'],
    view_func=EditOrganization.as_view('edit_organization')
)


class EditPerson(SidebarMixin, EditView):
    model = models.Person
    form_class = forms.PersonForm
    template_name = 'contacts/edit_person.html'
    sidebar_menu = contacts_menu

    def get_success_url(self):
        return url_for('.list_contacts')

    def save_changes(self, form, object):
        flash('The person contact details were correctly updated.', 'success')
        r = super().create_object(form, object)
        if not object.reference:
            object.reference = None
        return r

    def create_object(self, form, object):
        flash('The person contact details were correctly created.', 'success')
        object.is_active = True
        r = super().create_object(form, object)
        if not object.reference:
            object.reference = None
        return r

contacts_frontend.add_url_rule(
    '/people/add/', methods=['GET', 'POST'],
    view_func=EditPerson.as_view('add_person')
)
contacts_frontend.add_url_rule(
    '/people/<int:object_id>/', methods=['GET', 'POST'],
    view_func=EditPerson.as_view('edit_person')
)
