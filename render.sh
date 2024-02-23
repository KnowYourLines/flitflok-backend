python manage.py makemigrations api
python manage.py migrate
python manage.py collectstatic --no-input
gunicorn --bind 0.0.0.0:"$PORT" server.wsgi:application