import pytest

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from storm.database import mptt, get_engine


Base = declarative_base()


class Node(mptt.MPTTBase, Base):
    __tablename__ = '__test_node'

    id = sa.Column(sa.Integer, primary_key=True)
    type = sa.Column(sa.Integer, default=0)

    def __init__(self, id=None):
        self.id = id

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 0,
    }

    def __repr__(self):  # NOCOV
        return 'N({})'.format(self.id)


class SpecialNode(Node):
    __tablename__ = '__test_special_node'
    __table_args__ = None

    id = sa.Column(sa.Integer, sa.ForeignKey(Node.id), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 1,
    }

    def __repr__(self):  # NOCOV
        return 'S({})'.format(self.id)


trees_structure = {
    1: {
        2: {},
        3: {},
    },
    4: {},
    5: {
        6: {
            7: {},
            8: {
                10: {},
                11: {
                    12: {},
                },
            },
            9: {}
        },
        13: {},
        14: {},
    },
    15: {
        16: {
            17: {
                18: {
                    19: {},
                }
            },
        },
    },
}


@pytest.yield_fixture(scope='function')
def db_table():
    engine = get_engine()
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.yield_fixture(scope='function')
def q(db_table, session):
    def make_tree(parent, children):
        for k, v in children.items():
            n = Node(k)
            n.parent = parent
            make_tree(n, v)
    for k, v in trees_structure.items():
        root = Node(k)
        root.tree_id = k
        make_tree(root, v)
        session.add(root)
    session.flush()
    session.expire_all()
    yield Query(session)
    session.query(SpecialNode).delete()
    session.query(Node).delete()


class Query:
    def __init__(self, session):
        self.session = session

    def node(self, id, type=Node):
        return self.session.query(type).get(id)

    def ids(self, criteria):
        result = (self.session.query(Node)
                  .filter(criteria)
                  .order_by(Node.id)
                  .all())
        return [v.id for v in result]

    # def make_special(self, *ids):
    #     val = [{'id': i} for i in ids]
    #     self.session.execute(SpecialNode.__table__.insert().values(val))
    #     self.session.execute(Node.__table__.update()
    #                          .where(Node.id.in_(ids))
    #                          .values(type=1))
    #     self.session.flush()
    #     self.session.expire_all()
    #     self.session.expunge_all()

    def children(self, id):
        return self.ids(mptt.children(self.node(id)))

    def descendants(self, id, include_self=False):
        return self.ids(mptt.descendants(
            self.node(id), include_self=include_self
        ))

    def ancestors(self, id, include_self=False):
        return self.ids(mptt.ancestors(
            self.node(id), include_self=include_self
        ))

    def siblings(self, id, include_self=False):
        return self.ids(mptt.siblings(
            self.node(id), include_self=include_self
        ))


def test_children(q):
    assert q.children(1) == [2, 3]
    assert q.children(4) == []
    assert q.children(5) == [6, 13, 14]
    assert q.children(15) == [16]
    assert q.children(8) == [10, 11]
    assert q.children(12) == []


def test_descendants(q):
    assert q.descendants(1) == [2, 3]
    assert q.descendants(4) == []
    assert q.descendants(5) == [6, 7, 8, 9, 10, 11, 12, 13, 14]
    assert q.descendants(15) == [16, 17, 18, 19]
    assert q.descendants(8) == [10, 11, 12]
    assert q.descendants(12) == []

    assert q.descendants(1, True) == [1, 2, 3]
    assert q.descendants(4, True) == [4]
    assert q.descendants(5, True) == [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    assert q.descendants(15, True) == [15, 16, 17, 18, 19]
    assert q.descendants(8, True) == [8, 10, 11, 12]
    assert q.descendants(12, True) == [12]


def test_ancestors(q):
    assert q.ancestors(2) == [1]
    assert q.ancestors(4) == []
    assert q.ancestors(5) == []
    assert q.ancestors(8) == [5, 6]
    assert q.ancestors(12) == [5, 6, 8, 11]
    assert q.ancestors(17) == [15, 16]
    assert q.ancestors(19) == [15, 16, 17, 18]

    assert q.ancestors(2, True) == [1, 2]
    assert q.ancestors(4, True) == [4]
    assert q.ancestors(5, True) == [5]
    assert q.ancestors(8, True) == [5, 6, 8]
    assert q.ancestors(12, True) == [5, 6, 8, 11, 12]
    assert q.ancestors(17, True) == [15, 16, 17]
    assert q.ancestors(19, True) == [15, 16, 17, 18, 19]


def test_siblings(q):
    assert q.siblings(1) == []
    assert q.siblings(2) == [3]
    assert q.siblings(5) == []
    assert q.siblings(7) == [8, 9]
    assert q.siblings(12) == []
    assert q.siblings(18) == []

    assert q.siblings(1, True) == [1]
    assert q.siblings(2, True) == [2, 3]
    assert q.siblings(5, True) == [5]
    assert q.siblings(7, True) == [7, 8, 9]
    assert q.siblings(12, True) == [12]
    assert q.siblings(18, True) == [18]
