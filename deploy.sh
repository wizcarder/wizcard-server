#!/bin/bash
fab  --set function=LOCATIONSERVER,henv=$2,runuser=$3 set_hosts $1 -i ~/aws/stagewizcard.pem -u $3
fab --set function=WIZSERVER,henv=$2,runuser=$3 set_hosts $1 -i ~/aws/stagewizcard.pem -u $3

