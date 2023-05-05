import time
from datetime import datetime, date, timedelta

import requests
from flask import Blueprint, redirect, url_for, flash
from flask import jsonify, render_template, abort, request
from flask_login import login_required, login_user, logout_user, current_user

from core import db
from models import Task, Users, CommentsTask, History
from manage.forms import TaskFormEdit, LoginForm, TaskCommentForm

bp = Blueprint('/', __name__, url_prefix='/')


@bp.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))


@bp.route('/', methods=('POST', 'GET'))
@bp.route('/<board_id>', methods=('POST', 'GET'))
@bp.route('/user/<int:user_id>  /tasks', methods=('POST', 'GET'))
@bp.route('/<board_id>/task/<int:task_id>', methods=('POST', 'GET'))
@bp.route('/user/<int:user_id>/tasks/<int:task_id>', methods=('POST', 'GET'))
@login_required
def index(board_id=None, task_id=None, create_task=None, user_id=None):
    task = Task()
    counter = {}
    history_task = []
    user = None
    if board_id and board_id not in Task.BOARDS:
        abort(400, 'Страницы не существует')
    if not board_id:
        board_id = 'Actual'
    if task_id:
        task = Task.query.get_or_404(task_id)
        history_task = History.query.options(db.joinedload(History.user)).filter(History.task_id == task.id)\
            .order_by(History.created.desc()).all()

    form = TaskFormEdit(obj=task)
    users = Users.query.all()
    form.user_id.choices = [(0, '')] + [(user.id, user.username) for user in users]
    q = db.session.query(Task)

    if user_id:
        user = Users.query.get_or_404(user_id)
        q = q.filter(Task.user_id == user.id)

    actual = q.filter(Task.board == 'Actual')
    q = q.filter(Task.board == board_id)

    # Считает количество задач на доске актуальное
    for stage in Task.STAGE:
        counter[stage] = actual.filter(Task.stage == stage).count()
    counter['importance'] = actual.filter(Task.importance.in_(('high', 'medium'))).count()
    counter['new'] = actual.filter(datetime.now() - Task.created <= timedelta(days=1)).count()

    # Фильтры для основного меню по доске Actual
    filter = request.args.get('filter')
    if filter:
        q = actual.filter(Task.stage == request.args.get('filter'))
    if filter and filter == 'importance':
        q = actual.filter(Task.importance.in_(('high', 'medium')))
    if filter and filter == 'new':
        q = actual.filter(datetime.now() - Task.created <= timedelta(days=1))
    tasks = q.order_by(Task.created.desc())

    if request.method == 'POST':
        # Костыль на случай, если не приходит юзер
        stage_before = task.stage
        if form.user_id.data == 0:
            form.user_id.data = None
        
        if not form.board.data:
            form.board.data = board_id
        if form.importance.data == '':
            form.importance.data = None
        if task.comments:
            comments = task.comments.copy()
            comments = [i for i in comments if i != '']
        else:
            comments = []

        form_comment = request.form.get('comment')
        comments.append(form_comment)
        task.comments = comments
        form.populate_obj(task)
        if user_id:
            task.user_id = current_user.id
        # Удаление задачи: Задача физически не удаляется, а переноситься на доску готово
        if task.stage == 'Done':
            task.board = 'Complete'
            query_string = {'user_id': user_id}
        else:
            query_string = {'user_id': user_id, 'task_id': task_id}

        db.session.add(task)
        db.session.flush()
        # todo сделать функцию логирования - добавления записей в history
        if not task.stage:
            task_status = 'Created'
            db.session.add(History(task_id=task.id, stage=task.stage, board=task.board, user_id=current_user.id,
                                   task_status=task_status, title=task.title))
        else:
            if task.stage != stage_before:
                db.session.add(History(task_id=task.id, stage=task.stage, board=task.board, user_id=current_user.id,
                                       ))
        db.session.commit()
        return redirect(url_for('.index', **query_string))
    return render_template('index.html', tasks=tasks, form=form, task=task, counter=counter,
                           history_task=history_task, user=user, filter={'filter': filter})


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


@bp.route('/delete_task/<board_id>/<int:task_id>', methods=('POST',))
@bp.route('/delete_task/<int:user_id>/<int:task_id>', methods=('POST',))
@login_required
def del_task(task_id, user_id=None, board_id=None):

    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    # todo сделать функцию логирования - добавления записей в history
    db.session.add(History(task_id=task.id, stage=task.stage, board=task.board, user_id=current_user.id,
                           task_status='Deleted', title=task.title))
    db.session.commit()
    if user_id:
        qs = {'user_id': user_id}
    else:
        qs = {'board_id': board_id, 'task_id': task_id}
    return redirect(url_for('.index', **qs))


@bp.route('/users')
@login_required
def get_users():
    users = Users.query.order_by(Users.username).all()
    return render_template('users.html', users=users)
