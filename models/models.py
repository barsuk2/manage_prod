from collections import OrderedDict

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from core import db, login_manager
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String)

    task = db.relationship('Task', backref='user')
    history = db.relationship('History', backref='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return not self.is_authenticated


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)


class Task(db.Model):
    __tablename__ = 'tasks'

    # BOARDS = {'Actual': 'Актуальные', 'Complete': 'Готовые', 'Plans': 'В планах', 'Pause': 'На паузе'}
    BOARDS = OrderedDict(
        [('Plans', 'В планах'), ('Actual', 'Актуальные'), ('Pause', 'На паузе'), ('Complete', 'Готовые')])
    STATUS = ('Job', 'Pause', 'Complete', 'Project', 'Delete', 'Created', 'Deleted')
    STAGE = ('Dev', 'Qa', 'Review', 'Release', 'Done', 'Not_started')
    IMPORTANCE = {'high': 'Высокая', 'medium': 'Средняя', 'normal': 'Обычная', 'low': 'Низкая'}

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, nullable=True)
    board = db.Column(db.Enum(*list(BOARDS.keys()), name='board'), nullable=False)
    task_status = db.Column(db.Enum(*STATUS, name='task_status'))
    stage = db.Column(db.Enum(*STAGE, name='stage'), default='Not_started', server_default='Not_started')
    created = db.Column(db.DateTime(timezone=True), server_default=db.text('now()'), nullable=False)
    deadline = db.Column(db.DateTime(timezone=True), nullable=True)
    estimate = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', onupdate='CASCADE'))
    title = db.Column(db.String)
    description = db.Column(db.String)
    tags = db.Column(db.String, nullable=True)
    importance = db.Column(db.Enum(*list(IMPORTANCE.keys()), name='importance'))
    comments = db.Column(ARRAY(db.String(32), zero_indexes=True))

    def return_as_json(self):
        resp = {
            'id': self.id,
            'parent_id': self.parent_id,
            'board': self.board,
            'task_status': self.task_status,
            'stage': self.stage,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline,
            'estimate': self.estimate,
            'tags': self.tags,
        }
        return resp


class CommentsTask(db.Model):
    __tablename__ = 'task_comments'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='SET NULL', onupdate='CASCADE'))
    title = db.Column(db.String)
    created = db.Column(db.DateTime(timezone=True), server_default=db.text('now()'), nullable=False)
    description = db.Column(db.Text())

    def return_as_json(self):
        resp = {
            'id': self.id,
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
        }
        return resp


class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='SET NULL', onupdate='CASCADE'))
    stage = db.Column(db.Enum(*Task.STAGE, name='stage'), nullable=True)
    title = db.Column(db.String)
    task_status = db.Column(db.Enum(*Task.STATUS, name='task_status'), nullable=True)
    board = db.Column(db.Enum(*list(Task.BOARDS.keys()), name='board'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', onupdate='CASCADE'))
    created = db.Column(db.DateTime(timezone=True), server_default=db.text('now()'), nullable=False)


class Roles(db.Model):
    __tablename__ = 'roles'

    ROLES = ('super')

    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True)
    created = db.Column(db.DateTime(timezone=True), server_default=db.text('now()'), nullable=False)
    roles = db.Column(ARRAY(db.String(32), zero_indexes=True))
