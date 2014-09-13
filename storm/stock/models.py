import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref, object_session
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base

from storm.database import mptt, NULL


Model = declarative_base()


class Location(mptt.MPTTBase, Model):
    """
    A named location for some stock units.
    """
    __tablename__ = 'storm_stock_location'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode, nullable=False)
    type = sa.Column(sa.String(50), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': None,
        'polymorphic_on': type,
    }

    def __init__(self, name, parent=None):
        self.name = name
        if parent is not None:
            self.parent = parent

    def __repr__(self):
        return 'Location({})'.format(self.name)

    def stock_of(self, stock_unit, lot=None, virtual=False,
                 include_sublocations=False):
        session = object_session(self)
        quant_query = (session.query(sa.func.sum(Quant.quantity))
                       .select_from(Quant)
                       .filter(Quant.stock_unit == stock_unit))

        if lot:
            assert lot.stock_unit == stock_unit
            quant_query = quant_query.filter(Quant.lot == lot)

        if not include_sublocations:
            quant_query = quant_query.filter(Quant.location == self)
        else:
            quant_query = quant_query.join(Location).filter(
                mptt.descendants(self, include_self=True))

        real = quant_query.scalar() or 0

        if virtual:
            moves_query = (session.query(sa.func.sum(Move.quantity))
                           .filter((Move.stock_unit == stock_unit) &
                                   (Move.scheduled == True) &  # NOQA
                                   (Move.executed == False)))

            if lot:
                moves_query = moves_query.filter(Move.lot == lot)

            if not include_sublocations:
                moves_in_query = moves_query.filter(Move.target == self)
                moves_out_query = moves_query.filter(Move.source == self)
            else:
                moves_query = moves_query.filter(
                    mptt.descendants(self, include_self=True))
                moves_in_query = moves_query.join(Move.target)
                moves_out_query = moves_query.join(Move.source)

            quantities = session.query(
                moves_in_query.as_scalar(),
                moves_out_query.as_scalar()
            )
            moved_in, moved_out = quantities.one()
            virtual = (moved_in or 0) - (moved_out or 0)
        else:
            virtual = 0

        return real + virtual


class Warehouse(Location):
    """
    A specialization of a location which acts as a wharehouse.
    """
    __tablename__ = 'storm_stock_warehouse'
    __table_args__ = tuple()

    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Location.id, onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True
    )

    __mapper_args__ = {
        'polymorphic_identity': 'warehouse',
    }

    def __repr__(self):
        return 'Warehouse({})'.format(self.name)


class StockUnit(Model):
    """
    Materialization of a specific product for organizational purposes in a
    single organization.
    """
    __tablename__ = 'storm_stock_unit'

    id = sa.Column(sa.Integer, primary_key=True)
    sku = sa.Column(sa.String(64), nullable=False, unique=True)
    # TODO: measurement_quantity = sa.Column(...), normalized to SI -> custom
    # in its own table (piece, carton, box, pallet,...)
    # ref to item/product (upc -> on product)

    def in_stock(self, location, virtual=False, include_sublocations=False):
        return location.stock_of(self, virtual=virtual,
                                 include_sublocations=include_sublocations)


class Lot(Model):
    """
    A production lot is a set of items of the same type which have identical
    traceability characteristics (e.g. quality, serial number, ...).
    """
    __tablename__ = 'storm_stock_lot'
    __table_args__ = (
        sa.UniqueConstraint('stock_unit_id', 'serial'),
    )

    id = sa.Column(sa.Integer, primary_key=True)
    stock_unit_id = sa.Column(sa.Integer, sa.ForeignKey(StockUnit.id),
                              nullable=False, index=True)
    serial = sa.Column(sa.String(120), nullable=True)
    quantity = sa.Column(sa.Numeric(18, 6), nullable=False)
    # TODO: add a cost here?
    # timestamp

    stock_unit = relationship(StockUnit)

    def in_stock(self, location, virtual=False, include_sublocations=False):
        return location.stock_of(self.stock_unit, lot=self, virtual=virtual,
                                 include_sublocations=include_sublocations)


