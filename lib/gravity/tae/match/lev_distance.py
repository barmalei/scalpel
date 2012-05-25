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

from gravity.tae.distance import fDistance, fDistancePath, BaseDistanceMatrix

class fBaseLevDistance(fDistance):
    def __init__(self): 
        self._allowedOperations = set([fDistance.INSERTION, fDistance.DELETION, fDistance.SUBSTITUTION])
  
    def allowedOperations(self):
        self._allowedOperations
      
    #!!!
    # for future handling of empty string:
    #   1. empty text means the pattern is built by len(pattern) insertion operations
    #   2. empty pattern means the pattern is built by len(text) deletion operations
    #!!!
    def  _empty_generator(self, text, pattern):
        rows, cols = len(text), len(pattern)
        if rows == 0:
            for col in range(cols): yield (-1, col, col + 1)
        elif cols == 0:
            for row in range(rows): yield (row, -1, row + 1)
        
        
class fClassicalLevDistance(fBaseLevDistance):        
    def _distance(self, text, pattern):
        m = self._classical_compute_edit_distance(text, pattern)
        return m[len(text)][len(pattern)]

    def generator(self, text, pattern):
        m = self._classical_compute_edit_distance(text, pattern)
        for col in range(1, len(pattern) + 1): 
            for row in range(1, len(text) + 1):
                yield (row - 1, col - 1, m[row][col]) 
 
    def _classical_compute_edit_distance(self, text1, text2):
        rows = len(text1) + 1  # initial string 
        cols = len(text2) + 1  # string to be tested
        d    = [[0 for col in range(cols)] for row in range(rows)]
        for i in range(1, cols): d[0][i] = i
        for i in range(1, rows): d[i][0] = i
        
        for j in range(1, cols):
            for i in range(1, rows):
                if text1[i-1] == text2[j-1]: 
                    d[i][j] = d[i-1][j-1] 
                else:  
                    d[i][j] = min(d[i-1][j], #deletion
                                  d[i][j-1], #insertion
                                  d[i-1][j-1] ) + 1 #substitution
        return d


class fLevDistance(fBaseLevDistance):
    def generator(self, text, pattern):
        cols, rows = len(pattern), len(text)
            
        lcol = [i for i in range(rows + 1)]
        rcol = [0 for i in range(rows + 1)]
        
        for j in range(cols):
            pch, rcol[0] = pattern[j], j + 1
            for i in range(rows):
                lcol_i =  lcol[i]
                
                if text[i] == pch: 
                    rcol[i+1] = lcol_i
                    yield (i, j, lcol_i)
                else:   
                    rcol[i+1] = min(rcol[i],            #deletion
                                    lcol[i + 1],        #insertion
                                    lcol_i      ) + 1   #substitution
                    yield(i, j, rcol[i+1])  
            a, lcol = lcol, rcol
            rcol = a
            

class fLevDistance2(fBaseLevDistance):
    def generator(self, text, pattern):
        cols, rows = len(pattern), len(text)
        data = [i + 1 for i in xrange(rows)]
        
        for col in range(cols):
            pch, diag, top = pattern[col], col, col + 1 
            for row in range(rows):
                dr = data[row]
                if text[row] == pch: 
                    yield (row, col, diag)
                    top, diag = diag, dr           
                    data[row] = top 
                else:   
                    top = min(top,        #deletion
                              dr,         #insertion
                              diag) + 1   #substitution
                    yield (row, col, top)
                    diag = dr
                    data[row] = top
        
        
class fLevPath(fDistancePath):    
    def __init__(self, del_priority = 0, ins_priority=0, sub_priority = 0):
        self.ins_priority = ins_priority
        self.del_priority = del_priority
        self.sub_priority = sub_priority
    
    def path(self, matrix):        
        i, j = matrix.rows-1, matrix.cols-1
        dr = dc = pr = 0
     
        yield (i, j)
        while j != 0 or i != 0:
            min, left, top, diag = matrix.get(i,j), matrix.get(i,j-1), matrix.get(i-1,j), matrix.get(i-1,j-1)

            if left < min: 
                dr, dc, min, pr =  0, -1, left, self.ins_priority    
           
            if top < min or (top == min and pr < self.del_priority): 
                dr, dc, min, pr = -1,  0, top, self.del_priority 
                
            if diag < min or (diag == min and pr <= self.sub_priority): 
                dr = dc = -1
                
            if i > 0: i += dr
            if j > 0: j += dc

            yield (i, j)    


class fBaseLevDistanceDiag(fBaseLevDistance):
    MAX_VALUE = 1000000000
 
    def __init__(self, delta = 2):
        assert delta >= 0 
        fDistance.__init__(self)
        self._delta = delta

    def __call__(self, text, pattern, def_value=MAX_VALUE):
        return self._distance(unicode(text), unicode(pattern), def_value)

    def _distance(self, text, pattern, def_value = MAX_VALUE):
        data  = self._calc(text, pattern, def_value)
        delta = self._normalized_delta(len(text))
        return data[(delta * 2 + 2) * (len(pattern) - 1) + delta  + 1]

    def fill_matrix(self, text, pattern, m):
        m._size(len(text), len(pattern))
        for e in self.generator(text, pattern, m.def_value): m.put(e[0], e[1], e[2])
        return m

    def _calc(self, text, pattern, def_value):
        raise NotImplementedError()
        
    def _normalized_delta(self, rows):
        return rows - 1 if (rows - self._delta - 1) < 0 else self._delta
        
    def _colsize(self, rows, cols):
        return self._normalized_delta(rows) * 2 + 1


