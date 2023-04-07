
from core import db
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String)
    task = db.relationship('Task', backref='user')


class Task(db.Model):
    __tablename__ = 'tasks'

    BOARDS = ('Actual', 'Complete', 'Plans', 'Release')
    STATUS = ('Job', 'Pause', 'Complete', 'Project')
    STAGE = ('Dev', 'QA', 'Review', 'Release')

    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.Enum(*BOARDS, name='board'), nullable=False)
    task_status = db.Column(db.Enum(*STATUS, name='task_status'))
    stage = db.Column(db.Enum(*STAGE, name='stage'))
    created = db.Column(db.DateTime(timezone=True), server_default=db.text('now()'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', onupdate='CASCADE'))
    title = db.Column(db.String)
    description = db.Column(db.String)


    def return_as_json(self):
        resp = {
            'board': self.board,
            'task_status': self.task_status,
            'stage': self.stage,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
                }
        return resp


class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer,  db.ForeignKey('tasks.id', ondelete='SET NULL', onupdate='CASCADE'))
    task_status = db.Column(db.Enum(name='task_status'))
    board = db.Column(db.Enum(name='board'))
    stage = db.Column(db.Enum(name='stage'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', onupdate='CASCADE'))
    created = db.Column(db.DateTime(timezone=True), server_default=db.text('now()'), nullable=False)


class Roles(db.Model):
    __tablename__ = 'roles'

    ROLES = ('super')

    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    created = db.Column(db.DateTime(timezone=True), server_default=db.text('now()'), nullable=False)
    roles = db.Column(ARRAY(db.String(32), zero_indexes=True))

