from uwsgidecorators import postfork

from .app import create_app


class UwsgiPostforkingApp:
    """
    A wrapper for a Flask app factory which buils a new app only after having
    been forked.
    """
    def __init__(self, app_factory):
        self._instance = None
        self._factory = app_factory

        @postfork
        def _init_app():
            self._instance = self._factory()

    def __call__(self, *args, **kwargs):
        return self._instance(*args, **kwargs)


app = UwsgiPostforkingApp(create_app)
