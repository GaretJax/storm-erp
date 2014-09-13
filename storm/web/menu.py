"""
Support for dynamically generated menus.
"""

from flask import render_template, url_for


class Menu:
    def __init__(self, label, template='menu/_menu.html'):
        self.label = label
        self.template = template
        self._items = []

    def add(self, item):
        self._items.append(item)

    def add_all(self, items):
        self._items.extend(items)

    def add_grouped(self, label, items):
        self._items.append(GroupedItems(label, items))

    def __iter__(self):
        for item in self._items:
            yield item

    def __html__(self):
        return render_template(self.template, menu=self)


class RawMenuItem:
    def __init__(self, label, url, template='menu/_item.html'):
        self.label = label
        self.template = template
        self._url = url

    @property
    def url(self):
        url = self._url
        if callable(url):
            url = url()
        return url

    def __html__(self):
        return render_template(self.template, item=self)


class MenuItem(RawMenuItem):
    def __init__(self, label, url, template='menu/_item.html'):
        super().__init__(label, lambda: url_for(url), template)


class GroupedItems(object):
    def __init__(self, label, items=None, template='menu/_group.html'):
        self.label = label
        self.template = template
        self._items = items if items else []

    def add(self, item):
        self._items.append(item)

    def __iter__(self):
        for item in self._items:
            yield item

    def __html__(self):
        return render_template(self.template, group=self)
