import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy.ext.declarative import declared_attr


class StatefulMixin:
    def set_status(self, status, **kwargs):
        status_class = self.__class__.statuses.property.argument.class_
        status = status_class(status=status, **kwargs)
        self.statuses.append(status)
        return status


class StatusMixin:
    """
    Generic mixin to create status relations for stateful records.
    """

    id = sa.Column(sa.Integer, primary_key=True)
    status = sa.Column(sa.String(40), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False,
                          default=datetime.datetime.utcnow)
    comment = sa.Column(sa.Text)

    @declared_attr
    def record_id(cls):
        return sa.Column('record_id', sa.Integer,
                         sa.ForeignKey(cls.__stateful_args__['relation'].id),
                         nullable=False)

    @declared_attr
    def record(cls):
        return relationship(
            cls.__stateful_args__['relation'],
            backref=backref('statuses', order_by=lambda: cls.timestamp.desc())
        )

    @classmethod
    def __declare_last__(cls):
        relation = cls.__stateful_args__['relation']

        current_status = aliased(
            sa.select([cls.id.label('status_id'), relation.id.label('rel')])
            .where(cls.record_id == relation.id)
            .order_by(cls.timestamp.desc())
            .limit(1)
        )

        # relation.status_id = column_property(current_status.c.status_id)

        relation.status = relationship(
            cls,
            primaryjoin=current_status.c.rel == relation.id,
            secondaryjoin=current_status.c.status_id == cls.id,
            secondary=current_status,
            uselist=False,
            viewonly=True,
        )

    def __repr__(self):
        return '{}({:%Y-%m-%d %H:%M}, {!r})'.format(
            self.__class__.__name__, self.timestamp, self.status)
