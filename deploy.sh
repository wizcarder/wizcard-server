#!/bin/bash
fab -f upstart_fabfile.py   --set function=LOCATIONSERVER,henv=test set_hosts deploy -i ~/aws/wiztest.pem -u ubuntu
fab -f upstart_fabfile.py   --set function=WIZSERVER,henv=test set_hosts deploy -i ~/aws/wiztest.pem -u ubuntu

