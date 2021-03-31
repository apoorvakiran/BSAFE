web: pipenv run gunicorn "app:bsafe" --workers 8 --log-file -
worker: pipenv run flask worker --threads 1
periodiq: pipenv run flask periodiq
