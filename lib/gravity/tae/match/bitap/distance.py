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

from gravity.tae.distance import fDistance

class fBitapDistance(fDistance):
    def __init__(self, fRj):
        assert fRj
        self._fRj = fRj()  if isinstance(fRj, type) else fRj
    
    def _distance(self, text, pattern):       
        # calculate Rj function
        # !!! Probably it can be optimized regarding number of calculations 
        # !!! we need. It seems maximal number of iterations can be calculated 
        # !!! len(pattern) + allowed_errors
        self._fRj.set_pattern(pattern)
        for row in range(len(text)): self._fRj.compute(text[row])
        
        # means there more transformation than allowed by Rj function
        if self._fRj.lastBit() == 0: return -1
                
        rj = self._fRj.related_rj
        c  = self._fRj.count_related_rj()
        while rj and rj.lastBit(): 
            c -= 1
            rj = rj.related_rj
        return c
    
    def generator(self, text, pattern): 
        self._fRj.set_pattern(pattern)
        for row in range(len(text)):
            self._fRj.compute(text[row])
            for col in range(len(pattern)):
                yield (row, col, self._fRj.getBit(col))

    def fRj(self): return self._fRj 
    
    
class BitapDistanceMatrixSet(object):
    class BitapMatrix(object):
        def __init__(self, rows, cols):
            assert rows > 0 and cols > 0
            self._rows = rows
            self._cols = cols  
            self._data = [ [ 0 for col in range(cols) ] for row in range(rows) ]
          
        def __call__(self, row, col):
            return self.get(row, col)
            
        def get(row, col):
            return self._data[row][col]  
            
        @property    
        def cols(self): return self._cols
        
        @property
        def rows(self): return self._rows
    
        def _putRow(self, row, fRj):
            for i in range(fRj.size):
                self._data[row][i] = fRj.getBit(i)
        
        def __str_row__(self, row):
            return " ".join([str(e) for e in self._data[row]])
       
        def __str__(self):
            s = ""
            for row in range(self.rows):
                s +=  self.__str_row__(row)+ "\n"
            return s
                
                
    def __init__(self, fRj, text, pattern):        
        assert fRj and text and pattern
        self._text = text
        self._pattern = pattern
        
        if isinstance(fRj, type) : fRj = fRj()
        fRj.set_pattern(pattern)
        self._fRj = fRj
        
        rows = len(text)
        cols = len(pattern)
        self._matrix = [  BitapDistanceMatrixSet.BitapMatrix(rows, cols) for e in range(fRj.count_related_rj() + 1)]

        for row in range(rows):
            fRj(text[row])
            rj = fRj
            for i in range(self.size()-1, -1, -1):
                self._matrix[i]._putRow(row, rj)
                rj = rj.related_rj            
        
    def size(self): 
        return len(self._matrix)
      
    def matrix(self, index): 
        return self._matrix[index]
    
    def __str__(self):
        m = len(self._pattern)
        n = self.size()
        s = "   "
        for col in range(n):
            s += " ".join(self._pattern) + "   "
       
        s+= "\n   "
        for col in range(n): 
            s +=  ("-" * 2 * m) + "  " 
        s+= "\n"      
                 
        for row in range(len(self._text)):
            s += self._text[row] +  "| "
            for col in range(n):
                s += self.matrix(col).__str_row__(row) + "   "
            s += "\n"  
        return s
        
  
if __name__ == '__main__':
	main()
