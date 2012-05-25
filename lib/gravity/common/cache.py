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

class Cache(object):
    def __init__ (self, keyarguments=None, maxSize = 1000):
       assert maxSize > 1
       self._maxSize  = maxSize
       self._storage  = {}    
       if keyarguments != None: self._keyarguments = tuple(keyarguments)
       else                   : self._keyarguments = None
       
    def __call__(self, decorator):
        def _fetch(*args, **kargs):
            #
            # fetch inpout arguments that are supposed to be used for hash building 
            #
            parameters = []
            if self._keyarguments is None: 
                parameters.extend(args)
                for k in kargs: parameters.append(kargs[k])
            else:
                i = 0
                l = len(self._keyarguments)
                for a in args: 
                    ka = self._keyarguments[i] 
                    if ka != None: 
                        if a == None: raise BaseException("The %d ('%s') key argument is None. Not applicable value." % (i, ka)) 
                        parameters.append(a)     
                    i += 1   
                    if i >= l: break
                
                if i < l: 
                    for j in range(i, l): 
                        ka = self._keyarguments[j] 
                        if ka != None:
                            if ka not in kargs: raise BaseException("Cannot find '%s' key argument." % ka)         
                            else:
                                parameters.append(kargs[ka])
                
                
            key = self._build_key_(parameters)            
            if key not in self._storage:
                if self._maxSize > 0 and len(self._storage) == self._maxSize:
                    self._free_()
               
                value = decorator(*args, **kargs)
                self._allocate_(key, value)
                return value
            else:   
                return self._request_(key)

        return _fetch
       
    def _allocate_(self, key, value):
        self._storage[key] = value
      
    def _request_(self, key):
        return self._storage[key]
        
    def _free_(self):  
        self._storage.popitem()     
  
    def _build_key_(self, args):
        # convert into tuple since it is hash able
        return tuple(args)             
    
    def fetch(self, key):
        if key in self._storage:
            return self._storage[key]
        return None

if __name__ == '__main__':
    pass

