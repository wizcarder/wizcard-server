#!/bin/bash
for i in wizserver celeryworker memcached twistd celeryflower celerybeat locationjob
 do
  sudo service $i status
 done

