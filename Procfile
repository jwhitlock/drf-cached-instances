#web: python manage.py run_gunicorn -b "0.0.0.0:$PORT" -w 3
web: gunicorn sample_site.wsgi --log-file -
