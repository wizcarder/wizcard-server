#!/bin/sh

# Change the parameters here for another DB
USER=root
PWD=''
DB=wizcard

# Install the schema
mysql -u$USER -p$PWD -D$DB < /Users/aammundi/stuff/django/wizcard/wizcard/db/schema.sql

# TODO: load static tables
# Future initialization stuff post schema creation
