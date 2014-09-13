import operator
from sqlalchemy.orm import class_mapper
from sqlalchemy_mptt.mixins import BaseNestedSets


class MPTTBase(BaseNestedSets):
    """
    A specialization of BaseNestedSets which automatically registers
    subclasses as MPTT trees.
    """
    @classmethod
    def __declare_last__(cls):
        cls.register_tree()


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
