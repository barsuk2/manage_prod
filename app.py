from flask import Flask

from manage import bp
from core import db, login_manager
from core import csrf
from models import *
from jinja_filter import *


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(bp)
    app.add_template_filter(len_list)
    return app
