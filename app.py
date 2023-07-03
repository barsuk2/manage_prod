from flask import Flask

from manage import bp
from core import db, login_manager, storage
from core import csrf
from models import *
from jinja_filter import filters
from hooks import init_hooks


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    init_hooks(app)
    db.init_app(app)
    csrf.init_app(app)
    storage.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(bp)
    for filter in filters:
        app.add_template_filter(filter)
    return app
