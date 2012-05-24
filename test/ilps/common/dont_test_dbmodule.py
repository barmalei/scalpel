from __future__ import with_statement
import unittest, os

from ilps.common import db
from ilps.common.config import Configuration

db_config = Configuration()
db_config.read(os.path.join(os.path.dirname(__file__), "test_db.conf"))

class TestDBModule(unittest.TestCase):
 
    def test_usage(self):
        self.assertRaises(db.DatabaseError, self.create_wrong_db)
    
    def test_pool(self):
        # create and res-use test
        d1 = self.create_db("id")
        d2 = db.Database("id")
        self.assertEqual(d1, d2)
        d2.cleanup()
        
        # create idetical data base should raise exception
        def f(): self.create_db("id")
        self.assertRaises(db.DatabaseError, f)        
        
        # put two connections into pool
        c1 = d1.getConnection()
        c2 = d1.getConnection()
        self.assertEqual(d1._connections(), 2)
        self.assertEqual(d1._inactive_connections(), 0)

        # close one connection
        c1.close()
        self.assertEqual(d1._connections(), 2)
        self.assertEqual(d1._inactive_connections(), 1)

        # double close connection to check error handling    
        self.assertRaises(db.DatabaseError, c1.close)        

        # close second connection
        c2.close()
        self.assertEqual(d1._connections(), 1)
        self.assertEqual(d1._inactive_connections(), 1)

        # c2 should be unpooled (should not be referenced anymore) 
        # nevertheless the real connection is still opened
        self.assertRaises(db.DatabaseError, c1.close)        

        # the second connection should not be closed, just pooled, but 
        # the old reference to this connection should be invalid
        c3 = d1.getConnection()
        self.assertNotEqual(c2, c3)
        self.assertEqual(d1._connections(), 1)
        self.assertEqual(d1._inactive_connections(), 0)
    
        # cleanup data base
        d1.cleanup()
        self.assertEqual(d1._connections(), 0)
        self.assertEqual(d1._inactive_connections(), 0)
        self.assertRaises(db.DatabaseError, c3.close)        

        # test database with no pooling 
        d = self.create_db("TestZero", 1, 0)
        c = d.getConnection()
        self.assertEqual(d._connections(), 1)
        self.assertEqual(d._inactive_connections(), 0)

        # No connetion has ro be pooled after closing connection
        c.close()
        self.assertEqual(d._connections(), 0)
        self.assertEqual(d._inactive_connections(), 0)

        # test error handling if more then it possible connections have     
        # been requested
        c = d.getConnection()
        self.assertRaises(db.DatabaseError, d.getConnection)        
        d.cleanup()

        # test if object implements "with" paradigm correctly 
        with d.getConnection() as con:
            self.assertTrue(con != None)        


        # test global cleanup
        d1 = self.create_db("db1")
        d2 = self.create_db("db2")
        d1.getConnection()
        cc = d1.getConnection()
        cc.close()
        d2.getConnection()
        d2.getConnection()
        d2.getConnection()
        self.assertEqual(d1._connections(), 2)
        self.assertEqual(d1._inactive_connections(), 1)
        self.assertEqual(d2._connections(), 3)
        self.assertEqual(d2._inactive_connections(), 0)
        db.Database.cleanupDatabases()        
        self.assertEqual(d1._connections(), 0)
        self.assertEqual(d1._inactive_connections(), 0)
        self.assertEqual(d2._connections(), 0)
        self.assertEqual(d2._inactive_connections(), 0)
        db.cleanup_databases()


    def test_destroy(self):
        d = self.create_db("destroy")
        del d
                
    def test_exception_decorator(self):
        def error_handler(e):
            raise e    
        
        @db.exception_decorator(handler=error_handler)
        def do_something_with_db():
            self.create_wrong_db()
        
        self.assertRaises(db.DatabaseError, do_something_with_db)
        

    def create_wrong_db(self):
        db.create_database( "test", {'db':'wrong_dbname'} )
                
    def create_db(self, id, poolsize=3, poollatency=1):
        section = 'db'
        self.db     = db_config.get_string(section, 'db')
        self.host   = db_config.get_string(section, 'host')
        self.user   = db_config.get_string(section, 'user')
        self.passwd = db_config.get_string(section, 'passwd')
        self.params = { 'db':self.db, 'user':self.user, 'passwd':self.passwd, 'host':self.host, 'db.poolsize':poolsize, 'db.poollatency':poollatency}
        return db.create_database(id, self.params)        

if __name__ == '__main__':
    unittest.main()
