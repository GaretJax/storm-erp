import time
import importlib

from flask import Flask, g, request, render_template
from flask.ext.wtf.csrf import CsrfProtect
from flask.ext.principal import Principal
from flask.ext.mail import Mail
from flask.ext.babel import Babel
from werkzeug.debug import DebuggedApplication
from sqltap.wsgi import SQLTapMiddleware
from raven.contrib.flask import Sentry

import storm
from storm import database
from storm.config import settings

from . import menu as m


def create_app():
    app = Flask(__name__, template_folder='../frontend/templates',
                static_folder='../frontend/static')
    app.config.from_object(settings)

    # app.config['LOGIN_DISABLED'] = False

    # Enable debugging interface when needed
    if app.config['DEBUG']:
        app.wsgi_app = SQLTapMiddleware(app.wsgi_app)
        app.wsgi_app.start()
        app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
        app.debug = True

    # Enable requests throttling during testing
    if app.config['TESTING']:
        @app.before_request
        def throttle():
            time.sleep(float(request.cookies.get('delay', 0)))

    # Configure Sentry logging
    app.config['SENTRY_USER_ATTRS'] = ['username', 'first_name', 'last_name',
                                       'email']
    app.sentry = Sentry(app)

    # Babel support
    app.babel = Babel(app)

    # Database support
    @app.teardown_request
    def shutdown_session(exc):
        session = database.session()
        if exc is None:
            session.commit()
        else:
            session.rollback()
        session.close()
        database.session.remove()
        return exc

    # Outgoing emails support
    app.mail = Mail(app)

    # CSRF protection for POST requests
    csrf = CsrfProtect()
    csrf.init_app(app)

    # Flask-pricinpal
    app.principal = Principal(app)

    # Expose metadata in the templates
    app.jinja_env.globals.update({
        '__version__': storm.__version__,
        '__commit__': storm.__commit__,
    })

    # Requests timing support
    @app.before_request
    def request_start_time():
        g.start = time.time()

    @app.after_request
    def rendering_time(response):
        try:
            diff = time.time() - g.start
            if response.response and isinstance(response.response, list):
                r = response.response
                timing = '{:3.0f} ms'.format(diff * 1000).encode('ascii')
                r[0] = r[0].replace(b'__EXECUTION_TIME__', timing)
                response.headers["content-length"] = len(r[0])
        finally:
            return response

    # Error handlers
    if not app.config['DEBUG']:
        @app.errorhandler(404)
        def page_not_found(e):
            app.sentry.captureException()
            return (
                render_template('404.html', error_id=app.sentry.last_event_id),
                404
            )

        @app.errorhandler(403)
        def forbidden(e):
            app.sentry.captureException()
            return (
                render_template('403.html', error_id=app.sentry.last_event_id),
                403
            )

        @app.errorhandler(500)
        def server_error(e):
            app.sentry.captureException()
            return (
                render_template('500.html', error_id=app.sentry.last_event_id),
                500
            )

    # Support proxied url scheme header
    def handler(environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return app(environ, start_response)

    # Register views and blueprints
    @app.route('/')
    def index():
        return '<h1>Welcome to Storm!</h1> __EXECUTION_TIME__'

    @app.route('/logos/')
    def logos():
        return render_template('logos.html')

    app.main_menu = m.Menu('Main menu')

    blueprints = [
        ('storm.contacts.controllers.contacts_frontend', '/contacts'),
        ('storm.products.controllers.products_frontend', '/products'),
        ('storm.stock.controllers.stock_frontend', '/stock'),
    ]

    for bp_path, url_prefix in blueprints:
        module_path, blueprint_name = bp_path.rsplit('.', 1)
        blueprint = getattr(importlib.import_module(module_path),
                            blueprint_name)
        app.register_blueprint(blueprint, url_prefix=url_prefix)

    # Global context processors
    @app.context_processor
    def menu_processor():
        return {'menu': app.main_menu}

    return handler
