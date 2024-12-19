FROM python:3.12.4

RUN apt update
RUN apt install gettext -y

COPY ./requirements /requirements
RUN pip install -r requirements/dev.txt
RUN rm -rf requirements

COPY ./memotime /memotime/
WORKDIR /memotime

CMD python manage.py makemigrations \
  && python manage.py migrate \
  && python manage.py init_superuser \
  && python manage.py compilemessages \
  && python manage.py collectstatic --no-input \
  && gunicorn memotime.wsgi:application \
  --workers $(nproc) \
  --bind 0.0.0.0:8000 \
  --access-logfile /memotime/logs/gunicorn_access.log \
  --error-logfile /memotime/logs/gunicorn_error.log