from flask.ext.wtf import Form
from wtforms_alchemy import model_form_factory
from storm.database import session


BaseModelForm = model_form_factory(Form)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return session
