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

import lev_distance 
import ilps.tae.distance
import ilps.tae.match.clev
import ilps.tae.text


class fLevDistance(lev_distance.fBaseLevDistance):
    def _distance(self, text, pattern):
        return ilps.tae.match.clev.fLevDistance(text, pattern)
        
    def generator(self, text, pattern):
        text, pattern = unicode(text), unicode(pattern)
        data = ilps.tae.match.clev.fLevDistanceMatrix(text, pattern)
        rows, cols, index = len(text), len(pattern), 0
        for col in range(cols):
            for row in range(rows):
                yield (row, col, data[index])
                index += 1

    def fill_matrix(self, text, pattern, m):
        return super(self.__class__, self).fill_matrix(unicode(text), unicode(pattern), m)

    def matrix(self, text, pattern):
        class _UprightDistanceMatrix(ilps.tae.distance.BaseDistanceMatrix):
            def __init__(self, data, rows, cols):
                assert data and len(data) > 0 and len(data) == rows*cols
                ilps.tae.distance.BaseDistanceMatrix.__init__(self)
                self.rows = rows
                self.cols = cols
                self._data = data

            def get(self, row, col):
                return self._data[col * self.rows + row]
             
            def put(self, row, col, num):
                self._data[col * self.rows + row] = num

            def _size(self, rows, cols):
                pass

            def _resize_buffer(self):
                pass

        text, pattern = unicode(text), unicode(pattern)
        return _UprightDistanceMatrix(ilps.tae.match.clev.fLevDistanceMatrix(text, pattern), len(text), len(pattern))


class fLevDistanceDiag(lev_distance.fLevDistanceDiag):        
    def matrix(self, text, pattern, def_value = lev_distance.fBaseLevDistanceDiag.MAX_VALUE):
        return super(self.__class__, self).matrix(unicode(text), unicode(pattern), def_value)        

    def generator(self, text, pattern, def_value = lev_distance.fBaseLevDistanceDiag.MAX_VALUE):
        return super(self.__class__, self).generator(unicode(text), unicode(pattern), def_value)        
    
    def _distance(self, text, pattern, def_value = lev_distance.fBaseLevDistanceDiag.MAX_VALUE):
        return super(self.__class__, self)._distance(text, pattern, def_value)        
    
    def fill_matrix(self, text, pattern, m):
        return super(self.__class__, self).fill_matrix(unicode(text), unicode(pattern), m)       
        
    def _calc(self, text, pattern, def_value = lev_distance.fBaseLevDistanceDiag.MAX_VALUE):
        d = ilps.tae.match.clev.fLevDistanceDiag(text, pattern, self._normalized_delta(len(text)), def_value)
        return d 
        

class fLevPath(lev_distance.fDistancePath):
    def path(self, matrix):
        if not hasattr(matrix, 'colsize'):
            raise BaseException("Only 'lev_distance.fDiagLevDistance.matrix()' can be passed.")
        
        res = ilps.tae.match.clev.fLevPath(matrix.data, matrix.rows, matrix.cols, (matrix.colsize - 1)/2)
        for r in res: yield r


class fLevTextsAligner(ilps.tae.text.fTextsAligner):
    def __init__(self, delta = 10):
        self.delta = delta

    def _align(self, original_text, processed_text, offsets):
        if self.delta < 0:
            self.delta = abs(len(processed_text) - len(original_text))%100 + 1
            if self.delta < 10: self.delta = 10 
            
        return ilps.tae.match.clev.fLevTextAlignment(processed_text, original_text, self.delta, offsets)        


class fLevTokensAligner(ilps.tae.text.fTokensAligner):
    class TokenOffsets(object):
        def __init__(self, tokens):
            assert tokens
            self.tokens = tokens
        
        def __len__(self): 
            return len(self.tokens) * 2
    
        def __getitem__(self, key):
            t = self.tokens[key / 2]
            f = key % 2
            if f > 0: return t[f] + t[f + 1] - 1
            return t[f + 1]
        
        def __setitem__(self, key, value):
            f = key % 2
            t = self.tokens[key / 2]
            
            if f > 0: t[f + 1] = value - t[f] + 1
            else:     t[f + 1] = value
            
        def __iter__(self):
            class Iterator(object):
                def __init__(self, toff):
                    self.toff  = toff
                    self.count = len(toff)
                    self.index = 0
            
                def __iter__(self): return self
                
                def next(self): 
                    if self.index >= self.count: raise StopIteration()
                    r = self.toff[self.index]
                    self.index += 1
                    return r

            return Iterator(self)
 
    def __init__(self, delta = 10):
        self.delta = delta

    def _align(self, original_text, processed_text, tokens):
        offsets = fLevTokensAligner.TokenOffsets(tokens)
        res     = fLevTextsAligner(self.delta)(original_text, processed_text, offsets)
        for i in range(len(res)): offsets[i] = res[i]


if __name__ == '__main__':
	pass



