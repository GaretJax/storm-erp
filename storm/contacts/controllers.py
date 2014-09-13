from flask import Blueprint

from storm.database import session
from storm.web.views import ListView, SidebarMixin

from . import models
from .menu import main_menu_item, contacts_menu


contacts_frontend = Blueprint('contacts', __name__,
                              template_folder='templates')


@contacts_frontend.record_once
def register_menuitem(state):
    state.app.main_menu.add(main_menu_item)


class ListContacts(SidebarMixin, ListView):
    sidebar_menu = contacts_menu
    template_name = 'products/products.html'

    def get_objects(self, include_organizations=True, include_people=True):
        query = session.query(models.Contact)

        if not include_organizations:
            query.filter(models.Contact.contact_type != 'organization')

        return query

contacts_frontend.add_url_rule(
    '/', view_func=ListContacts.as_view('list_contacts'))
