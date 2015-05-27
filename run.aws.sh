ps -ef | grep "gunicorn" | grep 8000 | awk '{print $2}' | xargs kill
cat twistd.pid | xargs kill
twistd -r select web --class=pyapns.server.APNSServer --port=7077
sleep 2
#python manage.py run_gunicorn -b ec2-54-219-163-35.us-west-1.compute.amazonaws.com:8000 2>&1 | tee output.log
python manage.py run_gunicorn -b 192.168.0.6:8000 2>&1 | tee output.log

