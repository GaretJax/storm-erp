from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement


class CreateView(Executable, ClauseElement):
    def __init__(self, name, select):
        self.name = name
        self.select = select


class DropView(Executable, ClauseElement):
    def __init__(self, name):
        self.name = name


@compiles(CreateView)
def visit_create_view(element, compiler, **kw):
    select = compiler.process(element.select, literal_binds=True)
    return 'CREATE VIEW {} AS {}'.format(element.name, select)


@compiles(DropView)
def visit_drop_view(element, compiler, **kw):
    return 'DROP VIEW {}'.format(element.name)


def create_view(op, name, statement):
    view = CreateView(name, statement)
    op.execute(view)


def drop_view(op, name):
    op.execute(DropView(name))
