from flask import Flask
from manage import bp
from core import db
from models import *


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    # csrf.init_app(app)
    app.register_blueprint(bp)
    return app
