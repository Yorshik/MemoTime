# Установка MemoTime в Docker

Этот раздел описывает процесс установки и запуска MemoTime с использованием Docker.

## Предварительные требования

- Установленный Docker и Docker Compose. Инструкции по установке можно найти на официальном сайте Docker:
  - [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - [Docker Desktop for macOS](https://docs.docker.com/desktop/install/mac-install/)
  - [Docker Desktop for Linux](https://docs.docker.com/desktop/install/linux-install/)
  - Для Linux без графической оболочки используйте Docker Engine:
    - [Debian](https://docs.docker.com/engine/install/debian/)
    - [Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- Git

## Шаги установки

1. **Клонирование репозитория:**

    ```bash
    git clone https://gitlab.crja72.ru/django/2024/autumn/course/projects/team-1.git
    cd team-1
    ```

2. **Настройка окружения:**

    - Скопируйте файл `.env.template` в `.env`:

        ```bash
        cp .env.template .env
        ```

    - Отредактируйте файл `.env`, указав необходимые параметры:
        - **`MEMOTIME_SECRET_KEY`:** Уникальный, длинный, случайный секретный ключ для обеспечения безопасности приложения. Используйте генераторы случайных строк (например, [https://djecrety.ir/](https://djecrety.ir/)).
        - **`MEMOTIME_DEBUG`:** Режим отладки Django. `True` - включен, `False` - выключен. **В продакшене должно быть `False`!**
        - **`MEMOTIME_ALLOWED_HOSTS`:** Список разрешенных доменов для приложения. `*` разрешает все домены. **В продакшене укажите реальные домены!**
        - **`MEMOTIME_DEFAULT_USER_IS_ACTIVE`:** Определяет, будут ли новые пользователи активны сразу после регистрации. `True` - активны, `False` - неактивны.
        - **`MEMOTIME_EMAIL`:** Email, используемый приложением для отправки писем.
        - **`MEMOTIME_EMAIL_PASSWORD`:** Пароль от email, используемого для отправки писем.
        - **`MEMOTIME_RATE_LIMIT`:** Ограничение частоты запросов к API (количество запросов / период времени).
        - **`MEMOTIME_RATE_LIMIT_TIMEOUT`:** Время блокировки (в секундах) после превышения лимита запросов.
        - **`POSTGRES_DB`:** Имя базы данных PostgreSQL.
        - **`POSTGRES_USER`:** Имя пользователя PostgreSQL.
        - **`POSTGRES_PASSWORD`:** Пароль пользователя PostgreSQL.
        - **`POSTGRES_HOST`:** Хост базы данных PostgreSQL.
        - **`POSTGRES_PORT`:** Порт базы данных PostgreSQL.
        - **`CELERY_BROKER_URL`:** URL брокера сообщений Celery.

3. **Сборка и запуск контейнеров:**

    ```bash
    docker compose up --build -d
    ```

    Эта команда соберет образы и запустит контейнеры в фоновом режиме. Первый запуск может занять некоторое время, так как Docker должен скачать и собрать все необходимые образы.

4. **Создание суперпользователя:**

    ```bash
    docker compose exec django python manage.py createsuperuser
    ```

    Следуйте инструкциям для создания учетной записи администратора.

5. **Доступ к приложению:**
    После запуска контейнеров приложение будет доступно в браузере по адресу `http://localhost/` или `http://127.0.0.1/`.

**Успешной установки и использования MemoTime!**
