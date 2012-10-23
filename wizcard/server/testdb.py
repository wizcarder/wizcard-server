#!/usr/bin/python

# This module loads test data, eventually should use wizdb module

# Required imports (stdlibs)
import json
import sys
import MySQLdb as mdb

# Required imports (Wiz specific)
import wizutils

def usage():
    print 'Usage: python testdb.py <filename> <tablename>'
    sys.exit(-1)

def add_row(cursor, tablename, rowdict):
    # get column names
    sql = "SELECT column_name FROM information_schema.columns WHERE table_name='%s';" % (tablename)
    cursor.execute(sql)
    keys = cursor.fetchall()
    columns = tuple(i[0] for i in keys)

    # get values
    values = tuple(rowdict[key] for key in columns)
    row = tuple([s.encode('utf-8') for s in values])

    # insert into MySQL
    sql = "insert into %s %s values %s;" % (tablename, str(columns).replace('\'', ''), row)
    wizutils.log(sql)
    cursor.execute(sql)

def main():
    # parse command line args
    args = sys.argv[1:]
    if len(args) != 2:
        usage()
    filename = args[0]
    tablename = args[1]
    wizutils.log('Loading file: ', filename)

    # open connection to MySQL
    wizdb = mdb.connect('localhost', 'root', '', 'test')
    cursor = wizdb.cursor()

    # load the file into DB
    with open(filename) as instream:
	row = json.load(instream)
	add_row(cursor, tablename, row)

    wizdb.commit()

if __name__ == '__main__':
    main()
