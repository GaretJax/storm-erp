from storm.web import menu as m


main_menu_item = m.Menu('Address book')
main_menu_item.add_all([
    m.MenuItem('Organizations', 'products.list_categories'),
    m.MenuItem('People', 'products.list_products'),
])
