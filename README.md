# Room-park.ru

## Установка движка

Нам понадобятся:

- python >= 3.4
- postgresql >= 9.4
- virtualenvwrapper

На машине, где уже работали с нашими движками, всё это должно быть. На новой машине ставим их, как принято в вашей ОС. В Ubuntu 16, например, это делается так:

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

На более ранних версиях убунты берём поддерживаемые версии (python3.4, postgresql9.4).

Теперь создаём виртуальное окружение python, базу данных и директорию для изменяемых файлов:

```
$ mkvirtualenv -p python3 roompark
$ workon roompark
$ pip install -r requirements.txt
$ sudo -u postgres psql -c "CREATE USER roompark ENCRYPTED PASSWORD 'roompark'"
$ sudo -u postgres psql -c "CREATE DATABASE roompark OWNER roompark"
$ mkdir var
```

И создаём локальный конфиг движка в `/srv/room-park.ru/roompark/config.local.py`:

```python
DEBUG = True
ENVIRONMENT = 'development'
SERVER_NAME = 'local.room-park.ru'
SQLALCHEMY_DATABASE_URI = 'postgresql://roompark:roompark@localhost:5432/roompark'
MAIL_DEBUG = True
MAIL_ENABLED = True
MAIL_SINK = ('--> СЮДА-ПРОПИСАТЬ-СВОЮ-ПОЧТУ <-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!',)
ASSET_STORAGE_ROOT = '/srv/room-park.ru/var/assets'
```

Прописываем конфиг nginx (предполагается, что корень проекта находится в `/srv/room-park.ru`):

```
server {
    server_name local.room-park.ru;

    location / {
        proxy_pass http://127.0.0.1:5500;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        root /srv/room-park.ru/roompark;
        try_files $uri $uri/ =404;
        index index.html;
    }

    location /assets {
        root /srv/room-park.ru/var;
        try_files $uri $uri/ =404;
    }
}
```

## Обновление движка

После обновления кода из репозитория (и при установке тоже), нужно поставить пакеты python, накатить миграции базы и собрать фронт:

```
$ pip install -r requirements.txt
$ alembic upgrade head
$ gulp
```

## Установка правильной версии wkhtmltopdf

В проекте используется версия wkhtmltopdf "wkhtmltox-0.12.4_linux-generic-amd64" и pdfkit 0.6.1

Инструкция по установке нужного wkhtmltopdf:

```
$ apt-get remove --purge wkhtmltopdf
$ wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
$ tar xvf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
$ chown -R root:root wkhtmltox
$ cp wkhtmltox/bin/wkhtmlto* /usr/bin/
```

## Обновление базы роботов

После первоначальной установки pip install пакету robot_detection требуется обновление базы роботов

Инструкция по обновлению:

```
$ cd ~
$ wget http://www.robotstxt.org/db/all.txt
$ python .virtualenvs/roompark/lib/python{ПОДСТАВИТЬ ВЕРСИЮ}/site-packages/robot_detection.py all.txt
```

## Запуск движка

```
$ workon roompark
$ ./py.py runserver
```

## Сборка фронтенда

В корневой директории проекта запуск команды

```
$ nvm install 8; nvm use 8
$ npm install
```

1. `npm run dev` - соберёт develop-версии файлов bundle.css и bundle.js и будет смотреть за изменениями файлов в /static/develop, будут работать линтеры.
2. `npm run deploy` - соберёт production-версии файлов bundle.css и bundle.js


##Настройка ретрансляции с камеры

1. Пересобираем nginx (Debian)

`apt-get build-dep nginx`

`mkdir /tmp/build-nginx`

`cd /tmp/build-nginx`

`sudo apt-get source nginx`

`cd nginx-1.6.2/debian/modules`

`sudo git clone git://github.com/arut/nginx-rtmp-module.git`

В блоке full_configure_flags добавляем строку `--add-module=$(MODULESDIR)/nginx-rtmp-module`

`sudo nano ~/build-nginx/nginx-1.6.2/debian/rules`

Выходим и идем в директорию nginx-1.6.2

`cd ~/build-nginx/nginx-1.6.2/`

`sudo dpkg-buildpackage -b`

`cd ..`

Собираем nginx из двух установочных пакетов:

`dpkg -i nginx-common_1.6.2-5+deb8u5_all.deb nginx-full_1.6.2-5+deb8u5_amd64.deb`

2. Ставим ffmpeg

`sudo echo deb http://www.deb-multimedia.org testing main non-free >>/etc/apt/sources.list`

`sudo apt-get update`

`sudo apt-get install deb-multimedia-keyring`chown www-data:www-data hls

`sudo apt-get update`

`sudo apt-get install ffmpeg`

3. Создаем директорию для hls и лог ffmpeg

`sudo mkdir /tmp/hls && sudo chown www-data:www-data hls`

`sudo touch /var/log/nginx/ffmpeg.log && sudo chown www-data:adm /var/log/nginx/ffmpeg.log`

4. Добавляем в nginx.conf:

В http блок
```
    server {
        listen 8080;
        location /hls {
            add_header Cache-Control no-cache;

            types {
                application/vnd.apple.mpegurl m3u8;
                video/mp2t ts;
            }
        root /tmp/;
        }
    }
```
Если воркеров больше одного добавляем строку `rtmp_auto_push on;`

Далее еще один блок вставляем вне http блока:

```
    rtmp {
        server {
            listen 1935;
            chunk_size 4000;

            application cam1 {
                live on;
                exec_static ffmpeg -rtsp_transport tcp -i 'rtsp://webserver:biganto888@195.133.233.10:4445/axis-media/media.amp?videocodec=h264&streamprofile=web' -vcodec copy -acodec libfdk_aac -f flv rtmp://localhost:1935/cam1/stream 2>>/var/log/nginx/ffmpeg.log;
                hls on;
                hls_path /tmp/hls;
            }
        }
    }

```

Перезапускаем nginx

Ретрансляции должны быть доступны по адресам:

rtmp://room-park.ru:1935/cam1/stream

http://room-park.ru:8080/hls/stream.m3u8






Этот код - это веб-приложение, написанное на фреймворке Flask, которое позволяет пользователям создавать и управлять 
задачами. Оно использует базу данных SQLite и модели данных для управления задачами и пользователями. Приложение имеет 
несколько страниц, включая страницу входа в систему, главную страницу с задачами, страницу профиля пользователя и 
страницу со списком пользователей. Он также включает функции для создания, редактирования, удаления и отслеживания 
истории задач. Приложение также использует библиотеку Flask-Login для управления аутентификацией пользователей и 
Flask-WTF для создания форм. В целом, это приложение помогает пользователям эффективно управлять и отслеживать 
свои задачи.



