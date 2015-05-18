#!/bin/bash
fab  --set function=LOCATIONSERVER,henv=$2 set_hosts $1 -i ~/aws/stagewizcard.pem -u ubuntu
fab --set function=WIZSERVER,henv=$2 set_hosts $1 -i ~/aws/stagewizcard.pem -u ubuntu

