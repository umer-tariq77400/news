release: python manage.py migrate
release: mkdir -p media/profile_images media/article_covers
release: python manage.py collectstatic --noinput
web: gunicorn config.wsgi --log-file -