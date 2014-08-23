from storm.database import get_engine, session


def test_serializable():
    engine = get_engine()
    engine.dialect.isolation_level == 'SERIALIZABLE'
    session.connection().dialect.isolation_level == 'SERIALIZABLE'
