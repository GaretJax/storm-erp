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

    def dispatch_request(self, **kwargs):
        self.kwargs = kwargs
        return self.render(**kwargs)

    def render(self, **ctx):
        ctx = self.get_context_data(**ctx)
        return render_template(self.template_name, **ctx)


class ListView(TemplateView):
    model = None

    def get_objects(self):
        return session.query(self.model)

    def dispatch_request(self, **kwargs):
        self.kwargs = kwargs
        return self.render(object_list=self.get_objects())


class SingleObjectMixin:
    model = None

    def get_object(self, object_id):
        obj = session.query(self.model).get(object_id)
        if not obj:
            abort(404)
        return obj


class EditView(SingleObjectMixin, TemplateView):
    model = None
    form_class = None

    def get_form_class(self):
        return self.form_class

    def get_form(self, **kwargs):
        return self.get_form_class()(**kwargs)

    def get_success_url(self):
        raise NotImplementedError

    def save_changes(self, form, object):
        form.populate_obj(object)
        return redirect(self.get_success_url())

    def create_object(self, form, object):
        form.populate_obj(object)
        session.add(object)
        return redirect(self.get_success_url())

    def dispatch_request(self, object_id=None):
        is_editing = object_id is not None

        if is_editing:
            self.object = self.get_object(object_id)
            form = self.get_form(obj=self.object)
        else:
            self.object = self.model()
            form = self.get_form()

        if form.validate_on_submit():
            if is_editing:
                return self.save_changes(form, self.object)
            else:
                return self.create_object(form, self.object)

        return self.render(is_editing=is_editing, form=form,
                           object=self.object)


class DeleteView(SingleObjectMixin, TemplateView):
    model = None
    redirect_endpoint = None

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
