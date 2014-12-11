from flask import Blueprint, flash, url_for, abort, redirect

from storm.database import session, mptt
from storm.web.views import ListView, SidebarMixin, EditView

from . import models, forms
from .menu import stock_menu_item, stock_menu


stock_frontend = Blueprint('stock', __name__, template_folder='templates')


@stock_frontend.record_once
def register_menuitem(state):
    state.app.main_menu.add(stock_menu_item)


class WarehouseMixin:
    def warehouse(self):
        return session.query(models.Warehouse).get(self.kwargs['object_id'])


class ListLocations(WarehouseMixin, SidebarMixin, ListView):
    sidebar_menu = stock_menu
    template_name = 'stock/locations.html'

    def get_objects(self):
        locations = (session.query(models.Location)
                     .filter(mptt.descendants(self.warehouse()))
                     .order_by(models.Location.sort_order,
                               models.Location.name))
        locations = mptt.organize(locations)
        return locations

stock_frontend.add_url_rule(
    '/locations/<int:object_id>/',
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
        return url_for('.list_warehouses')

    def save_changes(self, form, object):
        flash('The location was correctly updated.', 'success')
        return super().save_changes(form, object)

    def create_object(self, form, object):
        flash('The location was correctly created.', 'success')
        return super().create_object(form, object)


class EditWarehouse(EditLocation):
    model = models.Warehouse
    form_class = forms.WarehouseForm
    template_name = 'stock/edit_warehouse.html'

stock_frontend.add_url_rule('/locations/<int:object_id>/',
                            methods=['GET', 'POST'],
                            view_func=EditWarehouse.as_view('edit_location'))

stock_frontend.add_url_rule('/locations/add/warehouse/',
                            methods=['GET', 'POST'],
                            view_func=EditWarehouse.as_view('add_warehouse'))


@stock_frontend.route('/locations/move/', methods=['POST'])
def move_location():
    form = forms.LocationMoveForm()
    if form.validate_on_submit():
        form.save()
        return 'OK'
    else:
        abort(400)


class ListWarehouses(SidebarMixin, ListView):
    sidebar_menu = stock_menu
    template_name = 'stock/warehouses.html'

    def get_objects(self):
        locations = (session.query(models.Warehouse)
                     .order_by(models.Warehouse.sort_order,
                               models.Warehouse.name))
        return locations

stock_frontend.add_url_rule(
    '/locations/warehouses/',
    view_func=ListWarehouses.as_view('list_warehouses'),
)


class ListShipments(SidebarMixin, ListView):
    sidebar_menu = stock_menu
    template_name = 'stock/shipments/list.html'

    def get_objects(self):
        return (session.query(models.IncomingShipment))

stock_frontend.add_url_rule(
    '/locations/shipments/',
    view_func=ListShipments.as_view('list_shipments'),
)


class PlanShipment(SidebarMixin, EditView):
    model = models.IncomingShipment
    form_class = forms.ShipmentForm
    template_name = 'stock/shipments/edit.html'
    sidebar_menu = stock_menu

    def get_success_url(self):
        return url_for('.list_shipments')

    def create_object(self, form, object):
        flash('The shipment was correctly created.', 'success')
        form.populate_obj(object)
        session.add(object)
        return redirect(self.get_success_url())

stock_frontend.add_url_rule(
    '/locations/shipments/new/',
    methods=['GET', 'POST'],
    view_func=PlanShipment.as_view('create_shipment'),
)
