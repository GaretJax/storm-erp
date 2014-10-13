from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField

from storm.web.forms import ModelForm, MPTTMoveForm
from storm.database import session, mptt, NULL

from . import models


def categories_query():
    return (session.query(models.Category)
            .order_by(models.Category.tree_id,
                      models.Category.parent_id != NULL,
                      models.Category.parent_id,
                      models.Category.sort_order,
                      models.Category.name))


def filtered_by_self(category):
    def factory():
        return categories_query().filter(
            (models.Category.tree_id != category.tree_id) |
            (~mptt.descendants(category, include_self=True))
        )
    return factory


def category_label(cat):
    return cat.path()


def category_selector(allow_blank=False):
    return QuerySelectField(query_factory=categories_query,
                            blank_text='--- No parent ---',
                            get_label=category_label,
                            allow_blank=allow_blank)


def products_query():
    return (session.query(models.Product)
            .order_by(models.Product.name))


def product_label(prod):
    return prod.name


def product_selector(allow_blank=False):
    return QuerySelectField(query_factory=products_query,
                            blank_text='--- No parent ---',
                            get_label=product_label,
                            allow_blank=allow_blank)


class CategoryForm(ModelForm):
    parent = category_selector(allow_blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._obj:
            self.parent.query_factory = filtered_by_self(self._obj)

    class Meta:
        model = models.Category
        only = ['name', 'description']


CategoryMoveForm = MPTTMoveForm.for_query_factory(
    categories_query, label=category_label)


class ProductForm(ModelForm):
    categories = QuerySelectMultipleField(
        query_factory=categories_query,
        get_label=category_label,
    )

    class Meta:
        model = models.Product
