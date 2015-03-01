#python manage.py celery worker -Q wizcard --loglevel=debug
#python manage.py celery worker --loglevel=info
#celery -A wizcard worker --loglevel=info -B -D
celery -A wizcard worker --loglevel=info -D
celery -A wizcard beat
#rabbitmqctl add_user ocr_user ocr$
#rabbitmqctl add_vhost ocr$
#rabbitmqctl set_permissions -p ocr ocr_user ".*" ".*" ".*"$

