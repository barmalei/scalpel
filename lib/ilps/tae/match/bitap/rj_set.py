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

from rj import fRj, fRjBase
from ilps.tae.distance import fDistance 


class fRjExact(fRjBase):
    def compute(self, ch): 
        self.rightshift()
        self.AND(self.alphabet().S(ch))
        return self

 
class fRjInsert(fRjExact):
    def __init__(self, pattern = None):
        fRjExact.__init__(self, pattern, fRjExact)
   
    def compute(self, ch):
        #return self.__classical_compute__(ch)
        rj = super(fRjInsert, self).compute(ch) 
        rj.OR(self.related_rj)
        self.related_rj(ch)
        return rj
  
    def __classical_compute__(self, ch): 
        b = self.getBit(-1)     
        for i in range(len(self.pattern)): 
            sb = self.getBit(i)
            if self.related_rj.getBit(i) : self.setBit(i, 1)
            elif b and ch == pattern[i]: self.setBit(i, 1)
            else: self.setBit(i, 0) 
            b = sb  
   
        self.related_rj(ch)
        return self

    def operationsDone(self, op): 
        if op == fDistance.INSERTION and (not self.related_rj.lastBit()):
            return 1 
        return 0
  

class fRjDelete(fRjExact):
    def __init__(self, pattern = None):
        fRjExact.__init__(self, pattern, fRjExact)
    
    def compute(self, ch):
        #return self.__classical_compute__(ch)

        self.related_rj(ch)
        rb = self.related_rj.lastBit()
        self.related_rj.rightshift()
        
        rj = super(fRjDelete, self).compute(ch) 
        rj.OR(self.related_rj)
        
        self.related_rj.leftshift()
        self.related_rj.setBit(self.size - 1, rb)
    
        return rj
        
    def __classical_compute__(self, ch): 
        self.related_rj(ch)
        
        b = self.getBit(-1)
        for i in range(len(self.pattern)): 
            sb = self.getBit(i)
            if self.related_rj.getBit(i-1) : self.setBit(i, 1)
            elif b and ch == self.pattern[i]: self.setBit(i, 1)
            else: self.setBit(i, 0)
            b = sb   
        return self

    def operationsDone(self, op): 
        if op == fDistance.DELETION and (not self.related_rj.lastBit()):
            return 1 
        return 0


class fRjSubstitute(fRjInsert): 
    def __classical_compute__(self, ch): 
        b = self.getBit(-1)
        for i in range(len(self.pattern)): 
            sb = self.getBit(i)
            if self.related_rj.getBit(i-1) : self.setBit(i, 1)
            elif self.getBit(i-1) and ch == self.pattern[i]: self.setBit(i, 1)
            else: self.setBit(i, 0)   
            b = sb
            
        self.related_rj(ch)
        return self

    def operationsDone(self, op): return 0 


class fRjKError(fRjBase):
    def __init__(self, pattern = None, errors = 1):
        assert errors > 0
        self._errors = errors

        if errors > 1:
            rrj = fRjKError(pattern, errors - 1)
        else:
            rrj = fRjExact(pattern)
            
        fRjBase.__init__(self, pattern, rrj)
       
    def compute(self, ch):         
        # pre-compute R(j+1)(d)
        self.rightshift()
        self.AND(self.alphabet().S(ch))
        self.OR(self.related_rj)
       
        # final calculation by creation intermidiate cloned R(j)(d-1)  
        cb = self.related_rj.clone()
        cb.OR(self.related_rj.compute(ch)) 
        cb.rightshift()
        self.OR(cb)
      
        return self 
        
    def kRj(self, k):
        assert k >= 0 and k <= self.errors
        rj = self
        for i in range(self.errors - k): rj = rj.related_rj
        return rj
        
    @property
    def errors(self): return self._errors     
        
    def operationsDone(self, op):
        return 0
  
  
if __name__ == '__main__':
	pass
