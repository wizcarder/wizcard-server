#!/bin/bash
/usr/local/sbin/rabbitmqctl add_user wizcard_user wizcard_pass
/usr/local/sbin/rabbitmqctl add_user location_user location_pass
/usr/local/sbin/rabbitmqctl add_user reco_user reco_pass
/usr/local/sbin/rabbitmqctl add_vhost wizcard_vhost
/usr/local/sbin/rabbitmqctl add_vhost reco_vhost
/usr/local/sbin/rabbitmqctl add_vhost location_vhost
/usr/local/sbin/rabbitmqctl set_permissions -p wizcard_vhost wizcard_user ".*" ".*" ".*"
/usr/local/sbin/rabbitmqctl set_permissions -p reco_vhost reco_user ".*" ".*" ".*"
/usr/local/sbin/rabbitmqctl set_permissions -p location_vhost location_user ".*" ".*" ".*"
/usr/local/sbin/rabbitmqctl set_user_tags guest none
#rabbitmqctl set_user_tags wizcard_user administrator
#rabbitmqctl set_user_tags reco_user administrator
#rabbitmqctl set_user_tags location_user administrator
#/usr/local/sbin/rabbitmqctl delete_user guest
