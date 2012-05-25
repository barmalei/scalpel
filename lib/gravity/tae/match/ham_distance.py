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


class fHammingDistance(fDistance):
    def __init__(self): 
        self._allowed_operations = set([fDistance.SUBSTITUTION]) 
  
    def allowedOperations(self):
        return self._allowed_operations
  
    def _distance(self, text, pattern):
        
        for i in self.generator(text, pattern): pass
        return i[2]
        
    def generator(self, text, pattern):
        assert len(text) == len(pattern)

        if len(text) == 0: yield (0, 0, 0)
        else:
            d = 0
            for rowcol in range(len(text)): 
                d += (text[rowcol] != pattern[rowcol])
                yield (rowcol, rowcol, d) 

if __name__ == '__main__':
	pass
