from storm.web import menu as m

stock_menu_item = m.Menu('Stock management')
stock_menu_item.add_all([
    m.MenuItem('Locations', 'stock.list_warehouses'),
    m.MenuItem('Movements', 'products.list_products'),
    m.MenuItem('Reporting', 'products.list_products'),
])

stock_menu = m.Menu('Stock')
stock_menu.add_grouped('Stock moves', [
    m.RawMenuItem('Incoming shipments', '#'),
    m.RawMenuItem('Internal stock moves', '#'),
    m.RawMenuItem('Delivery orders', '#'),
])
stock_menu.add_grouped('Inventory', [
    m.RawMenuItem('Current stock information', '#'),
    m.RawMenuItem('Manage inventories', '#'),
    m.RawMenuItem('Create a new inventory', '#'),
])
stock_menu.add_grouped('Locations', [
    m.MenuItem('Manage warehouses', 'stock.list_warehouses'),
    m.MenuItem('Add a new warehouse', 'stock.add_warehouse'),
])
stock_menu.add_grouped('Reporting', [
    m.RawMenuItem('All stock moves', '#'),
    m.RawMenuItem('Product traceability', '#'),
])
