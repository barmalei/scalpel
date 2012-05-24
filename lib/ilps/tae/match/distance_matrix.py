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

"""

Module represents set of matrix storage implementations to keep distance
functions results. For maximal efficiency it is supposed the distance function
is calculated column by column.

"""

from ilps.tae.distance import BaseDistanceMatrix
import array                                                        
    
    
class DistanceMatrix(BaseDistanceMatrix):
    """ Lazy initialized storage to keep calculation results 
    
    Internal structure of the matrix is based on nested list usage where
    every nested list keeps data for the given row. 
    """
    
    def __init__(self, def_value=0):
        BaseDistanceMatrix.__init__(self, def_value)
        self._data = [[]]

    def _get(self, row, col):
        return self.def_value  if len(self._data) <= row or len(self._data[row]) <= col  else self._data[row][col] 
     
    def _put(self, row, col, num):
        data = self._data

        r = len(data) 
        if r <= row: 
            # lazy matrix creation implementation
            while r <= row: 
                data.append([])  
                r += 1
                
        c = len(data[row])
        if c <= col:
            datarow = data[row] 
            while c <= col: 
                datarow.append(self.def_value)  
                c += 1
        
        data[row][col] = num
        
    def _resize_buffer(self):
        self._data = [[]]


class UprightDistanceMatrix(BaseDistanceMatrix):
    """ Matrix storage implementation using one dimensional array.  
        where (row, col) pair is transformed into array index using 
        simple formula: row * cols + col
    """

    def __init__(self, def_value=0, use_array = True):
        BaseDistanceMatrix.__init__(self, def_value)
        self.use_array = use_array

    def _get(self, row, col):
        return self._data[row * self.cols + col]
     
    def _put(self, row, col, num):
        self._data[row * self.cols + col] = num

    def _resize_buffer(self):
        size = self.rows * self.cols
        if self.use_array:
            self._data = array.array('i', [self.def_value] * size)
        else:
            self._data = [self.def_value] * size
        
    @classmethod
    def create(cls, list, rows, cols, def_value = 0):
        assert len(list) == (rows * cols)
        class _UprightDistanceMatrix(UprightDistanceMatrix):
            def __init__(self, list, rows, cols, def_value=0):
                assert list and len(list) > 0 and len(list) == (rows * cols) 
                BaseDistanceMatrix.__init__(self, def_value)
                self.cols  = cols
                self.rows  = rows
                self._data = list
      
            def _size(self, rows, cols):
                pass
 
            def _resize_buffer(self):
                assert len(self._data) == (self.rows * self.cols)
            
        return _UprightDistanceMatrix(list, rows, cols, def_value)
      
        
class HybridSubsetDistanceMatrix(BaseDistanceMatrix):
    """ This one of the most efficient (performance/memory usage) way 
    to store only subset of matrix data. It is supposed to be used 
    whenever an algorithm needs calculating only subset of row elements 
    for every columns. 
     
    Internally it organized as standard Python list which keeps low level 
    arrays where every array is used to keep row elements. The first 
    element of the nested row array defines first row index:
    [
       [2, 0, 1]   # column 0, row[2] is 0 and row[3] is 1
       [1, 2, 3]   # column 1, row[1] is 2 and row[2] is 3
       ...
    ]  
    
    """
    
    def __init__(self, def_value = 0):
        BaseDistanceMatrix.__init__(self, def_value)
        self._data = []

    def get(self, row, col):        
        # standard distance matrix behavior
        if row == -1:
            return 0 if col == -1 else col + 1
        elif col == -1: return row + 1

        data= self._data

        # if there is no column has been allocated yet or
        # no data is defined for the found row
        if col >= len(data)    or \
           data[col][0] < 0    or \
           data[col][0] + len(data[col]) - 1 <= row or \
           row < data[col][0]: 
            return self.def_value
            
        rowdata = data[col]
        return rowdata[row - rowdata[0] + 1]    

    def put(self, row, col, num):
        if self.get(row, col) != num: 
            data = self._data
                    
            c = len(data)
            # column has not been allocated yet
            while c <= col: 
                data.append(array.array("i", [-1]))  
                c += 1
            
            rowdata = data[col]
            row_start, row_len = rowdata[0], len(rowdata) - 1
        
            # column has not been used yet
            if row_start < 0:
                row_start = rowdata[0] = row
                
            # row is out of right bound
            if row >= row_start + row_len:
                c = row - row_start - row_len
                while c >= 0: 
                    rowdata.append(self.def_value)
                    c -= 1
           
            # unexpected situation. calculation has to be performed from 
            # upper row to lower row 
            elif row < row_start: raise BaseException("Wrong calculation order")

            rowdata[row - row_start + 1] = num

    def _resize_buffer(self):
        self._data = []


class UprightSubsetDistanceMatrix(BaseDistanceMatrix):
    """ Matrix storage implementation to keep partial calculated results 
        using one dimensional array where (row, col) pair is transformed 
        into array index using simple formula: row * max_rows + col. The
        partial result cannot be calculated for more than specified fixed 
        maximal size (max_rows). 
    """
    
    def __init__(self, max_rows, def_value = 1000000000):
        assert max_rows > 0
        BaseDistanceMatrix.__init__(self, def_value)
        self.max_rows = max_rows
        
    #
    #  To speed up calculation this method overrides 
    #
    def get(self, row, col):
        if row == -1:
            return 0 if col == -1 else col + 1
        elif col == -1: return row + 1
 
        data, dval, maxr = self._data, self.def_value, self.max_rows 
        index = col * (maxr + 1)
        
        # if there is no column has been allocated yet or
        # no data is defined for the found row
        start_row = data[index]
        return dval if row < start_row or row >= start_row + maxr else data[index + row - start_row + 1]
                  
    def put(self, row, col, num):
        if self.get(row, col) != num: 
            data, index  = self._data, col * (self.max_rows + 1)
            start_row = data[index]
            if start_row == self.def_value:
                data[index] = start_row = row
            elif row < start_row: 
                raise BaseException("Invalid calculation order: ", start_row, row, col)
                            
            data[index + 1 + row - start_row] = num
      
    def _resize_buffer(self):
    #    assert self.max_rows <= self.rows
        self._data = [self.def_value] * (self.cols * (self.max_rows + 1))

    
if __name__ == '__main__':
	pass
