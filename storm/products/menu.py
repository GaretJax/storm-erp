from storm.web import menu as m

contacts = m.Menu('Address book')
contacts.add_all([
    m.MenuItem('Organizations', 'products.list_categories'),
    m.MenuItem('People', 'products.list_products'),
])

catalog = m.Menu('Catalog')
catalog.add_all([
    m.MenuItem('Categories', 'products.list_categories'),
    m.MenuItem('Products', 'products.list_products'),
])

stock = m.Menu('Stock management')
stock.add_all([
    m.MenuItem('Locations', 'products.list_products'),
    m.MenuItem('Movements', 'products.list_products'),
    m.MenuItem('Reporting', 'products.list_products'),
])

main_menu = m.Menu('Main menu')
main_menu.add_all([
    contacts,
    catalog,
    stock,
])

categories_menu = m.Menu('Categories')
categories_menu.add_all([
    m.MenuItem('Manage categories', 'products.list_categories'),
    m.MenuItem('Add a new category', 'products.add_category'),
])


products_menu = m.Menu('Products')
products_menu.add_all([
    m.MenuItem('Manage products', 'products.list_products'),
    m.MenuItem('Add a new product', 'products.add_product'),
])
