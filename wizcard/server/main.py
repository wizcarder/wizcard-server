#!/usr/bin/python

# The WizCard HTTP Server
# The main entry point for the Wiz server. All HTTP requests are handled here.

# Required standard imports
import json
import sys
from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
import MySQLdb as mdb
import pdb

# Required Wiz specific imports
import wizutils
from wizreq import WizRequestHandler
from wizdb import WizDB

# Test messages
ack = {"status": "ok"}
nack = {"status": "fail"}
stats = {"metric": "dummy"}

# The global Wiz request server. This is of type WizRequestHandler.
global wizser

# HTTP requests GET and POST are handled by this class
class WizHTTPRequestHandler (BaseHTTPRequestHandler) :
    def do_POST(self):            
        global wizser
        try:
            wizutils.log('POST: ', self.headers.getheader('content-type'), 
                self.headers['content-length'])
            if self.headers.has_key('content-length'):
                length = int( self.headers['content-length'] )

                # read data posted in URL request
                data = self.rfile.read( length )

                # extract the parameters passed to URL
                data.split('&')

                # deserialize json document to a python object
                request = json.loads(data)

                # process request
                response = wizser.processRequest(request)

            	# send a blank line to end headers:
            	self.wfile.write("\n")

                # send a response back to client
		self.wfile.write(response)

            else:
                wizutils.log('POST: ', 'Error no data')
        except Exception as excp:
            wizutils.log(excp)

    def do_GET(self) :
        wizutils.log('GET: ', self.path)
        if self.path == "/me" :
            # send response code:
            self.send_response(200)

            # send headers:
            self.send_header("Content-type:", "text/html")

            # send a blank line to end headers:
            self.wfile.write("\n")

            # send response:
            json.dump(stats, self.wfile)

def usage():
    print 'Usage: python wizserver.py <port>'
    sys.exit(-1)

def main():
    global wizser

    # parse command line args
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    port = int(args[0])
    wizutils.log('Starting WizServer on port: ', port)

    # The HTTP server object
    server = HTTPServer(("localhost", port), WizHTTPRequestHandler)

    # MySQL connection
    # TODO: connection parameters to be read from a configuration file
    db = mdb.connect('localhost', 'root', '', 'test')
    db.autocommit(True)

    # WizDB object
    wizdb = WizDB(db)

    # The Wiz request handler
    wizser = WizRequestHandler(wizdb)
    
    # The event loop!
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        wizutils.log('Shutting down Wizserver')
        server.socket.close()

if __name__ == '__main__':
    main()
