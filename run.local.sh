ps -ef | grep "runserver" | awk '{print $2}' | xargs kill
cat twistd.pid | xargs kill
twistd -r select web --class=pyapns.server.APNSServer --port=7077
sleep 2
python manage.py runserver ec2-54-219-163-35.us-west-1.compute.amazonaws.com:8000
#python manage.py runserver 192.168.0.6:8000

