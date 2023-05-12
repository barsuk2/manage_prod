from flask import Blueprint

bp = Blueprint('/', __name__, url_prefix='/')

from . import views
