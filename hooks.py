from datetime import datetime

from flask import session
from flask_login import current_user
from core import db


def init_hooks(app):

    @app.before_request
    def user_last_active():
        """последняя активность юзера"""
        if current_user.is_authenticated:
            user = current_user
            user.last_active = datetime.now()
            db.session.commit()

