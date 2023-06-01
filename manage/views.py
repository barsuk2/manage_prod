import json
import string
import secrets

import plotly
import plotly.graph_objs as go
import plotly.express as px
import datetime
from sqlalchemy import extract, literal_column
import pandas as pd
from flask_login import login_required, login_user, logout_user, current_user
from flask import redirect, url_for, flash, render_template, abort, request, jsonify, current_app

from . import bp
from core import db
from models import Task, Users, History
from manage.forms import TaskFormEdit, LoginForm, UserForm, StatisticFilter


def counter_tasks(tasks=None):
    """Возвращает количество задач на доске Актуальное"""
    counter = {}
    if not tasks:
        tasks = Task.query.filter(Task.board == 'Actual')
    for stage in Task.STAGE:
        counter[stage] = tasks.filter(Task.stage == stage).count()
    counter['importance'] = tasks.filter(Task.importance.in_(('high', 'medium'))).count()
    counter['new'] = tasks.filter(datetime.datetime.now() - Task.created <= datetime.timedelta(days=1)).count()
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
        query_string = {'user_id': user_id, 'task_id': task_id}
        # Удаление задачи: Задача физически не удаляется, а переноситься на доску готово
        query_string.update({'filter': filter})
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
    form = StatisticFilter()
    user_id = request.args.get('user')
    users = Users.query.order_by(Users.name).all()
    year = datetime.date.today().year
    period = request.args.get('period')

    periods = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь',
               'декабрь']
    periods = list(zip(range(1, 13), periods))
    form.user.choices = [('all', 'По всем')] + [(user.id, user.name) for user in users]
    form.period.choices = [('current_year', 'Текущий год')] + list(periods)

    normal_tasks = db.session.query(Task.user_id, db.func.count().label('normal')) \
        .filter(extract('year', Task.completed) == year,
                Task.completed < Task.deadline).group_by(Task.user_id)

    tasks = db.session.query(Task.user_id, Users.name, db.func.count().label('tasks')) \
        .filter(extract('year', Task.completed) == year) \
        .join(Users).group_by(Task.user_id, Users.name).order_by(Users.name)

    if user_id and user_id != 'all':
        user = Users.query.get_or_404(user_id)
        normal_tasks = normal_tasks.filter(Task.user_id == user.id)
        tasks = tasks.filter(Task.user_id == user.id)
    if period != 'current_year':
        normal_tasks = normal_tasks.filter(extract('month', Task.completed) == period)
        tasks = tasks.filter(extract('month', Task.completed) == period)
        # SQL запрос
        # select name,  count(tasks.id), ( select count(*) from tasks where user_id  = 106 and
        # extract(year from completed) = 2023 and extract(month from completed) = 2 and completed < deadline)
        # as normal, ( select count(*) from tasks where user_id  = 106 and extract(year from completed) = 2023
        # and extract(month from completed) = 2 and completed >= deadline) as overdue from tasks join
        # users u on u.id = tasks.user_id where u.id  = 106 and extract(year from completed) = 2023 and
        # extract(month from completed) = 2 group by name;

    tasks_by_months = db.session.query(extract('month', Task.completed).label('month'), Users.name,
                                       db.func.count(Task.id).label('tasks')). \
        filter(extract('year', Task.completed) == year).join(Users).group_by(literal_column('month'), Users.name)

    df_tasks = pd.read_sql_query(tasks.statement, current_app.config.get('SQLALCHEMY_DATABASE_URI'),
                                 index_col='user_id')
    df_normal = pd.read_sql_query(normal_tasks.statement, current_app.config.get('SQLALCHEMY_DATABASE_URI'),
                                  index_col='user_id')
    df_tasks = df_tasks.join(df_normal)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_tasks['name'],
        y=df_tasks['tasks'],
        name='Выполнено задач',
        textposition="inside",
        texttemplate="%{y}",
        textfont_color="white",
        marker_color='indianred'
    ))
    fig.add_trace(go.Bar(
        x=df_tasks['name'],
        y=df_tasks['normal'],
        name='Задачи выполенные в срок',
        marker_color='green',
        texttemplate="%{y}",
        textposition="inside",
        textangle=0,
        textfont_color="white",
    ))
    fig.update_layout(
        title=go.layout.Title(
            text="Диаграмма выполенные задачи<br><sup>Дополнительно - задачи выполенные в срок</sup>",
            xref="paper",
            x=0
        ),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text=f"Разработчики<br><sup>{period}</sup>"
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text="Задачи <br><sup>Количество задач за выбранный период</sup>"
            )
        ),

    )
    df = pd.read_sql_query(tasks_by_months.statement, current_app.config.get('SQLALCHEMY_DATABASE_URI'))
    diagrams = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    fig_ = px.bar(df, x='month', y='tasks', color='name', title="Сводная по месячно по каждому разработчику<br>"
                                                                "<sup>Католичество задач за выбранный период</sup>",
                  text_auto=True, barmode='group')
    diagrams_by_months = json.dumps(fig_, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('statistic/index.html', counter=counter, diagrams=diagrams,
                           diagrams_by_months=diagrams_by_months, form=form)
