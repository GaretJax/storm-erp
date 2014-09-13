from .crud import DeleteView, ListView

__all__ = ['DeleteView', 'ListView', 'SidebarMixin']


class SidebarMixin:
    sidebar_menu = None

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx['sidebar_menu'] = self.sidebar_menu
        return ctx
