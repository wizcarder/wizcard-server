ps -ef | grep "gunicorn" | grep 8000 | awk '{print $2}' | xargs kill
cat twistd.pid | xargs kill
twistd -r select web --class=pyapns.server.APNSServer --port=7077
sleep 2
gunicorn wizcard.wsgi:application -b ec2-54-219-163-35.us-west-1.compute.amazonaws.com:8000 2>&1 | tee output.log

