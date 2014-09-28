from storm.web import menu as m

main_menu_item = m.Menu('Catalog')
main_menu_item.add_all([
    m.MenuItem('Categories', 'products.list_categories'),
    m.MenuItem('Products', 'products.list_products'),
])

products_menu = m.Menu('Products')
products_menu.add_grouped('Categories', [
    m.MenuItem('Manage categories', 'products.list_categories'),
    m.MenuItem('Add a new category', 'products.add_category'),
])
products_menu.add_grouped('Products', [
    m.MenuItem('Manage products', 'products.list_products'),
    m.MenuItem('Add a new product', 'products.add_product'),
    m.MenuItem('Manage attributes', 'products.list_products'),
])
