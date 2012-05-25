#!/usr/bin/env python
#       
#       Copyright 2009 Andrei <vish@gravitysoft.org>
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
import os, cPickle, re


class CatalogIndex(object):

    # name of the file to store generated aggregation files list 
    _INDEX_FILE_NAME = '.indexfile'
    
    def __init__(self, root):
        assert root
        if not os.path.exists(root) or not os.path.isdir(root): 
            raise IOError("Wrong root '%s'." % root)
        
        self._root       = os.path.abspath(root)
        self.indexfiles = {}
        self._index_was_loaded = False
        self._is_dirty = False
        self._indexfile = os.path.join(self._root, CatalogIndex._INDEX_FILE_NAME) 
        
    @property
    def indexfile(self): return self._indexfile 
 
    @property
    def root(self): return self._root
 
    def put(self, file, status = None):
        file = self._check_and_norm(file)
  
        self._load()
        if file in self.indexfiles and self.indexfiles[file] == status:
            return 
        
        self.indexfiles[file] = status
        self._is_dirty = True
 
    def status(self, file):
        file = self._check_and_norm(file)

        self._load()
        return self.indexfiles[file]
 
    def ls(self, mask = None, status=None):
        self._load()
        if mask == None and status == None: 
            for path in self.indexfiles: yield (path, self.indexfiles[path])    
        else:
            matcher = None 
            if mask != None : matcher = re.compile(mask)
            for path in self.indexfiles:
                if (matcher is None or matcher.match(path)) and\
                   (status is None or status == self.indexfiles[path]):
                    yield (path, self.indexfiles[path])    
     
    def flush(self):
        if self._is_dirty:
            f = open(self.indexfile, 'w')
            try:     cPickle.dump(self.indexfiles, f, protocol = 2)
            finally: f.close()
            self._is_dirty = False
    
    def cleanup(self):
        if os.path.exists(self.indexfile): os.remove(self.indexfile)
            
        self.indexfiles = {}    
        self._index_was_loaded = False
        self._is_dirty = False
   
    def _load(self):
        if self._index_was_loaded: return
        
        if os.path.exists(self.indexfile):
            f = open(self.indexfile, 'r')
            try: self.indexfiles = cPickle.load(f)
            finally: f.close()
        else:
            self.indexfiles = {}
        
        self._index_was_loaded = True
        
    def _check_and_norm(self, file):
        assert file
        
        file = os.path.normpath(file)
        if os.path.isabs(file): 
            prefix = os.path.commonprefix([self.root, file])
            if self.root != prefix:
                raise IOError("File '%s' doesn't belong to catalog." % file)
            file = file[len(prefix) + 1:]
        else:                    
            if not os.path.exists(os.path.join(self.root, file)): 
                raise IOError("File '%s' doesn't exist" % file)
        
        return file


def main():

    root = '/home/barmalei/projects/bridge/data/part1-test-subset'
    index = CatalogIndex(root)


#    for f and range(100000): 
        
    print index._check_and_norm('./70700.xml')     
    print index._check_and_norm('70700.xml')     
    print index._check_and_norm('/home/barmalei/projects/bridge/data/part1-test-subset/70700.xml')     

 
 
    
    
    index.put('./70700.xml')
    index.flush()
    index.put('./70700.xml')
    index.put('./70710.xml')
    index.put('./70711.xml', 3)

    for i in index.ls(status=None):
        print i[0]

    index.cleanup()

    for i in index.ls():
        print i[0]

    for i in index.ls('.*71.*'):
        print i[0]



if __name__ == '__main__':
	main()
    
    #raise BaseException("Module is not executable")
