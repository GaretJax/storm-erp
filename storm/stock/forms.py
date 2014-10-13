from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import form, fields

from storm.web.forms import ModelForm, MPTTMoveForm
from storm.database import session, mptt, NULL

from . import models
from storm.contacts.forms import supplier_selector
from storm.products.forms import product_selector


def locations_query():
    return (session.query(models.Location)
            .order_by(models.Location.tree_id,
                      models.Location.parent_id != NULL,
                      models.Location.parent_id,
                      models.Location.sort_order,
                      models.Location.name))


def filtered_by_self(location):
    def factory():
        return locations_query().filter(
            (models.Location.tree_id != location.tree_id) |
            (~mptt.descendants(location, include_self=True))
        )
    return factory


def warehouse_query():
    return (session.query(models.Warehouse)
            .order_by(models.Location.tree_id,
                      models.Location.parent_id != NULL,
                      models.Location.parent_id,
                      models.Location.sort_order,
                      models.Location.name))


def only_descendants(location):
    def factory():
        return locations_query().filter(mptt.descendants(location))
    return factory


def location_label(loc):
    return loc.path()


def location_selector(allow_blank=False):
    return QuerySelectField(query_factory=locations_query,
                            blank_text='--- No parent ---',
                            get_label=location_label,
                            allow_blank=allow_blank)


def warehouse_selector(allow_blank=False):
    return QuerySelectField(query_factory=warehouse_query,
                            blank_text='--- No warehouse ---',
                            get_label=location_label,
                            allow_blank=allow_blank)


class LocationForm(ModelForm):
    parent = location_selector(allow_blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._obj:
            self.parent.query_factory = filtered_by_self(self._obj)

    class Meta:
        model = models.Location
        only = ['name']


class WarehouseForm(ModelForm):
    input_dock = location_selector(allow_blank=True)
    output_dock = location_selector(allow_blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._obj:
            self.input_dock.query_factory = only_descendants(self._obj)
            self.output_dock.query_factory = only_descendants(self._obj)

    class Meta:
        model = models.Warehouse
        only = ['name']


LocationMoveForm = MPTTMoveForm.for_query_factory(
    locations_query, label=location_label)


class IncomingMoveForm(form.Form):
    product = product_selector()
    quantity = fields.DecimalField()


class ShipmentForm(ModelForm):
    supplier = supplier_selector()
    destination_warehouse = warehouse_selector()

    products = fields.FieldList(fields.FormField(IncomingMoveForm),
                                min_entries=1)

    class Meta:
        model = models.IncomingShipment
