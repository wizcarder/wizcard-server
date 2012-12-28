#!/bin/sh

# Change the parameters here for another DB
USER=root
PWD=''
DB=wizcard
echo clear user $CLEAR_USER
ACTION=$1
echo $ACTION

# Install the schema
mysql -u$USER -p$PWD -D$DB < ./wizcard/db/schema.sql


if [ "$ACTION"=="delete" ];
then
echo "dropping tables"
mysql -u$USER -p$PWD -D$DB < ./wizcard/db/drop.sql
fi

# TODO: load static tables
# Future initialization stuff post schema creation
