#!/usr/bin/env pbython
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


#
#  Left to right bits sequence representation:
#
#  bit number |0|1|2|3| ... |N|
#  ----------------------------
#  bit value  |0|0|1|0| ... |0|
#
#  This bits representation is more natural than internal machine view
#  where bits are ordered from right to left  

class BitsStorage(object):
    def __init__(self, size):
        assert size > 0    
        self._set_size(size)        
  
    def setBits(self, rng, v):
        for i in rng: self.setBit(i, v)

    def toList(self): return [ self.getBit(i) for i in range(-1, self.size) ]    
     
    def setBit(self, i, v): self.__setBit__(i, v)

    def getBit(self, i): return self.__getBit__(i)

    def lastBit(self): return self.getBit(self.size - 1)

    def leftshift(self): raise NotImplementedError()
                        
    def rightshift(self): raise NotImplementedError()
        
    def AND(self, bs):  raise NotImplementedError()
      
    def OR(self, bs): raise NotImplementedError()
        
    def __bits__(self): raise NotImplementedError()

    def __allocate__(self, size, value = 0): raise NotImplementedError()

    def __setBit__(self, i, v): raise NotImplementedError()
    
    def __getBit__(self, i): raise NotImplementedError()

    def __str__(self): return " ".join([str(i) for i in self.toList()])

    def _set_size(self, s): 
        assert s > 0
        self._size = s
        self.__allocate__(s)
        
    def _get_size(self): 
        return self._size
        
    size = property(_get_size, _set_size)


class ListBitsStorage(BitsStorage):

    # integer bits representation !
    def __bits__(self):
        r = 0
        for i in range(self.size):
            if self._bs[i] :  r |= (1 << i)
        return r
        
    def leftshift(self): self.__shift__(range(0, self.size))
            
    def rightshift(self): self.__shift__(range(self.size-1, -1, -1), self.getBit(-1))
        
    def AND(self, bs):
        for i in range(self.size):
            self._bs[i] = int(self._bs[i] and bs.getBit(i))
    
    def OR(self, bs):
        for i in range(self.size):
            self._bs[i] = int(self._bs[i] or bs.getBit(i))
    
    def __allocate__(self, size, value = 0): 
        if len(self._bs) != size:
            self._bs = [ 0 for i in range(size) ] 
            if value == 0: return
      
        for i in range(len(self._bs)-1, -1, -1): 
            if value & (1 << i):  self._bs[i] = 0
            else: self._bs[i] = 1
              
    def __setBit__(self, i, v): self._bs[i] = v
    
    def __getBit__(self, i):
        if i < 0: return 1       
        return self._bs[i]

    def __shift__(self, rng, a=0):    
        for i in rng:
            b = self._bs[i]
            self._bs[i] = a
            a = b


class BitsWiseStorage(BitsStorage):
    #!!!
    # Implementation is a little bit dirty since it always instantiates 
    # BitsWiseStorage class 
    # !!!
    def clone(self):
        c = BitsWiseStorage(self.size)
        c.__allocate__(self.size, self.__bits__())
        return c 

    def __bits__(self): return self._bs

    def leftshift(self): self._bs = self._bs >> 1
            
    def rightshift(self): 
        b = self.getBit(-1)
        self._bs = self._bs << 1
        if b: self.setBit(0, 1)
        
    def AND(self, bs): self._bs = bs.__bits__() & self._bs
      
    def OR(self, bs): self._bs = bs.__bits__() | self._bs
  
    def __allocate__(self, size, value=0): self._bs = value
 
    def __setBit__(self, i, v):
        if v:  self._bs = self._bs |  (1 << i)
        else:  self._bs = self._bs & ~(1 << i)
            
    def __getBit__(self, i): 
        if i < 0 or self._bs & (1 << i) : return 1 
        return 0
 
    
if __name__ == '__main__':
    pass
