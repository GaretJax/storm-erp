from storm.stock.models import Location, StockUnit, Lot, Batch, Move, Warehouse


def test_move_simple(session):
    l0 = Location('1')
    l1 = Location('2')

    unit = StockUnit(sku='UNIT')
    lot = Lot(stock_unit=unit, quantity=10)

    session.add_all([l0, l1, unit, lot])

    batch = Batch()
    batch.moves.append(Move(
        stock_unit=unit,
        lot=lot,
        quantity=4,
        source=l0,
        target=l1,
    ))

    assert lot.in_stock(l0, virtual=True) == 0
    assert lot.in_stock(l1, virtual=True) == 0
    assert lot.in_stock(l0, virtual=False) == 0
    assert lot.in_stock(l1, virtual=False) == 0

    batch.schedule()

    assert lot.in_stock(l0, virtual=True) == -4
    assert lot.in_stock(l1, virtual=True) == 4
    assert lot.in_stock(l0, virtual=False) == 0
    assert lot.in_stock(l1, virtual=False) == 0

    batch.apply()

    assert lot.in_stock(l0, virtual=True) == -4
    assert lot.in_stock(l1, virtual=True) == 4
    assert lot.in_stock(l0, virtual=False) == -4
    assert lot.in_stock(l1, virtual=False) == 4


def test_stock_multiple_lots(session):
    l0 = Location('1')
    l1 = Location('2')

    unit = StockUnit(sku='UNIT')
    lot0 = Lot(stock_unit=unit, quantity=10)
    lot1 = Lot(stock_unit=unit, quantity=20)

    session.add_all([l0, l1, unit, lot0, lot1])

    batch = Batch()
    batch.moves.append(Move(
        stock_unit=unit,
        lot=lot0,
        quantity=3,
        source=l0,
        target=l1,
    ))
    batch.moves.append(Move(
        stock_unit=unit,
        lot=lot1,
        quantity=5,
        source=l1,
        target=l0,
    ))

    assert lot0.in_stock(l0, virtual=True) == 0
    assert lot0.in_stock(l1, virtual=True) == 0
    assert lot0.in_stock(l0, virtual=False) == 0
    assert lot0.in_stock(l1, virtual=False) == 0

    assert lot1.in_stock(l0, virtual=True) == 0
    assert lot1.in_stock(l1, virtual=True) == 0
    assert lot1.in_stock(l0, virtual=False) == 0
    assert lot1.in_stock(l1, virtual=False) == 0

    assert unit.in_stock(l0, virtual=True) == 0
    assert unit.in_stock(l1, virtual=True) == 0
    assert unit.in_stock(l0, virtual=False) == 0
    assert unit.in_stock(l1, virtual=False) == 0

    batch.schedule()

    assert lot0.in_stock(l0, virtual=True) == -3
    assert lot0.in_stock(l1, virtual=True) == 3
    assert lot0.in_stock(l0, virtual=False) == 0
    assert lot0.in_stock(l1, virtual=False) == 0

    assert lot1.in_stock(l0, virtual=True) == 5
    assert lot1.in_stock(l1, virtual=True) == -5
    assert lot1.in_stock(l0, virtual=False) == 0
    assert lot1.in_stock(l1, virtual=False) == 0

    assert unit.in_stock(l0, virtual=True) == 2
    assert unit.in_stock(l1, virtual=True) == -2
    assert unit.in_stock(l0, virtual=False) == 0
    assert unit.in_stock(l1, virtual=False) == 0

    batch.apply()

    assert lot0.in_stock(l0, virtual=True) == -3
    assert lot0.in_stock(l1, virtual=True) == 3
    assert lot0.in_stock(l0, virtual=False) == -3
    assert lot0.in_stock(l1, virtual=False) == 3

    assert lot1.in_stock(l0, virtual=True) == 5
    assert lot1.in_stock(l1, virtual=True) == -5
    assert lot1.in_stock(l0, virtual=False) == 5
    assert lot1.in_stock(l1, virtual=False) == -5

    assert unit.in_stock(l0, virtual=True) == 2
    assert unit.in_stock(l1, virtual=True) == -2
    assert unit.in_stock(l0, virtual=False) == 2
    assert unit.in_stock(l1, virtual=False) == -2