class Batch(Model):
    __tablename__ = 'storm_stock_batch'

    id = sa.Column(sa.Integer, primary_key=True)

    def schedule(self):
        """
        Schedule the moves belonging to this batch by assigning concrete
        locations and lots.
        """
        self.moves.update({'scheduled': True}, synchronize_session='fetch')

    def apply(self):
        """
        Apply already scheduled stock moves by updating the quants.
        """
        session = object_session(self)

        with session.begin_nested():
            for m in self.moves:
                assert m.scheduled
                if not m.quantity:  # NOCOV
                    continue

                table = Quant.__table__

                query = (table.update()
                         .returning(table.c.id, table.c.quantity)
                         .where((table.c.location_id == m.source.id) &
                                (table.c.lot_id == m.lot.id))
                         .values(quantity=table.c.quantity - m.quantity))
                source_quant = session.execute(query).fetchone()
                if not source_quant:
                    session.add(Quant(
                        location=m.source,
                        lot=m.lot,
                        quantity=-m.quantity
                    ))

                query = (table.update()
                         .returning(table.c.id, table.c.quantity)
                         .where((table.c.location_id == m.target.id) &
                                (table.c.lot_id == m.lot.id))
                         .values(quantity=table.c.quantity + m.quantity))
                target_quant = session.execute(query).fetchone()
                if not target_quant:
                    session.add(Quant(
                        location=m.target,
                        lot=m.lot,
                        quantity=m.quantity
                    ))

                session.flush()
            self.moves.update({'executed': True}, synchronize_session='fetch')
            session.query(Quant).filter(Quant.quantity == 0).delete()


# class BatchStatus(states.StatusMixin, Model):
#    __tablename__ = 'storm_stock_batch_status'
#    __stateful_args__ = {
#        'relation': Batch,
#    }


class Move(Model):
    """
    A movement of a certain quantity of stock units belonging to a lot, from a
    location to another one.

    This relation has a minor denormalization on stock units + lots in order to
    support automatic lot selection on move scheduling.
    """
    __tablename__ = 'storm_stock_move'

    id = sa.Column(sa.Integer, primary_key=True)
    batch_id = sa.Column(sa.Integer, sa.ForeignKey(Batch.id), nullable=False)
    source_location_id = sa.Column(sa.Integer, sa.ForeignKey(Location.id),
                                   nullable=False)
    target_location_id = sa.Column(sa.Integer, sa.ForeignKey(Location.id),
                                   nullable=False)
    stock_unit_id = sa.Column(sa.Integer, sa.ForeignKey(StockUnit.id),
                              nullable=False)
    lot_id = sa.Column(sa.Integer, sa.ForeignKey(Lot.id), nullable=True)
    quantity = sa.Column(sa.Numeric(18, 6), nullable=False)

    is_scheduled = sa.Column(sa.Boolean, default=False)
    is_executed = sa.Column(sa.Boolean, default=False)

    batch = relationship(Batch, backref=backref('moves', lazy='dynamic'))
    source = relationship(Location, foreign_keys=source_location_id,
                          backref=backref('moves_from'))
    target = relationship(Location, foreign_keys=target_location_id,
                          backref=backref('moves_to'))
    stock_unit = relationship(StockUnit, backref=backref('moves'))
    lot = relationship(Lot, backref=backref('moves'))

    __table_args__ = (
        sa.UniqueConstraint('batch_id',
                            'source_location_id', 'target_location_id',
                            'stock_unit_id', 'lot_id'),
        #                    postgresql_where=lot != None),
        # sa.UniqueConstraint('batch_id',
        #                    'source_location_id', 'target_location_id',
        #                    'stock_unit_id',
        #                    postgresql_where=lot == None),
        # https://bitbucket.org/zzzeek/sqlalchemy/issue/3161/
    )


class Quant(Model):
    """
    The amount of products belonging to a certain lot in a given location.
    """
    __tablename__ = 'storm_stock_quant'
    __table_args__ = (
        sa.UniqueConstraint('location_id', 'lot_id'),
    )

    id = sa.Column(sa.Integer, primary_key=True)
    location_id = sa.Column(sa.Integer, sa.ForeignKey(Location.id),
                            nullable=False)
    lot_id = sa.Column(sa.Integer, sa.ForeignKey(Lot.id), nullable=True)
    quantity = sa.Column(sa.Numeric(18, 6), nullable=False)

    location = relationship(Location, backref=backref('quants'))
    lot = relationship(Lot, backref=backref('quants'))
    stock_unit = association_proxy('lot', 'stock_unit')

    # product
    # (cost/price/value)
    # owner
