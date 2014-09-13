from flask import Blueprint, render_template, redirect, url_for, abort, flash
import sqlalchemy as sa

from storm.database import session, mptt
from storm.web.views import DeleteView, ListView, SidebarMixin

from . import models, forms
from .menu import main_menu, categories_menu, products_menu


products_frontend = Blueprint('products', __name__,
                              template_folder='templates')


@products_frontend.context_processor
def menu_processor():
    return {
        'menu': main_menu,
    }




class ListCategories(SidebarMixin, ListView):
    sidebar_menu = categories_menu
    template_name = 'products/categories.html'

    def get_objects(self):
        categories = (session.query(models.Category)
                      .order_by(models.Category.sort_order,
                                models.Category.name))
        categories = mptt.organize(categories)
        return categories

products_frontend.add_url_rule(
    '/categories/',
    view_func=ListCategories.as_view('list_categories')
)


@products_frontend.route('/categories/new/', methods=['GET', 'POST'],
                         endpoint='add_category')
@products_frontend.route('/categories/<int:category_id>/',
                         methods=['GET', 'POST'])
def edit_category(category_id=None):
    edit = category_id is not None

    if edit:
        category = session.query(models.Category).get(category_id)
        if not category:
            abort(404)
        form = forms.CategoryForm(obj=category)
    else:
        category = models.Category()
        form = forms.CategoryForm()

    if form.validate_on_submit():
        form.populate_obj(category)
        if not edit:
            category.sort_order = (
                session.query(sa.func.max(models.Category.sort_order) + 1)
                .filter(models.Category.parent == form.parent.data)
                .scalar()
            )
            session.add(category)
            flash('The category was correctly created.', 'success')
        else:
            flash('The category was correctly updated.', 'success')
        return redirect(url_for('.list_categories'))

    return render_template('products/edit_category.html', edit=edit,
                           sidebar_menu=categories_menu, form=form,
                           object=category)


@products_frontend.route('/categories/move/', methods=['POST'])
def move_category():
    form = forms.CategoryMoveForm()
    if form.validate_on_submit():
        form.save()
        return 'OK'
    else:
        abort(400)


class DeleteCategory(SidebarMixin, DeleteView):
    sidebar_menu = categories_menu
    model = models.Category
    template_name = 'products/delete_category.html'
    redirect_endpoint = '.list_categories'

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx['children_count'] = (session.query(self.model)
                                 .filter(mptt.descendants(ctx['object']))
                                 .count())
        return ctx

    def deleted(self):
        flash('The category was correctly deleted.', 'success')
        return super().deleted()

products_frontend.add_url_rule(
    '/categories/<int:object_id>/delete/',
    view_func=DeleteCategory.as_view('delete_category'),
    methods=['GET', 'POST']
)


class ListProducts(SidebarMixin, ListView):
    sidebar_menu = products_menu
    template_name = 'products/products.html'

    def get_objects(self):
        products = (session.query(models.Product)
                    #.filter(models.Product.is_active)
                    )
        return products

products_frontend.add_url_rule(
    '/', view_func=ListProducts.as_view('list_products'))


@products_frontend.route('/new/', methods=['GET', 'POST'],
                         endpoint='add_product')
@products_frontend.route('/<int:product_id>/',
                         methods=['GET', 'POST'])
def edit_product(product_id=None):
    edit = product_id is not None

    if edit:
        product = session.query(models.Product).get(product_id)
        if not product:
            abort(404)
        form = forms.ProductForm(obj=product)
    else:
        product = models.Product()
        form = forms.ProductForm()

    if form.validate_on_submit():
        form.populate_obj(product)
        if not edit:
            product.is_active = True
            session.add(product)
            flash('The product was correctly created.', 'success')
        else:
            flash('The product was correctly updated.', 'success')
        return redirect(url_for('.list_products'))

    return render_template('products/edit_product.html', edit=edit,
                           sidebar_menu=products_menu, form=form)
