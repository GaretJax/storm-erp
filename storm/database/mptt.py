import operator
import sqlalchemy as sa
from sqlalchemy.orm import class_mapper, object_session
from sqlalchemy_mptt.mixins import BaseNestedSets


class MPTTBase(BaseNestedSets):
    """
    A specialization of BaseNestedSets which automatically registers
    subclasses as MPTT trees.
    """
    @classmethod
    def __declare_last__(cls):
        cls.register_tree()


class SortableMPTTBase(MPTTBase):
    sort_order = sa.Column(sa.Integer, nullable=False, server_default='0')

    def _reorder(self, where):
        session = object_session(self)
        new_orders = sa.alias((
            sa.select([
                sa.over(sa.func.row_number(),
                        order_by=self.__table__.c.sort_order).label('order'),
                self.__table__.c.id
            ])
            .where(where)
        ))
        session.execute(self.__table__.update()
                        .where(self.__table__.c.id == new_orders.c.id)
                        .values({
                            'sort_order': new_orders.c.order
                        }))

    def move(self, inside, after):
        session = object_session(self)

        # Update sort order on old siblings
        ct = self.__table__
        self._reorder(
            (ct.c.parent_id == self.parent_id) & (ct.c.id != self.id))

        # Update parent
        self.parent = inside

        # Update sort order on item
        if after:
            session.expire(after, ['sort_order'])
            self.sort_order = after.sort_order + 1
        else:
            self.sort_order = 0

        # Update sort order on new siblings
        (session.query(self.__class__)
         .filter(self.__class__.parent == inside)
         .filter(self.__class__.sort_order >= self.sort_order)
         .filter(self.__class__.id != self.id)
         .update({'sort_order': self.__class__.sort_order + 1}))

        # Rebuild correct ordering
        self._reorder(ct.c.parent_id == self.parent_id)


def _in_tree(node, selectable):
    """
    Utility function to build a filter criterio to select only nodes in the
    same tree as the current node in more advanced filters introduced below.
    """
    return selectable.tree_id == node.tree_id


def descendants(node, include_self=False):
    """
    Builds a filter criterion to select all descendants of the parent node.
    """
    selectable = node.__class__
    if include_self:
        ops = operator.ge, operator.le
    else:
        ops = operator.gt, operator.lt
    return (_in_tree(node, selectable) &
            (ops[0](selectable.left, node.left)) &
            (ops[1](selectable.right, node.right)))


def children(node, selectable=None):
    """
    Builds a filter criterion to select all direct children of the parent node.
    """
    selectable = node.__class__
    return selectable.parent_id == node.id


def ancestors(node, include_self=False):
    """
    Builds a filter criterion to select all ancestors of the parent node.
    """
    selectable = node.__class__
    if include_self:
        ops = operator.le, operator.ge
    else:
        ops = operator.lt, operator.gt
    return (_in_tree(node, selectable) &
            (ops[0](selectable.left, node.left)) &
            (ops[1](selectable.right, node.right)))


def siblings(node, include_self=False):
    """
    Builds a filter criterion to select all siblings of the current node.
    """
    selectable = node.__class__
    query = (_in_tree(node, selectable) &
             (selectable.parent_id == node.parent_id))
    if not include_self:
        pk = class_mapper(node.__class__).primary_key[0]
        query = query & (pk != node.id)
    return query


class NestedSetOrganizer:
    def __init__(self, objects):
        self.objects = objects
        self.grouped = {}
        self.roots = []
        self._organized = False

    def organize(self):
        self.grouped = {}
        self.roots = []
        for o in self.objects:
            if o.parent_id:
                self.grouped.setdefault(o.parent_id, []).append(o)
            else:
                self.roots.append(o)
        self._organized = True

    def _entry(self, obj):
        return obj, self.is_branch(obj), self.children(obj)

    def __iter__(self):
        if not self._organized:
            self.organize()
        for o in self.roots:
            yield self._entry(o)

    def is_leaf(self, obj):
        assert self._organized
        return not self.is_leaf(obj)

    def is_branch(self, obj):
        assert self._organized
        return bool(self.grouped.get(obj.id, False))

    def children(self, obj):
        assert self._organized
        for o in self.grouped.get(obj.id, []):
            yield self._entry(o)


def organize(query):
    return NestedSetOrganizer(query)
