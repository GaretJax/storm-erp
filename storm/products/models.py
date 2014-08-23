import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from storm.database import mptt


Model = declarative_base()


class Category(mptt.MPTTBase, Model):
    __tablename__ = 'storm_product_category'
    __table_args__ = (
        sa.UniqueConstraint('parent_id', 'name'),
    )

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(120), nullable=False)
    description = sa.Column(sa.Text)
    active = sa.Column(sa.Boolean, nullable=False, default=False)


class Product(Model):
    """
    Base model for a product type.
    """
    __tablename__ = 'storm_product_product'

    id = sa.Column(sa.Integer, primary_key=True)
    upc = sa.Column(sa.String(128), unique=True, nullable=False)
    ean13 = sa.Column(sa.Integer, unique=True)
    active = sa.Column(sa.Boolean, nullable=False, default=False)
    type = sa.Column(sa.String(50), nullable=True)

    name = sa.Column(sa.Unicode(120), nullable=False)
    description = sa.Column(sa.Text)

    categories = relationship(Category, secondary=lambda: product_categories,
                              backref=backref('products'))

    __mapper_args__ = {
        'polymorphic_identity': None,
        'polymorphic_on': type,
    }

    # TODO: Add support for the following fields
    # attributes + values
    # images

    # prices?
    # uom?
    # logistic units?
    # date added/updated


product_categories = sa.Table(
    'storm_product_categories',
    sa.Column('product_id', sa.Integer, sa.ForeignKey(Product.id),
              primary_key=True),
    sa.Column('category_id', sa.Integer, sa.ForeignKey(Category.id),
              primary_key=True),
)
