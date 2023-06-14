from datetime import datetime

from flask import session, render_template
from flask_login import current_user
from core import db

from functools import wraps
from flask import g, request, redirect, url_for

from models import Roles


def roles_required(*roles):
    def real_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.has_role(*roles):
                return render_template('access_denied.html'), 403
            return f(*args, **kwargs)

        return wrapper

    return real_decorator


def init_hooks(app):
    @app.before_request
    def user_last_active():
        """последняя активность юзера"""
        if current_user.is_authenticated:
            user = current_user
            user.last_active = datetime.now()
            db.session.commit()