def test_stock_sublocations(session):
    l00 = Location('0')
    l01 = Location('0/1', parent=l00)
    l02 = Location('0/2', parent=l00)
    l10 = Location('1')
    l11 = Location('1/1', parent=l10)
    l111 = Location('1/1/1', parent=l11)

    unit = StockUnit(sku='UNIT')
    lot = Lot(stock_unit=unit, quantity=10)

    session.add_all([l00, l10, unit, lot])
    session.flush()
    session.expire(l00, ['left', 'right'])
    session.expire(l10, ['left', 'right'])
    session.expire(l11, ['left', 'right'])

    batch = Batch()

    def m(src, dst, qty):
        batch.moves.append(Move(
            stock_unit=unit,
            lot=lot,
            quantity=qty,
            source=src,
            target=dst,
        ))

    m(l00, l11, 3)
    m(l01, l11, 5)
    m(l02, l111, 7)
    m(l01, l10, 11)
    m(l02, l01, 13)
    m(l00, l111, 17)

    batch.schedule()

    # Virtual, no sublocations
    assert lot.in_stock(l00, virtual=True) == -20
    assert lot.in_stock(l01, virtual=True) == -3
    assert lot.in_stock(l02, virtual=True) == -20
    assert lot.in_stock(l10, virtual=True) == 11
    assert lot.in_stock(l11, virtual=True) == 8
    assert lot.in_stock(l111, virtual=True) == 24

    # Real, no sublocations
    assert lot.in_stock(l00, virtual=False) == 0
    assert lot.in_stock(l01, virtual=False) == 0
    assert lot.in_stock(l02, virtual=False) == 0
    assert lot.in_stock(l10, virtual=False) == 0
    assert lot.in_stock(l11, virtual=False) == 0
    assert lot.in_stock(l111, virtual=False) == 0

    # Virtual, with sublocations
    assert lot.in_stock(l00, virtual=True, include_sublocations=True) == -43
    assert lot.in_stock(l01, virtual=True, include_sublocations=True) == -3
    assert lot.in_stock(l02, virtual=True, include_sublocations=True) == -20
    assert lot.in_stock(l10, virtual=True, include_sublocations=True) == 43
    assert lot.in_stock(l11, virtual=True, include_sublocations=True) == 32
    assert lot.in_stock(l111, virtual=True, include_sublocations=True) == 24

    # Real, with sublocations
    assert lot.in_stock(l00, virtual=False, include_sublocations=True) == 0
    assert lot.in_stock(l01, virtual=False, include_sublocations=True) == 0
    assert lot.in_stock(l02, virtual=False, include_sublocations=True) == 0
    assert lot.in_stock(l10, virtual=False, include_sublocations=True) == 0
    assert lot.in_stock(l11, virtual=False, include_sublocations=True) == 0
    assert lot.in_stock(l111, virtual=False, include_sublocations=True) == 0

    batch.apply()

    # Virtual, with sublocations
    assert lot.in_stock(l00, virtual=True, include_sublocations=True) == -43
    assert lot.in_stock(l01, virtual=True, include_sublocations=True) == -3
    assert lot.in_stock(l02, virtual=True, include_sublocations=True) == -20
    assert lot.in_stock(l10, virtual=True, include_sublocations=True) == 43
    assert lot.in_stock(l11, virtual=True, include_sublocations=True) == 32
    assert lot.in_stock(l111, virtual=True, include_sublocations=True) == 24

    # Real, with sublocations
    assert lot.in_stock(l00, virtual=False, include_sublocations=True) == -43
    assert lot.in_stock(l01, virtual=False, include_sublocations=True) == -3
    assert lot.in_stock(l02, virtual=False, include_sublocations=True) == -20
    assert lot.in_stock(l10, virtual=False, include_sublocations=True) == 43
    assert lot.in_stock(l11, virtual=False, include_sublocations=True) == 32
    assert lot.in_stock(l111, virtual=False, include_sublocations=True) == 24


def test_location_repr():
    assert 'test-location' in repr(Location('test-location'))
    assert 'test-location' in repr(Warehouse('test-location'))
