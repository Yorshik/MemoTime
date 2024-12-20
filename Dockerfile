FROM python:3.12.4

RUN apt-get update && apt-get install -y gettext

COPY ./requirements /requirements
RUN pip install -r requirements/dev.txt

COPY ./memotime /memotime/
WORKDIR /memotime

RUN mkdir -p /memotime/logs

CMD ["gunicorn", "memotime.wsgi:application", "--workers", "$(nproc)", "--bind", "0.0.0.0:8000", "--access-logfile", "/memotime/logs/gunicorn_access.log", "--error-logfile", "/memotime/logs/gunicorn_error.log"]