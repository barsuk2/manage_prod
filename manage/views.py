import time
from datetime import datetime, date, timedelta

import requests
from flask import Blueprint, redirect, url_for, flash
from flask import jsonify, render_template, abort, request
from flask_login import login_required, login_user, logout_user, current_user

from core import db
from models import Task, Users, CommentsTask
from manage.forms import TaskFormEdit, LoginForm, TaskCommentForm

bp = Blueprint('/', __name__, url_prefix='/')


@bp.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))


@bp.post('/task/<int:task_id>/add_comment')
@login_required
def task_add_comment(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskCommentForm(obj=request.form)
    comment = CommentsTask(task_id=task.id, title=form.title.data, description=form.description.data)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.index', task_id=task_id, board_id=task.board, add_comment=1))


@bp.route('/task/<int:task_id>')
@login_required
def get_task(task_id):
    resp = {}
    comment_ = {}
    task = Task.query.get_or_404(task_id)
    resp['task'] = task.return_as_json()
    comments = CommentsTask.query.filter_by(task_id=task_id).order_by(CommentsTask.created.desc()).all()
    for ind, comment in enumerate(comments):
        comment_[str(ind)] = comment.return_as_json()
    resp['comments'] = comment_
    resp['task'] = task.return_as_json()
    return jsonify(resp)


@bp.route('/', methods=('POST', 'GET'))
@bp.route('/<board_id>/<int:task_id>', methods=('POST', 'GET'))
@bp.route('/<board_id>/<create_task>', methods=('POST', 'GET'))
@bp.route('/<board_id>', methods=('POST', 'GET'))
@login_required
def index(board_id=None, task_id=None, create_task=None):
    task = Task()
    comments = []
    counter = {}
    if board_id and board_id not in Task.BOARDS:
        abort(400, 'Страницы не существует')
    if not board_id:
        board_id = 'Actual'
    if task_id:
        task = Task.query.get_or_404(task_id)
        comments = CommentsTask.query.filter_by(task_id=task_id).order_by(CommentsTask.created.desc()).all()
    add_comment = request.args.get('add_comment')

    form = TaskFormEdit(obj=task)
    form_comments = TaskCommentForm(obj=task)
    users = Users.query.all()
    form.user_id.choices = [(0, '')] + [(user.id, user.username) for user in users]
    q = db.session.query(Task)

    # Считает количество задач на доске актуальное
    actual = q.filter(Task.board == 'Actual')
    q = q.filter(Task.board == board_id)

    for stage in Task.STAGE:
        counter[stage] = actual.filter(Task.stage == stage).count()

    counter['importance'] = actual.filter(Task.importance.in_(('high', 'medium'))).count()
    counter['new'] = actual.filter(datetime.now() - Task.created <= timedelta(days=1)).count()

    # Filter Actual
    if request.args.get('a_filter'):
        q = actual.filter(Task.stage == request.args.get('a_filter'))

    if request.args.get('a_importance'):
        q = actual.filter(Task.importance.in_(('high', 'medium')))

    if request.args.get('a_new'):
        q = actual.filter(datetime.now() - Task.created <= timedelta(days=1))

    tasks = q.order_by(Task.created.desc())
    if request.method == 'POST':
        if form.user_id.data == 0:
            form.user_id.data = None
        if not form.board.data:
            form.board.data = board_id
        if form.importance.data == '':
            form.importance.data = None
        form.populate_obj(task)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('.index', task_id=task_id, board_id=task.board))
    return render_template('index.html', tasks=tasks, form=form, task=task, form_comments=form_comments,
                           comments=comments, create_task=create_task, add_comment=add_comment, counter=counter)


@bp.route('/my_tasks')
@bp.route('/my_tasks/<int:task_id>', methods=('POST', 'GET'))
@login_required
def mytask(task_id=None):
    """
    Список моих задач
    """
    counter = {}
    user = current_user
    task = Task()
    if task_id:
        task = Task.query.get_or_404(task_id)
        comments = CommentsTask.query.filter_by(task_id=task_id).order_by(CommentsTask.created.desc()).all()
    form = TaskFormEdit(obj=task)
    q = db.session.query(Task)
    # Считает количество задач на доске актуальное
    q = q.filter(Task.board == 'Actual', Task.user_id == user.id)

    for stage in Task.STAGE:
        counter[stage] = q.filter(Task.stage == stage).count()

    counter['importance'] = q.filter(Task.importance.in_(('high', 'medium'))).count()
    counter['new'] = q.filter(datetime.now() - Task.created <= timedelta(days=1)).count()

    # Filter Actual
    if request.args.get('a_filter'):
        q = q.filter(Task.stage == request.args.get('a_filter'))

    if request.args.get('a_importance'):
        q = q.filter(Task.importance.in_(('high', 'medium')))

    if request.args.get('a_new'):
        q = q.filter(datetime.now() - Task.created <= timedelta(days=1))
    tasks = Task.query.filter(Task.user_id == user.id, Task.board == 'Actual')
    return render_template('my_tasks.html', tasks=tasks, counter=counter, form=form)


@bp.route('my/task/<int:task_id>', methods=('GET', 'POST'))
@login_required
def task_edit(task_id, ):
    """
    Редактировать задачу
    """
    task = db.session.query(Task).get_or_404(task_id)
    comment = db.session.query(CommentsTask).filter(CommentsTask.task_id == task.id).all()
    form = TaskFormEdit(obj=task)

    if request.method == 'POST':
        form.stage.data = request.form.get('stage')
        print(form.stage.data)
        form.populate_obj(task)
        if task.stage == 'Done':
            task.board = 'Complete'
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('.task_edit', task_id=task.id))
    return render_template('task.html', task=task, form=form, comment=comment)


@bp.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        password = form.password.data
        remember_my = form.remember_my.data
        user = Users.query.filter(Users.username == name).first()
        if not user or not user.check_password(password):
            flash('Логин/Пароль не найден', 'danger')
        else:
            param = {'remember': True} if remember_my is True else {}
            login_user(user, **param)
            return redirect(url_for('.index'))
    return render_template('login.html', form=form)


@bp.route('/delete_task/<board_id>/<int:task_id>')
@login_required
def del_task(board_id, task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('.index', board_id=board_id))


@bp.route('/users')
@login_required
def get_users():
    users = Users.query.order_by(Users.username).all()
    return render_template('users.html', users=users)
