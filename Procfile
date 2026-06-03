web: python manage.py migrate --noinput && python manage.py create_default_users && python manage.py collectstatic --noinput && gunicorn afronight_manager.wsgi --bind 0.0.0.0:$PORT