class fLevDistanceDiag(fBaseLevDistanceDiag):
    def matrix(self, text, pattern, def_value = fBaseLevDistanceDiag.MAX_VALUE):
        rows, cols = len(text), len(pattern)
        data = self._calc(text, pattern, def_value)
    
        class DiagDistanceMatrix(BaseDistanceMatrix):
            def __init__(self, rows, cols, colsize, data, def_value):
                BaseDistanceMatrix.__init__(self, def_value)
                self.data    = data
                self.colsize = colsize
                self.rows    = rows
                self.cols    = cols
                
            def get(self, row, col):
                if row == -1:
                    return 0 if col == -1 else col + 1 
                elif col == -1: 
                    return row + 1
                
                data, dval, maxr = self.data, self.def_value, self.colsize
                index = col * (maxr + 1)
        
                # if there is no column has been allocated yet or
                # no data is defined for the found row
                start_row = data[index]
                return dval if row < start_row or row >= start_row + maxr else data[index + row - start_row + 1]
                
            def put(self, row, col):
                raise NotImplementedError()
            
        
        return DiagDistanceMatrix(rows, cols, self._colsize(rows, cols), data, def_value) 
            
    def generator(self, text, pattern, def_value = fBaseLevDistanceDiag.MAX_VALUE):
        rows, cols, data = len(text), len(pattern), self._calc(text, pattern, def_value)
        colsize = self._colsize(rows, cols) 
        cc = colsize + 1     
                
        for col in range(cols):
            # calculate starting index of the col 
            index = col * cc
            srow  = data[index]
            
            # switch to first data element
            index += 1
                        
            for row in range(colsize):
                d = data[index + row] 
                if d == def_value : break 
                yield (row + srow, col, d)
     
    def _calc(self, text, pattern, def_value = fBaseLevDistanceDiag.MAX_VALUE):
        """ Low level diagonal distance calculation function to minimize speed up computation """
        rows, cols = len(text), len(pattern)
        
        delta = self._normalized_delta(rows)
        
        # initialize  column data 
        colsize = self._colsize(rows, cols)
        
        #
        #  Column 
        #
        lcol, rcol = [ def_value ]*(colsize + 3), [ def_value ]*(colsize + 3)  
    
        # init left column data
        #
        # Two columns are allocated to calculate result:  
        #
        # left col<-+   +-> right col (to be calculated basing on left col content)
        #           |   |
        # --------+---+---+---+---+---- 
        # row/col |-1   0   2   3   ...  
        # --------+---+---+---+---+----
        #    -1   | 0 | ? |   |   |
        #     0   | 1 | ? |   |   |
        #     1   | 2 | ? |   |   |
        #     2   | 3 | ? |   |   |
        #     3   | . | ? |   |   |
        #           
        #  left column has to be intilized with values starting from 0..n
        #  where:
        #    n = 1(anchor element) + <diaganal size> + 1(col=-1 element) 
        #           
        for i in range(delta + 3): lcol[i] = i
  
        # initialize array to keep result data
        # this is the plain array where every calculated row diagonal 
        # elements are placed in fixed sized slot - (colsize + 1). The first (extra)
        # element in the slot is used to keep first row index the data have been
        # calculated. array is pre-filled with default value to make difference between
        # elements that have been calculated and untouchable elements.  
        cc = colsize + 1
        data = [def_value] * (cols * cc)
  
        l_row1, l_row2 = 0, delta + 1 
        maxrow = rows - 1

        for col in range(cols):
            # calculate anchor row index
            arow = (col * rows) // cols
            
            # upper row
            r_row1 = arow - delta if arow > delta else 0
            
            # lower row
            r_row2 = arow + delta if arow + delta < rows else maxrow 

            lcol[0] = col     if l_row1 == 0 else lcol[1]   
            rcol[0] = col + 1 if r_row1 == 0 else def_value
            
            # to speed up access to array element store it in temporary var
            col_ch = pattern[col]
            
            # slightly speed up loop below
            drr, dlr = 1 - r_row1, 1 - l_row1    

            # calculate starting index for the given column 
            index = col * cc
            
            # store starting row to be calculated as the first element 
            data[index] = r_row1
            index += 1
            
            for row in range(r_row1, r_row2 + 1, 1): 
                i, j = row + drr, row + dlr    
                
                if text[row] == col_ch: 
                    data[index] = rcol[i] = lcol[j - 1]
                else:  
                    # the construction below is equivalent of min (a,b,c) just to win another thousand milliseconds
                    a,b,c = lcol[j], rcol[i - 1], lcol[j - 1]
                    if a < b:
                        if c < a: a = c 
                    else:
                        a = b if b < c else c
  
                    rcol[i] = data[index] = a + 1
            
                index += 1 
            
            # replace left row reference with just calculated right row
            a, lcol = lcol, rcol
            rcol = a
            l_row1, l_row2 = r_row1, r_row2
        
        # return result array
        return data


if __name__ == '__main__':
	pass


