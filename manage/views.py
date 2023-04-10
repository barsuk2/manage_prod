import json

from flask import Blueprint, redirect, url_for, flash
from flask import current_app, jsonify, render_template, abort, request

from core import db
from models import Task, Users
from manage.forms import TaskFormEdit

bp = Blueprint('/', __name__, url_prefix='/')


@bp.route('/<int:task_id>')
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.return_as_json())


@bp.route('/', methods=('POST', 'GET'))
@bp.route('/<int:task_id>', methods=('POST', 'GET'))
@bp.route('/<board_id>', methods=('POST', 'GET'))
def index(board_id=None, task_id=None):
    task = Task()
    if board_id and board_id not in Task.BOARDS:
        abort(400, 'Страницы не существует')
    if not board_id:
        board_id = 'Actual'
    if task_id:
        task = Task.query.get_or_404(task_id)
    form = TaskFormEdit(obj=task)
    users = Users.query.all()
    form.user_id.choices = [(0, '')] + [(user.id, user.username) for user in users]
    q = db.session.query(Task).filter(Task.board == board_id)
    tasks = q.order_by(Task.created.desc())
    if request.method == 'POST':
        a = 'sdasd, dasd'
        if form.user_id.data == 0:
            form.user_id.data = None
        if not form.board.data:
            form.board.data = board_id
        if form.tags.data:
            form.tags.data = form.tags.data.split(',')
            print(f"\033[m\033[33m {form.tags.data} \033[0m")  # желтый

        form.populate_obj(task)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('.index', board_id=board_id))
    return render_template('index.html', tasks=tasks, form=form, task=task)




# @bp.route('/post_task_/<int:task_id>', methods=('POST', 'GET'))
# def post_task_(task_id=None):
#     if task_id == 100:
#         task = Task()
#     else:
#         task = Task.query.get_or_404(task_id)
#     form = TaskFormEdit(obj=task)
#     users = Users.query.all()
#     form.user.choices = [(0, '')] + [(user.id, user.username) for user in users]
#
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             form.populate_obj(task)
#             db.session.add(task)
#             db.session.commit()
#     # return redirect(url_for('.index'))
#     return render_template('task.html', form=form, task=task)
