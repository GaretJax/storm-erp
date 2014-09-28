from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms_alchemy import model_form_factory
from storm.database import session


BaseModelForm = model_form_factory(Form)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return session


class MPTTMoveForm(Form):
    def validate(self):
        if not super().validate():
            return False
        fields = [self.instance, self.parent, self.previous_sibling]
        instances = [f.data for f in fields if f.data]
        if len(instances) != len(set(instances)):
            return False
        if self.previous_sibling.data:
            if self.previous_sibling.data.parent != self.parent.data:
                return False
        return True

    def save(self):
        self.instance.data.move(inside=self.parent.data,
                                after=self.previous_sibling.data)

    @staticmethod
    def _make_field(factory, label, allow_blank):
        return QuerySelectField(query_factory=factory,
                                blank_text='--- No parent ---',
                                get_label=label,
                                allow_blank=allow_blank)

    @classmethod
    def for_query_factory(cls, query_factory, label=None):
        return type('MPTTMoveForm', (cls,), {
            'instance': cls._make_field(query_factory, label, False),
            'parent': cls._make_field(query_factory, label, True),
            'previous_sibling': cls._make_field(query_factory, label, True),
        })
