#!/usr/bin/python

# The test data loader

# Required imports (stdlibs)
import json
import sys
from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
import MySQLdb as mdb

# Required imports (Wiz specific)
import utils
from wizreq import WizRequestHandler

def usage():
    print 'Usage: python testdb.py <filename>'
    sys.exit(-1)

def add_row(cursor, tablename, rowdict):

    # filter out keys that are not column names

    sql = "SELECT column_name FROM information_schema.columns WHERE table_name='%s';" % tablename
    print sql
    cursor.execute(sql)

    columns = cursor.fetchall()
    
    print columns
    keys = tuple(i[0] for i in columns)
    print keys
    values_template = ", ".join(["%s"] * len(keys))
    print values_template

    sql = "insert into %s (%s) values (%s)" % ( 
        tablename, keys, values_template)
    print sql
    values = tuple(rowdict[key] for key in keys)
    print values
    cursor.execute(sql, values)

def main():

    # parse command line args
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    filename = args[0]
    utils.wizlog('Loading file: ', filename)

    wizdb = mdb.connect('localhost', 'pranay', 'birdie', 'pranay_db')
    cursor = wizdb.cursor()
    tablename = 'wiz_card_user'

    # load the file into DB
    with open(filename) as instream:
	row = json.load(instream)
	print row
        row = tuple(i[1] for i in row)
	print row
	row = [s.encode('utf-8') for s in row]
	print row
	add_row(cursor, tablename, row)

if __name__ == '__main__':
    main()
