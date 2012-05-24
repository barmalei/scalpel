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

from ilps.tae.text import fMatch 
import array
                         
class fDistance(object):
    """ Distance function interface. Distance function is a function that 
    calculates minimal number of operations to be performed to transform
    the given pattern into the given text. 
    
    Usage:
    
      # distance calculation
      d = fLevDistance()("text1", "text2")           
      
    """
    
    INSERTION     =  1
    DELETION      = -1    
    SUBSTITUTION  =  0
              
    ## !!!! not decided whether the method should exist           
    def allowedOperations(self):
        raise NotImplementedError()

    def __call__(self, text, pattern):
        assert text != None and pattern != None
        return self._distance(unicode(text), unicode(pattern))

    def _distance(self, text, pattern):
        """ Method returns minimal distance the specified "pattern" can be transformed 
        into the given "text".
        """
        for e in self.generator(text, pattern): pass
        return e[2]

    def fill_matrix(self, text, pattern, m):
        m._size(len(text), len(pattern))
        for e in self.generator(text, pattern): m.put(e[0], e[1], e[2])
        return m
    
    def generator(self, text, pattern): 
        """ Distance function should be implemented as a generator if it is supposed
        to keep results in a distance matrix. Generator should generates 
        all calculated distance values as number of (row, column, value) tuples 
        """
        raise NotImplementedError()
        
        
class BaseDistanceMatrix(object):        
    """ Basic abstract class to implement matrix storage to keep calculated
    distance function results. The matrix requires:
     -- "distfunc" that has to provide generator method implemented
     -- "text" and "pattern"
     
    Usage:
     
        m = XXXDistanceMatrix()
        d = LevenshteinDistance()
        d.fill_matrix("text1", "text2", m)
  
     To show results:
     
        print m
  
    """

    def __init__(self, def_value=0):
        self.def_value = def_value
        self.rows = self.cols = 0

    def cells(self):
        for row in xrange(self.rows):
            for col in xrange(self.cols): yield (row, col, self.get(row, col))

    def get(self, row, col):
        if row == -1:
            return 0 if col == -1 else col + 1
        elif col == -1: return row + 1
        return self._get(row, col)

    def put(self, row, col, num):
        if self.get(row, col) != num: self._put(row, col, num)
  
    def _get(self, row, col):
        raise NotImplementedError()

    def _put(self, row, col, num):
        raise NotImplementedError()
        
    def __str__(self, text = None, pattern = None, path = []):
        return self.toString(text, pattern, path)
    
    def _size(self, rows, cols):
        assert rows >= 0 and cols >= 0
        if rows != self.rows and cols != self.cols:
            self.rows, self.cols = rows, cols
            self._resize_buffer()
    
    def _resize_buffer(self):
        pass    
    
    def toString(self, text = None, pattern = None, path=[]):
        if (text    != None and len(text)    != self.rows) or \
           (pattern != None and len(pattern) != self.cols):
            raise BaseException("Incorrect text or pattern")

        res = '   |'
        if pattern:
            for ch in pattern: 
                # test if there is \n character and replace it with \\n
                if ch == "\n": 
                    res += ("\\n  ")
                else:
                    res += ("%2s  " % ch)
        
        res += ("\n" + '-'* (len(res) + 3) + "\n")
   
        for row in xrange(self.rows):
            
            if text : 
                if text[row] == "\n": res += "%2s |" % "\\n" 
                else:   res += "%2s |" % text[row]
            
            for col in xrange(self.cols):
                if  (row, col) in path : res += "*%02d " % self.get(row, col)
                else                   : res += "%03d "  % self.get(row, col)                   
            res += '\n' 
        return res

    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __eq__(self, other):
        if other                                 and \
           isinstance(other, BaseDistanceMatrix) and \
           self.rows == other.rows               and \
           self.cols == other.cols:

            for col in range(self.cols):
                for row in range(self.rows):
                    if self.get(row, col) != other.get(row, col): 
                        return False
            return True
        return False
    
    
class fDistanceMatch(fMatch):    
    """ This is implementation of match function which uses distance function
    to match two strings. 
    """
   
    def __init__(self, distfunc, threshold = 0.34):
        assert distfunc and threshold > 0 and threshold <= 1 
        if isinstance(distfunc, type): distfunc = distfunc() 
        self._distfunc = distfunc 
        self._threshold = threshold

    @property
    def threshold(self): return self._threshold

    def _match(self, text, pattern):
        d = self._distfunc(text, pattern)
        return (d / (len(pattern) + 0.0) < self._threshold)


class fDistancePath(object):
    """ Abstract class to be extended with various implementations of
     distance path calculation (for instance minimal path).
 
    Usage:
    
        path = fMinPath()(distance_matrix)
 
    """
    
    def __call__(self, matrix):
        assert matrix
        return [p for p in self.path(matrix)]
  
    def path(self, matrix): 
        """ This method has to return array of (row, column) tuples that defines
        a path the concrete implementation calculates
        """
        raise NotImplementedError()
        
        

class fMinPath(fDistancePath):        
    """ Straightforward implementation of minimal distance path calculation. 
    """
    def path(self, matrix):
        d = matrix
        # special case when one of the string is empty  
        if d.rows == 0 or d.cols == 0:
            if d.rows == 0: 
                for col in range(d.cols): yield (0, col)
            else:
                for row in range(d.rows): yield (row, 0)
        else:    
            i, j = d.rows-1, d.cols-1
            dr = dc = 0
         
            yield (i, j)
            while j != 0 or i != 0:
                min, left, top, diag = d.get(i,j), d.get(i,j-1), d.get(i-1,j), d.get(i-1,j-1)

                if left  < min: dr, dc, min =  0, -1, left    
                if top   < min: dr, dc, min = -1,  0, top 
                if diag <= min: dr = dc = -1
                
                if i > 0: i += dr
                if j > 0: j += dc
                
                yield (i, j)    
    
    
def ls_operations(path, src_text, dest_text):
    i, max = 0, len(path)-1 
    while i < max:
        e1, e2   = path[i], path[i + 1]
        row, col = e1[0], e1[1]
        dr, dc   = e2[0] - row, e2[1] - col
    
        if dr < 0: 
            if dc < 0:
                yield (row, col, fDistance.SUBSTITUTION)
            else: 
                yield (row, col, fDistance.DELETION)
        else:
            yield (row, col, fDistance.INSERTION)
        i += 1

   
    rows, cols = len(src_text), len(dest_text)
    if rows == 0:
        pass  
    elif cols == 0:
        pass
    else:
        # since path always ends at (0, 0) last operation can be substitution 
        if src_text[0] != dest_text[0]:
            yield (0, 0, fDistance.SUBSTITUTION)
    
        
def operations_to_text(path, src_text, dest_text):
    for o in ls_operations(path, src_text, dest_text):
        src_index, dest_index, op = o[0], o[1], o[2]
    
        # !!!
        #  It should be very slow code below. 
        #  It has to be optimized. 
        # !!!
        if op == fDistance.SUBSTITUTION:
            if dest_text[dest_index] != src_text[src_index]:
                src_text = "".join([src_text[0:src_index], dest_text[dest_index], src_text[src_index+1:]])
        elif op == fDistance.INSERTION :
            src_text = "".join([src_text[0:src_index + 1], dest_text[dest_index], src_text[src_index+1:]])
        else:
            src_text = "".join([src_text[0:src_index], src_text[src_index + 1:]])
    
    return src_text
            
    
if __name__ == '__main__':
	pass

