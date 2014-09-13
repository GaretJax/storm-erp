from flask import Blueprint, render_template, redirect, url_for, abort, flash
import sqlalchemy as sa

from storm.database import session, mptt
from storm.web.views import DeleteView, ListView, SidebarMixin, EditView

from . import models, forms
from .menu import main_menu_item, products_menu
from .menu import stock_menu_item  # TODO: Move to its own module


products_frontend = Blueprint('products', __name__,
                              template_folder='templates')


@products_frontend.record_once
def register_menuitem(state):
    state.app.main_menu.add(main_menu_item)
    state.app.main_menu.add(stock_menu_item)


class ListCategories(SidebarMixin, ListView):
    sidebar_menu = products_menu
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


@products_frontend.route('/categories/add/', methods=['GET', 'POST'],
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
                           sidebar_menu=products_menu, form=form,
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
    sidebar_menu = products_menu
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
        return session.query(models.Product)

products_frontend.add_url_rule(
    '/', view_func=ListProducts.as_view('list_products'))


class EditProduct(SidebarMixin, EditView):
    model = models.Product
    form_class = forms.ProductForm
    template_name = 'products/edit_product.html'
    sidebar_menu = products_menu

    def get_success_url(self):
        return url_for('.list_products')

    def save_changes(self, form, object):
        flash('The product was correctly updated.', 'success')
        return super().create_object(form, object)

    def create_object(self, form, object):
        flash('The product was correctly created.', 'success')
        object.is_active = True
        return super().create_object(form, object)

products_frontend.add_url_rule('/add/', methods=['GET', 'POST'],
                               view_func=EditProduct.as_view('add_product'))
products_frontend.add_url_rule('/<int:object_id>/', methods=['GET', 'POST'],
                               view_func=EditProduct.as_view('edit_product'))
