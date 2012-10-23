#!/usr/bin/python
# The Wiz database module
# Implements Wiz specific database functions

# Required standard imports
import json
import pdb

# Required Wiz specific imports
import wizutils

# This class hosts all Wiz specific DB library functions
class WizDB:
    def __init__(self, db):
        self.db = db

    # Query DB and return a JSON object
    def query(self, table, key, value):
        self.cursor = self.db.cursor()
	# formulate and run the query
        sql = "SELECT * FROM %s WHERE %s='%s';" % (table, key, value)
	wizutils.log(sql)
	self.cursor.execute(sql)
	rows = self.cursor.fetchall()

	# build json object
	columns = [column[0] for column in self.cursor.description]
	tuples  = [zip(columns, row) for row in rows]
	query_result = [dict(line) for line in tuples]
	if not query_result:
	    return (json.dumps({}))
	else:
	    return (json.dumps(query_result[0]))
	self.cursor.close()

    # Query DB and return a JSON object
    def except_query(self, table, key, value):
        self.cursor = self.db.cursor()
	# formulate and run the query
        sql = "SELECT * FROM %s WHERE %s!='%s';" % (table, key, value)
	wizutils.log(sql)
	self.cursor.execute(sql)
	rows = self.cursor.fetchall()

	# build json object
	columns = [column[0] for column in self.cursor.description]
	tuples  = [zip(columns, row) for row in rows]
	query_result = [dict(line) for line in tuples]
	if not query_result:
	    return (json.dumps({}))
	else:
	    return (json.dumps(query_result))
	    #return (json.dumps(query_result[0]))
	self.cursor.close()


    # Private method for inserting a row
    def __insert(self, tablename, obj, encodeFlag):
        self.cursor = self.db.cursor()
        # get column names
        sql = "SELECT DISTINCT(column_name) FROM information_schema.columns WHERE table_name='%s';" % (tablename)
        self.cursor.execute(sql)
        keys = self.cursor.fetchall()
        columns = tuple(i[0] for i in keys)
    
        # get values
        values = tuple(obj[key] for key in columns)
	if encodeFlag:
	    row = tuple([s.encode('utf-8') for s in values])
	else:
	    row = values
        # insert into DB
        sql = "insert into %s %s values %s;" % (tablename, str(columns).replace('\'', ''), row)
        wizutils.log(sql)

	# TODO: exception handling duplicate entry
        self.cursor.execute(sql)
	self.db.commit()
	self.cursor.close()

    # Insert a JSON object into DB
    def insertJSON(self, tablename, obj):
	self.__insert(tablename, obj, True)

    # Insert a dictionary object into DB
    def insertDict(self, tablename, obj):
	self.__insert(tablename, obj, False)

    # TODO: more methods (e.g. delete, seach, existence check etc.)

# End of wizdb.py
