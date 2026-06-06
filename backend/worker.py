from tasks import celery_app

# Этот файл просто импортирует celery_app из tasks.py
# и служит точкой входа для запуска воркера командой:
# celery -A worker worker --loglevel=info