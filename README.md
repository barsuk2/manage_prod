# Task tracker

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
$ sudo -u postgres psql -c "CREATE USER mp_base ENCRYPTED PASSWORD 'mp_base'"
$ sudo -u postgres psql -c "CREATE DATABASE roompark OWNER mp_base"
```


