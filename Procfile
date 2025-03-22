release: python manage.py migrate
web: gunicorn config.wsgi --log-file -

heroku ps:scale web=1
