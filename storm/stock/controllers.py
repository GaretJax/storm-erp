from flask import Blueprint, flash, url_for, abort

from storm.database import session, mptt
from storm.web.views import ListView, SidebarMixin, EditView

from . import models, forms
from .menu import stock_menu_item, stock_menu


stock_frontend = Blueprint('stock', __name__, template_folder='templates')


@stock_frontend.record_once
def register_menuitem(state):
    state.app.main_menu.add(stock_menu_item)


class ListLocations(SidebarMixin, ListView):
    sidebar_menu = stock_menu
    template_name = 'stock/locations.html'

    def get_objects(self):
        locations = (session.query(models.Location)
                     .order_by(models.Location.sort_order,
                               models.Location.name))
        locations = mptt.organize(locations)
        return locations

stock_frontend.add_url_rule(
    '/locations/',
    view_func=ListLocations.as_view('list_locations')
)


class EditLocation(SidebarMixin, EditView):
    model = models.Location
    form_classes = {
        None: forms.LocationForm,
        'warehouse': forms.WarehouseForm,
    }
    template_name = 'stock/edit_location.html'
    sidebar_menu = stock_menu

    def get_form_class(self):
        try:
            return self.form_classes[self.object.type]
        except KeyError:
            return self.form_classes[None]

    def get_success_url(self):
        return url_for('.list_locations')

    def save_changes(self, form, object):
        flash('The location was correctly updated.', 'success')
        return super().create_object(form, object)

    def create_object(self, form, object):
        flash('The location was correctly created.', 'success')
        return super().create_object(form, object)

stock_frontend.add_url_rule(
    '/locations/<int:object_id>/', methods=['GET', 'POST'],
    view_func=EditLocation.as_view('edit_location')
)

stock_frontend.add_url_rule('/locations/add/warehouse/',
                            methods=['GET', 'POST'],
                            view_func=EditLocation.as_view('add_location'))


@stock_frontend.route('/locations/move/', methods=['POST'])
def move_location():
    form = forms.LocationMoveForm()
    if form.validate_on_submit():
        form.save()
        return 'OK'
    else:
        abort(400)
