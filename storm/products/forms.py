from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
import sqlalchemy as sa
from sqlalchemy.orm import object_session

from storm.web.forms import ModelForm
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
    if cat.parent:
        return ' ' * (cat.level - 2) * 6 + ' | –  ' + cat.name
    else:
        return cat.name


def category_selector(allow_blank=False):
    return QuerySelectField(query_factory=categories_query,
                            blank_text='--- No parent ---',
                            get_label=category_label,
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


class CategoryMoveForm(Form):
    category = category_selector(allow_blank=False)
    parent = category_selector(allow_blank=True)
    previous_sibling = category_selector(allow_blank=True)

    def validate(self):
        if not super().validate():
            return False
        fields = [self.category, self.parent, self.previous_sibling]
        instances = [f.data for f in fields if f.data]
        if len(instances) != len(set(instances)):
            return False
        if self.previous_sibling.data:
            if self.previous_sibling.data.parent != self.parent.data:
                return False
        return True

    def save(self):
        # TODO: This works, but... needs testing!
        c = self.category.data
        p = self.parent.data
        s = self.previous_sibling.data

        session = object_session(c)

        def reorder(table, where, order_by, attr='sort_order'):
            new_orders = sa.alias((
                sa.select([
                    sa.over(sa.func.row_number(),
                            order_by=order_by).label('order'),
                    table.c.id
                ])
                .where(where)
            ))
            session.execute(table.update()
                            .where(table.c.id == new_orders.c.id)
                            .values({
                                attr: new_orders.c.order
                            }))

        # Update sort order on old siblings
        ct = models.Category.__table__
        reorder(ct,
                (ct.c.parent_id == c.parent_id) & (ct.c.id != c.id),
                [ct.c.sort_order, ct.c.name])

        # Update parent
        c.parent = p

        # Update sort order on item
        if s:
            session.expire(s, ['sort_order'])
            c.sort_order = s.sort_order + 1
        else:
            c.sort_order = 0

        # Update sort order on new siblings
        (session.query(models.Category)
         .filter(models.Category.parent == p)
         .filter(models.Category.sort_order >= c.sort_order)
         .filter(models.Category.id != c.id)
         .update({
             'sort_order': models.Category.sort_order + 1,
         }))

        # Rebuild correct ordering
        reorder(ct, (ct.c.parent_id == c.parent_id), ct.c.sort_order)


class ProductForm(ModelForm):
    categories = QuerySelectMultipleField(
        query_factory=categories_query,
        get_label=category_label,
    )

    class Meta:
        model = models.Product
        # only = ['name', 'description']
