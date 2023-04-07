import json

from flask import Blueprint
from flask import current_app, jsonify, render_template, abort

from core import db
from models import Task, Users
from manage.forms import TaskFormEdit

bp = Blueprint('/', __name__, url_prefix='/')


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/board/<board_id>')
def get_board(board_id=None):

    if board_id not in Task.BOARDS:
        abort(400, 'Страницы не существует')
    form = TaskFormEdit()
    users = Users.query.all()
    form.user.choices = [(0, '')] + [(user.id, user.username) for user in users]
    q = db.session.query(Task).filter(Task.board == board_id)
    tasks = q.order_by(Task.created.desc())
    return render_template('index.html', tasks=tasks, form=form)


@bp.route('/task/<int:task_id>')
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.return_as_json())
