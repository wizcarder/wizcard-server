#!/bin/bash
rabbitmqctl add_user wizcard_user wizcard_pass
rabbitmqctl add_user location_user location_pass
rabbitmqctl add_vhost wizcard_vhost
rabbitmqctl set_permissions -p wizcard_vhost wizcard_user ".*" ".*" ".*"
rabbitmqctl set_permissions -p '/' location_user ".*" ".*" ".*"
rabbitmqctl set_user_tags guest none
rabbitmqctl set_user_tags wizcard_user administrator
#rabbitmqctl delete_user guest
