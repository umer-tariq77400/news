release: python manage.py migrate
release: mkdir media/profile_images
release: mkdir media/article_covers
release: python manage.py collectstatic --noinput
web: gunicorn config.wsgi --log-file -