celery -A wizcard worker -Q ocr,celery,image_upload,pushnotif,beat --loglevel=info
celery -A wizcard beat
