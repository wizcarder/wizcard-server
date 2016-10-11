from __future__ import generators
#raw db access for location server
class WizcardDB(object):
    # Open database connection
    def __init__(self, socket, user, passwd, db):
        import MySQLdb
        self.db = MySQLdb.connect(
                    host=socket,
                    user=user,
                    passwd=passwd,
                    db=db)

        self.cursor = self.db.cursor()

    # execute SQL query using execute() method.
    def table_select(self, query):
        self.cursor.execute(query)
        
    #An iterator that uses fetchmany to keep memory usage down"
    def ResultIter(self, arraysize=1000):
        while True:
            results = self.cursor.fetchmany(arraysize)
            if not results:
                break
            for result in results:
                yield result

    # Fetch a single row using fetchone() method.
    def fetch_one(self):
        self.data = self.cursor.fetchone()

    # disconnect from server
    def close(self):
        self.db.close()
