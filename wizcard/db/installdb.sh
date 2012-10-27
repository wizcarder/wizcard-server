#!/bin/sh

# Change the parameters here for another DB
USER=root
PWD=''
DB=wizcard
echo clear user $CLEAR_USER

# Install the schema
mysql -u$USER -p$PWD -D$DB < ~/projects/WizCard/trunk/wizcard-server/wizcard/db/schema.sql

# TODO: load static tables
# Future initialization stuff post schema creation
