rabbitmqctl add_user wizcard_user wizcard_pass
rabbitmqctl add_vhost wizcard_vhost
rabbitmqctl set_permissions -p wizcard_vhost wizcard_user ".*" ".*" ".*"
