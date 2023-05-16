import json
import string
import secrets

import plotly
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
from flask_login import login_required, login_user, logout_user, current_user
from flask import redirect, url_for, flash, render_template, abort, request, jsonify

from . import bp
from core import db
from models import Task, Users, History
from manage.forms import TaskFormEdit, LoginForm, UserForm


def counter_tasks(tasks=None):
    """Возвращает количество задач на доске Актуальное"""
    counter = {}
    if not tasks:
        tasks = Task.query.filter(Task.board == 'Actual')
    for stage in Task.STAGE:
        counter[stage] = tasks.filter(Task.stage == stage).count()
    counter['importance'] = tasks.filter(Task.importance.in_(('high', 'medium'))).count()
    counter['new'] = tasks.filter(datetime.now() - Task.created <= timedelta(days=1)).count()
    return counter


def loging_stage_task(task, task_id, before_task=None):
    """ Добавляет в таблицу History движение задачи - """
    qs = {}
    if task.id != task_id:
        qs = {'task_status': 'Created', 'title': task.title}
    # Добавляем новый
    elif task.stage != before_task['stage']:
        qs = {'task_status': 'Job'}
    elif task.board == 'Complete':
        qs = {'task_status': 'Complete'}

    task_history = History(task_id=task.id, stage=task.stage, board=task.board, user_id=current_user.id, **qs)
    db.session.add(task_history)
    db.session.commit()


@bp.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))


@bp.route('/', methods=('POST', 'GET'))
@bp.route('/<board_id>', methods=('POST', 'GET'))
@bp.route('/user/<int:user_id>/tasks', methods=('POST', 'GET'))
@bp.route('/<board_id>/task/<int:task_id>', methods=('POST', 'GET'))
@bp.route('/user/<int:user_id>/task/<int:task_id>', methods=('POST', 'GET'))
@login_required
def index(board_id=None, task_id=None, user_id=None):
    counter = {}
    history_task = []
    user = None
    create_task = request.args.get('create_task')
    if board_id and board_id not in Task.BOARDS:
        abort(400, 'Страницы не существует')
    if not board_id:
        board_id = 'Actual'
    if task_id:
        task = Task.query.get_or_404(task_id)
        history_task = History.query.options(db.joinedload(History.user)).filter(History.task_id == task.id) \
            .order_by(History.created.desc()).all()
    else:
        task = Task()
    before_task = task.__dict__
    form = TaskFormEdit(obj=task)
    users = Users.query.all()
    form.user_id.choices = [(0, '')] + [(user.id, user.name) for user in users]
    q = db.session.query(Task)

    if user_id:
        user = Users.query.get_or_404(user_id)
        q = q.filter(Task.user_id == user.id)

    actual = q.filter(Task.board == 'Actual')
    q = q.filter(Task.board == board_id)

    counter = counter_tasks(q)
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
            query_string = {'user_id': user_id, 'task_id': task_id}
        else:
            query_string = {'board_id': board_id, 'task_id': task_id}
        # Удаление задачи: Задача физически не удаляется, а переноситься на доску готово
        if task.stage == 'Done':
            task.board = 'Complete'
        db.session.add(task)
        db.session.commit()
        loging_stage_task(task, task_id, before_task)

        return redirect(url_for('.index', **query_string))
    return render_template('index.html', tasks=tasks, form=form, task=task, counter=counter,
                           history_task=history_task, user=user, filter=filter, create_task=create_task)


@bp.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        password = form.password.data
        remember_my = form.remember_my.data
        user = Users.query.filter(Users.email == name).first()
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
    db.session.add(History(task_id=task.id, stage=task.stage, board=task.board, user_id=current_user.id,
                           task_status='Deleted'))
    db.session.commit()
    if user_id:
        qs = {'user_id': user_id}
    else:
        qs = {'board_id': board_id}
    return redirect(url_for('.index', **qs))


@bp.route('/users')
@login_required
def get_users():
    users = Users.query.order_by(Users.name).all()
    return render_template('users/users.html', users=users)


@bp.post('/users/delete/<int:user_id>')
@login_required
def del_user(user_id):
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('.get_users'))


@bp.route('/users/profole/<int:user_id>')
@login_required
def user_profile(user_id):
    user = Users.query.get_or_404(user_id)
    return render_template('users/profile_user.html', user=user)


@bp.route('/users/user/<int:user_id>', methods=('POST', 'GET'))
@bp.route('/users/user/new', methods=('POST', 'GET'))
@login_required
def user_edit(user_id=None):
    if user_id:
        user = Users.query.get_or_404(user_id)
    else:
        user = Users()
    form = UserForm(obj=user)
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.password.data:
                form.password.data = user.set_password(form.password.data)
            form.populate_obj(user)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('.user_edit', user_id=user.id))
        else:
            flash(form.errors, 'danger')
    return render_template('users/edit_user.html', user=user, form=form)


@bp.get('/user/generate_pass')
def generate_pass():
    alphabet = string.ascii_letters + string.digits + '-!"#$%&?@'
    password = ''.join(secrets.choice(alphabet) for _ in range(6))
    pass_ = json.dumps({'pass': password})
    return jsonify(pass_)


@bp.get('/statistic/tasks')
def get_statistic_task():
    counter = counter_tasks()
    # Generate the figure **without using pyplot**.
    df = pd.DataFrame({
        #     'Месяц': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь'],
        #     'Количество': [4, 5, 2, 2, 4, 4],
        #     # 'Доски': ['Актуальные', 'Готово', 'План', 'Актуальные', 'Готово', 'План', 'Актуальные', 'Готово', 'План']
        #     'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
        # })
        # fig = px.bar(df, x='Месяц', y='Количество', color='City', barmode='group')
        'Fruit': ['qweqwe', 'Oranges', 'Апрель', 'Apples', 'Oranges',
                  'Bananas'],
        'Amount': [4, 1, 2, 2, 4, 5],
        'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']

    })
    fig = px.bar(df, x='Fruit', y='Amount', color='City',
                 barmode='group')
    # fig = px.bar(df, x='Месяц', y='Количество', color='Доски', barmode='group')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    print(graphJSON)
    return render_template('statistic/index.html', counter=counter, graphJSON=graphJSON)

# @bp.route("/plot")
# def hello():
#     # Generate the figure **without using pyplot**.
#     df = pd.DataFrame({
#         'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges',
#                   'Bananas'],
#         'Amount': [4, 1, 2, 2, 4, 5],
#         'City': ['Казань', 'Казань', 'Казань', 'Нижний', 'Нижний', 'Нижний']
#     })
#     fig = px.bar(df, x='Fruit', y='Amount', color='City',
#                  barmode='group')
#     graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
#     return f"<img src='data:image/png;base64,{data}'/>"
