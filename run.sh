#python manage.py run_gunicorn -b ec2-54-219-163-35.us-west-1.compute.amazonaws.com:8000 2>&1 | tee output.log
python manage.py runserver 192.168.0.6:8000

