from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from lagring import FlaskLagring

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = '.login'
login_manager.login_message = 'Авторизация'
login_manager.login_message_category = "info"
csrf = CSRFProtect()
storage = FlaskLagring()
