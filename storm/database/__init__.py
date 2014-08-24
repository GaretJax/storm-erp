"""
Utilities to work with the backing database throughout STORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from storm.config import settings


_engine = None


def get_engine():
    global _engine
    if not _engine:
        _engine = create_engine(settings.DB_URL,
                                isolation_level='SERIALIZABLE')
    return _engine


def late_binding_factory(original_factory):
    def make_session():
        return original_factory(bind=get_engine())
    return make_session


session_factory = late_binding_factory(sessionmaker())
session = _session = scoped_session(session_factory)


# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.sql.expression import ClauseElement
#
#
# def get_or_create(session, model, defaults=None, **kwargs):
#     if defaults is None:
#         defaults = {}
#
#     query = session.query(model).filter_by(**kwargs)
#     instance = query.first()
#
#     if instance:
#         return instance, False
#     else:
#         try:
#             params = dict(
#                 (k, v)
#                 for k, v in kwargs.items()
#                 if not isinstance(v, ClauseElement)
#             )
#             params.update(defaults)
#             instance = model(**params)
#
#             with session.begin_nested():
#                 session.add(instance)
#                 session.commit()
#                 return instance, True
#         except IntegrityError:
#             instance = query.one()
#             return instance, False
