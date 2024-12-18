# MemoTime
for windows install gevent
![pipeline status](https://gitlab.crja72.ru/django/2024/autumn/course/team-1/badges/main/pipeline.svg)

## Запуск проекта

### Установка зависимостей

Убедитесь, что python установлен, только после этого устанавливайте зависимости

### Windows

```bash
cd C:/project/path/requirements
pip install -r dev.txt
```

#### Linux

```bash
cd /project/path/requirements
pip3 install -r dev.txt
```

#### Mac OS

```bash
cd /project/path/requirements
pip3 install -r dev.txt
```

### Установка PostgreSQL (база данных)

#### Windows

Загрузите и установите PostgreSQL с официального сайта [PostgreSQL](https://www.postgresql.org/download/).

После установки PostgreSQL убедитесь, что сервис запущен. Возможно, потребуется создать пользователя и базу данных для проекта. Подробности по созданию пользователя и базы данных можно найти в документации PostgreSQL. Скорее всего, вам потребуется выполнить запрос подобный следующему (замените `your_user` и `your_database` на ваши данные):

```sql
CREATE USER your_user WITH PASSWORD 'your_password';
CREATE DATABASE your_database OWNER your_user;
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql
```

#### Mac OS

```bash
brew install postgresql
```

### Применение миграций

В зависимости от вашей ОС, команды могут немного отличаться

```bash
cd /project/path/memotime
python3 manage.py migrate
```

или

```bash
cd C:/project/path/memotime
py manage.py migrate
```

### Запуск проекта

Также, в зависимости от ОС, команды могут отличаться

```bash
python3 manage.py runsever
```

или

```bash
py manage.py runserver
```

## Переменные окружения

### MEMOTIME_SECRET_KEY

Секретный ключ, которые генерирует Джанго

### MEMOTIME_DEBUG

Режим дебага, True - дебаг включен, отображается debug toolbar

Так как используется база данных PostgreSQL ее нужно настроить:

### POSTGRES_DB

Имя базы

### POSTGRES_USER

Имя пользователя, требуется для управления базой данных

### POSTGRES_PASSWORD

Пароль для пользователя

### POSTGRES_HOST

Хост, на котором находится сервер PostgreSQL, по умолчанию - localhost

### POSTGRES_PORT

Порт, который сервер PostgreSQL использует для связи, по умолчанию - 5432
