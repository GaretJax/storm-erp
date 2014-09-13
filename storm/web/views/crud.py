from flask import abort, render_template, redirect, url_for
from flask.views import View

from storm.database import session

from flask.ext.wtf import Form


def confirmed():
    return Form().validate_on_submit()


class TemplateView(View):
    template_name = None

    def get_context_data(self, **ctx):
        return ctx

    def render(self, **ctx):
        ctx = self.get_context_data(**ctx)
        return render_template(self.template_name, **ctx)


class ListView(TemplateView):
    model = None

    def get_objects(self):
        return session.query(self.model)

    def dispatch_request(self):
        return self.render(object_list=self.get_objects())


class DeleteView(TemplateView):
    model = None
    redirect_endpoint = None

    def get_object(self, object_id):
        obj = session.query(self.model).get(object_id)
        if not obj:
            abort(404)
        return obj

    def dispatch_request(self, object_id):
        obj = self.get_object(object_id)
        if confirmed():
            self.delete(obj)
            return self.deleted()
        else:
            return self.render(
                object=obj,
                form=Form(),
                back_url=url_for(self.redirect_endpoint),
            )

    def delete(self, object):
        session.delete(object)

    def deleted(self):
        return redirect(url_for(self.redirect_endpoint))
