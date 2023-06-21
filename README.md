# Task tracker
Трекер задач - это основная часть проекта, которая предназначена для отслеживания и управления задачами. Она включает в 
себя функции создания, редактирования и удаления задач, а также просмотра списка задач и их статусов. 

Раздел админка. 
Юзеры и роли
Данный раздел служит для управления юзерами.Добавление, удаление, присвоение ролей.

Статистика
Данный раздел служит для просмотра статистических данных о юзерах и задачах за текущий год.

## Установка движка
Нам понадобятся:

- python >= 3.4
- postgresql >= 9.4
- virtualenvwrapper


```
# Python, PostgreSQL:
$ sudo apt-get install postgresql-9.5 postgresql-server-dev-9.5 python3.5 python3.5-dev python-pip

# Virtualenvwrapper:
$ sudo pip install virtualenvwrapper
$ mkdir ~/.virtualenvs
$ export WORKON_HOME=~/.virtualenvs
$ echo ". /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
$ . ~/.bashrc
```

```
$ mkvirtualenv -p python3 manage_prod
$ workon manage_prod
$ pip install -r requirements.txt
$ sudo -u postgres psql -c "CREATE USER mp_owner ENCRYPTED PASSWORD 'mp_owner'"
$ sudo -u postgres psql -c "CREATE DATABASE mp_base OWNER mp_owner"
```


