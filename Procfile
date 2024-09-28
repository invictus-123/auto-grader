web: python manage.py collectstatic --noinput
release: python manage.py migrate --no-input
web: gunicorn my_site.wsgi
