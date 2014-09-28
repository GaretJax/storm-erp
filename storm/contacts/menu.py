from storm.web import menu as m


main_menu_item = m.Menu('Address book')
main_menu_item.add_all([
    m.MenuItem('Everybody', 'contacts.list_contacts'),
    m.MenuItem('Organizations', 'contacts.list_organizations'),
    m.MenuItem('People', 'contacts.list_people'),
])

contacts_menu = m.Menu('Contacts')
contacts_menu.add_grouped('Contacts', [
    m.MenuItem('Everybody', 'contacts.list_contacts'),
])
contacts_menu.add_grouped('Organizations', [
    m.MenuItem('Organizations', 'contacts.list_organizations'),
    m.MenuItem('Add a new organization', 'contacts.add_organization'),
])
contacts_menu.add_grouped('People', [
    m.MenuItem('People', 'contacts.list_people'),
    m.MenuItem('Add a new person', 'contacts.add_person'),
])
