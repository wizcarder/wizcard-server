ps -ef | grep "gunicorn" | awk '{print $2}' | xargs kill
cat twistd.pid | xargs kill
twistd -r select web --class=pyapns.server.APNSServer --port=7077

python manage.py run_gunicorn -b ec2-54-219-163-35.us-west-1.compute.amazonaws.com:8000 2>&1 | tee output.log

