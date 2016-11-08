#!/bin/bash
for i in wizserver celeryworker celeryflower celerybeat locationjob
 do
  sudo service $i status
 done

sudo /etc/init.d/memcached status

