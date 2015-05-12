#!/bin/bash
fab  --set function=LOCATIONSERVER,henv=test set_hosts $1 -i ~/aws/stagewizcard.pem -u ubuntu
fab --set function=WIZSERVER,henv=test set_hosts $1 -i ~/aws/stagewizcard.pem -u ubuntu

