import string
import secrets
from datetime import timedelta, date, datetime
import random

from app import create_app
from flask_script import Manager, Command, Server, Shell, Option

from core import db
from models import Users, Task

app = create_app()
manager = Manager(app)


class AddFakeTasks(Command):
    option_list = (
        Option('--total_tags', '-t', help='Какое количество задач добавить каждому юзеру'),
    )

    def run(self, total_tags=0):
        details = string.ascii_letters
        boards = list(Task.BOARDS.keys())
        users = Users.query.all()
        stages = Task.STAGE
        month = date.today().month
        importance = list(Task.IMPORTANCE.keys())
        tags = ['feature', 'bugfix', 'front', 'end']

        for user in users:
            for _ in range(int(total_tags)):
                created = datetime.now() - timedelta(days=1 * 30 * random.randint(0, month))
                deadline = created + timedelta(days=random.randint(0, 10))
                completed = created + timedelta(days=random.randint(0, 20))
                board = secrets.choice(boards)
                stage = secrets.choice(stages)
                importance_ = secrets.choice(importance)
                tag = secrets.choice(tags)
                user_id = user.id
                if stage == 'Done':
                    board = 'Complete'

                if board == 'Complete':
                    stage = 'Done'
                if board == 'Plans':
                    deadline = None
                    user_id = None
                task = Task(board=board, stage=stage, description='fake',
                            created=created, deadline=deadline, completed=completed, importance=importance_, tags=tag,
                            user_id=user_id, title=''.join(secrets.choice(details) for _ in range(10)))
                # tags =
                # importance =
                # comments =
                # task_status =
                # deadline =
                # estimate =
                db.session.add(task)
            db.session.flush()
            db.session.commit()
            db.session.commit()


class DelFakeTasks(Command):
    def run(self):
        fake_tasks = Task.query.filter(Task.description == 'fake')
        for task in fake_tasks:
            db.session.delete(task)
        db.session.commit()


class AddFakeUsers(Command):
    option_list = (
        Option('--total_users', '-t', help='Какое количество юзеров добавить'),
    )

    def run(self, total_users):
        details = string.ascii_letters

        for kwargs in range(int(total_users)):
            name = ''.join(secrets.choice(details) for _ in range(4))
            email = name + '@' + name + '.ru'

            param = {'email': email, 'name': name, 'password_hash': 'fake_user'}
            user = Users(**param)

            db.session.add(user)
            db.session.commit()


class Super(Command):
    '''Создает super юзера'''
    option_list = (
        Option('--name', '-n', help='Имя пользователя'),
        Option('--email', '-e', help='Email пользователя'),
        Option('--password', '-p', help='Пароль пользователя'),
    )

    def run(self, name, email, password):
        param = {'email': email, 'name': name, 'password_hash': Users.hash_password(password)}
        user = Users(**param)
        db.session.add(user)
        db.session.commit()


manager.add_command('add-fake-users', AddFakeUsers())
manager.add_command('super', Super())
manager.add_command('add-fake-task', AddFakeTasks())
manager.add_command('del-fake-task', DelFakeTasks())

if __name__ == "__main__":
    manager.run()
