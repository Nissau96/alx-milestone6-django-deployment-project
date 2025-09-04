web: gunicorn deployment_project.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A deployment_project worker --loglevel=info
beat: celery -A deployment_project beat --loglevel=info