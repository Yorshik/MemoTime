## Установка MemoTime в Docker

Этот раздел описывает процесс установки и запуска MemoTime с использованием Docker.

### Предварительные требования

- Установленный Docker и Docker Compose. Инструкции по установке можно найти на официальном сайте Docker:
  - [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - [Docker Desktop for macOS](https://docs.docker.com/desktop/install/mac-install/)
  - [Docker Desktop for Linux](https://docs.docker.com/desktop/install/linux-install/)
  - Для Linux без графической оболочки используйте Docker Engine:
    - [Debian](https://docs.docker.com/engine/install/debian/)
    - [Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- Git

### Шаги установки

1. **Клонирование репозитория:**

   ```bash
   git clone c:\Users\05mba\Desktop\programing\dev\project_team-1\memotime
   cd memotime
   ```

2. **Настройка окружения:**
   - Скопируйте файл `apps/.env.example` в `apps/.env`:

     ```bash
     cp apps/.env.example apps/.env
     ```

   - Отредактируйте файл `apps/.env`, указав необходимые параметры:
     - **`SECRET_KEY`:** Сгенерируйте надежный секретный ключ.
     - **`DATABASE_URL`:**  Настройте подключение к базе данных PostgreSQL (если не используете дефолтные настройки).
     - **`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`:** Укажите данные для отправки email.
     - **`TELEGRAM_BOT_TOKEN`:** Вставьте токен вашего Telegram бота.
     - **`ALLOWED_HOSTS`:** Добавьте `*`
     - **`CSRF_TRUSTED_ORIGINS`:** Добавьте `http://127.0.0.1`, `http://localhost`

3. **Сборка и запуск контейнеров:**

   ```bash
   docker compose up --build -d
   ```

   Эта команда соберет образы и запустит контейнеры в фоновом режиме. Первый запуск может занять некоторое время, так как Docker должен скачать и собрать все необходимые образы.

4. **Выполнение миграций:**

   ```bash
   docker compose exec web python manage.py migrate
   ```

5. **Создание суперпользователя:**

   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

   Следуйте инструкциям для создания учетной записи администратора.

6. **(Опционально) Сбор статики:**

   ```bash
   docker compose exec web python manage.py collectstatic --noinput
   ```

7. **Доступ к приложению:**
   После запуска контейнеров приложение будет доступно в браузере по адресу `http://localhost/` или `http://127.0.0.1/`.

## Дополнительные команды Docker Compose

- **Остановить контейнеры:**

  ```bash
  docker compose down
  ```

- **Перезапустить контейнеры:**

  ```bash
  docker compose restart
  ```

- **Посмотреть логи контейнера `web`:**

  ```bash
  docker compose logs -f web
  ```

- **Пересобрать образы:**

  ```bash
  docker compose build
  ```

- **Удалить неиспользуемые образы:**

  ```bash
  docker image prune
  ```

- **Удалить все неиспользуемые образы и тома:**

   ```bash
   docker system prune -a --volumes
   ```

## Примечания

- Убедитесь, что порты, указанные в `docker-compose.yml`, не заняты другими приложениями.
- Если вы вносите изменения в код, вам нужно пересобрать образы с помощью команды `docker compose build` и перезапустить контейнеры `docker compose up --build -d`.
- Для работы Celery необходимо, чтобы Redis был запущен и доступен в контейнере `web`.
- Убедитесь, что в настройках `ALLOWED_HOSTS` в файле `apps/.env` указаны все хосты, с которых будет доступно приложение.
- `CSRF_TRUSTED_ORIGINS` пропишите доверенные хосты.

## Устранение неполадок

- Если у вас возникли проблемы с подключением к базе данных, убедитесь, что параметры `DATABASE_URL` в файле `apps/.env` указаны правильно.
- Если приложение не запускается, проверьте логи контейнеров с помощью команды `docker compose logs`.
- Ошибки в коде, допущенные после запуска контейнеров, не отражаются на работе приложения. Для их исправления необходимо пересобирать образы (`docker compose build`) и перезапускать контейнеры (`docker compose up --build -d`).

**Успешной установки и использования MemoTime!**
