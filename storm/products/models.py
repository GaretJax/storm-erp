import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from storm.database import mptt


Model = declarative_base()


class Category(mptt.SortableMPTTBase, Model):
    __tablename__ = 'storm_product_category'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(120), nullable=False)
    description = sa.Column(sa.Text)
    is_active = sa.Column(sa.Boolean, nullable=False, default=False)

    @declared_attr
    def __table_args__(cls):
        # NOTE: This is a terrible hack, but it *should* be used at migration
        # *generation* time only, so it *might* be safe. This should be fixed
        # upstream (in sqlalchemy_mptt), though!
        mptt.SortableMPTTBase.__tablename__ = cls.__tablename__
        table_args = mptt.SortableMPTTBase.__table_args__
        del mptt.SortableMPTTBase.__tablename__
        # NOTE: Hack end

        return table_args + (
            sa.UniqueConstraint('parent_id', 'name'),
        )

    def path(self):
        path = self.name
        if self.parent:
            path = '{} / {}'.format(self.parent.path(), path)
        return path


class Product(Model):
    """
    Base model for a product type.
    """
    __tablename__ = 'storm_product_product'

    id = sa.Column(sa.Integer, primary_key=True)
    upc = sa.Column(sa.String(128), unique=True, nullable=False)
    ean13 = sa.Column(sa.BigInteger, unique=True)
    is_active = sa.Column(sa.Boolean, nullable=False, default=False)
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
    'storm_product_categories', Model.metadata,
    sa.Column('product_id', sa.Integer, sa.ForeignKey(Product.id),
              primary_key=True),
    sa.Column('category_id', sa.Integer, sa.ForeignKey(Category.id),
              primary_key=True),
)


class Image(Model):
    __tablename__ = 'storm_product_image'

    id = sa.Column(sa.Integer, primary_key=True)


class AttributeType(Model):
    __tablename__ = 'storm_product_attributetype'

    id = sa.Column(sa.Integer, primary_key=True)
    key = sa.Column(sa.String(120), unique=True, nullable=False)
    name = sa.Column(sa.Unicode(120), nullable=False)
    description = sa.Column(sa.Text)


class ProductAttribute(Model):
    __tablename__ = 'storm_product_attributes'

    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.id),
                           primary_key=True)
    attribute_type_id = sa.Column(sa.Integer, sa.ForeignKey(AttributeType.id),
                                  primary_key=True)
    value = sa.Column(sa.Unicode(255))
