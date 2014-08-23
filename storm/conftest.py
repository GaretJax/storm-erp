import pytest
from storm import database


@pytest.yield_fixture(scope='function')
def session():
    s = database.session()
    yield s
    s.rollback()
    s.close()
    database.session.remove()
