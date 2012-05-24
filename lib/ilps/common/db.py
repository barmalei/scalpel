#!/usr/bin/env python
#       
#       Copyright 2010 Andrei <vish@gravitysoft.org>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from __future__ import with_statement
import sys, threading, datetime

#
#  Data base module to centralize working with data base connections,
#  support connection pools and have a possibility to track connection
#  leakage.
#

def create_db(id, parameters):
    return Database(id, parameters)

def remove_db(id):
    pass

def get_db(id):
    return Database.getDatabase(id)

def get_dbconnection(id):
    return Database(id).getConnection()


class Database(object):
    DS_LOCK = threading.RLock()
    SOURCES = {}

    class CursorWrapper(object):
        def __init__(self, cursor, owner):
            assert cursor and owner
            self._cursor = cursor
            self._owner = owner
        
        @property
        def description(self):
            return self._cursor.description

        @property
        def rowcount(self):
            return self._cursor.rowcount
    
        def close(self): self._owner._closeMe(self)

        def callproc(self, procname, parameters=None):
            return self._cursor.callproc(procname, parameters)

        def execute(self, operation, parameters=None):
            return self._cursor.execute(operation, parameters)

        def executemany(self, operation, seq_of_parameters):
            return self._cursor.executemany(operation, seq_of_parameters)

        def fetchone(self):
            return self._cursor.fetchone()

        def fetchmany(self, size=None):
            s  = self.arraysize
            if size : s = size
            return self._cursor.fetchmany(s)
        
        def fetchall(self): 
            return self._cursor.fetchall()
         
        def nextset(self):
            return self._cursor.nextset()  
         
        @property
        def arraysize(self):
            return self._cursor.arraysize
            
        def setinputsizes(self, sizes):
            return self._cursor.setinputsizes(sizes)
            
        def setoutputsize(self, size, column=None):
            return self._cursor.setoutputsize(size, column)

        def _orig_cursor(self):
            return self._cursor


    class ConnectionWrapper(object):
        def __init__(self, connection, owner):
            assert connection and owner
            self._connection = connection
            self._creation_time = datetime.datetime.now() 
            self._owner = owner
            self._cursors = []
    
        def creationTime(self): return self._creation_time
    
        def close(self): 
            with Database.DS_LOCK:
                self._owner._closeMe(self) 
              
        def commit(self):
            return self._connection.commit()
            
        def rollback(self):
            return self._connection.rollback()
            
        def cursor(self):
            with Database.DS_LOCK:
                c = Database.CursorWrapper(self._connection.cursor(), self)
                self._cursors.append(c)
                return c

        def _closeMe(self, cur):
            with Database.DS_LOCK:
                try: i = self._cursors.index(cur)
                except ValueError: i = -1
                if i >= 0:
                    self._cursors.pop(i)
                    cur._orig_cursor().close()
                
        def cleanup(self):
            with Database.DS_LOCK:
                for cur in self._cursors:
                    try: cur._orig_cursor().close()
                    except: pass
                self._cursors = []

        def __str__(self):
            return "'%s' connection wrapper, created: " % self._owner._id  + str(self._creation_time)            
        
        def __enter__(self): pass 

        def __exit__(self, type, value, traceback):
            self.close()
      
        def _orig_conn(self):
            return self._connection
      
      
    @classmethod
    def createDatabase(cls, id, parameters):
        assert id and parameters
        with cls.DS_LOCK: 
            if id in cls.SOURCES: 
                raise BaseException("Data base '%s' already exists." % id)
            return Database(id, parameters)
                
    @classmethod
    def getDatabase(cls, id):
        assert id
        with cls.DS_LOCK: return cls.SOURCES[id]
    
    
    @classmethod
    def hasDatabase(cls, id):
        assert id
        with cls.DS_LOCK: return id in cls.SOURCES
    
    def init(self, id, parameters):
        global DBMODULE 
      
        self._poolSize = 1
        key = 'db.poolsize' 
        if  key in parameters:
            self._poolSize = int(parameters[key])     
            del parameters[key]

        self._poolLatency = self._poolSize / 5
        key = 'db.poollatency' 
        if key in parameters:
            self._poolLatency = int(parameters[key])     
            del parameters[key]
            
        assert self._poolLatency >= 0 and self._poolSize >= 0 
        if self._poolLatency > self._poolSize:
            raise BaseException("DB '%s' pool latency cannot be less than max pool size." % id)
        
        self._parameters = parameters
        self._id   = id    
        self._pool = []
        self._module = DBMODULE
        self._firstfree = 0
        
    def __new__(cls, id, parameters = None):
        assert id and len(id.strip()) > 0
        id = id.strip()
        
        with cls.DS_LOCK:
            if id in cls.SOURCES:
                ds = cls.SOURCES[id]
                if parameters and parameters != ds._parameters:
                    raise BaseException("Data base '%s' have been defined with another db parameters.")
                return ds   
            else:
                if parameters == None:
                    raise BaseException("DB parameters have not been specified for '%s' data base." % id)
                
                ds = object.__new__(cls)                
                ds.init(id, parameters)  
                ds.ping()
                cls.SOURCES[id] = ds
                return ds
        
    def ping(self):
        con = None
        try: con = self._module.connect(**self._parameters)
        finally:     
            if con : con.close()
        
    def getConnection(self):
        with self.DS_LOCK:
            # connection pool should not be used
            if self._poolSize == 0:
                return Database.ConnectionWrapper(self._module.connect(**self._parameters), owner = self) 
            else:
                # found free connection in pool
                if self._firstfree < len(self._pool): 
                   self._firstfree += 1 
                   return self._pool[self._firstfree - 1]
                else:
                    # pool is not full  
                    if  self._poolSize > len(self._pool): 
                        c = Database.ConnectionWrapper(self._module.connect(**self._parameters), owner = self) 
                        self._pool.append(c)           
                        self._firstfree = len(self._pool)
                        return c
                    else:    
                        # pool is full
                        raise BaseException("'%s' connection pool is full (%d connections opened)." % (self._id, len(self._pool)))            

    def cleanup(self):
        with self.DS_LOCK:
            for c in self._pool:
                try: c.orig_conn().close() 
                except: pass
            self._pool = []
            self._firstfree = 0    
                
    def _closeMe(self, con):
        with self.DS_LOCK:
            # pool is not supported
            if self._poolSize == 0:
                con._orig_conn().close()
            else:
                try: i = self._pool.index(con)
                except ValueError: i = -1
                if i == -1 or i >= self._firstfree:
                    raise BaseException("DB '%s' connection has been already closed." % self._id)
                    
                # check if have already enough opened free connection
                # and really close connection if it is true
                if self._poolLatency == (len(self._pool) - self._firstfree): 
                    c = self._pool.pop(i)
                    c.cleanup()
                    c._orig_conn().close() 
                else:  
                    c = self._pool.pop(i)  
                    c.cleanup()
                    self._pool.append(c)
                self._firstfree -= 1
                         

    def __str__(self):
        s = "Data base '%s' {" % self._id + "\n  Parameters:" + str(self._parameters)
        s += "\n  pool size    = %d" % self._poolSize
        s += "\n  pool latency = %d" % self._poolLatency
        s += "\n  free connections = %d" % (len(self._pool) - self._firstfree)
        s += "\n  first free pos   = %d" % self._firstfree
        s += "\n  " + str(self._pool)  + "\n}"
        return s
   

DBMODULE = None

def __LOAD_DB_MODULE__(module='MySQLdb'):
    global DBMODULE
   
    if DBMODULE and DBMODULE.__name__ != module: 
        raise BaseException("Only one db specific module can be loaded at the same time.")
    elif DBMODULE == None: 
        DBMODULE = __import__(module) 
        for k in DBMODULE.__dict__: 
            o = DBMODULE.__dict__[k]
            if k.find("Error") >=0 or k.find("Warning") >= 0:
                setattr(sys.modules[__name__], k, o)
        

if __name__ != '__main__':
	__LOAD_DB_MODULE__()
