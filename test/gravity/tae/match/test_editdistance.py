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


from gravity.tae.distance  import fDistanceMatch, fMinPath
from gravity.tae.match.distance_matrix import DistanceMatrix
from gravity.tae.match.lev_distance import fClassicalLevDistance, fLevDistance

import unittest


class TestEditdistance(unittest.TestCase):
    
    def test_ldistance(self):     
        ed = fClassicalLevDistance()
        self.assertEqual(ed("Text", "Text"), 0)

        ed = fClassicalLevDistance()
        self.assertEqual(ed("Texmt", "sdText"), 3)

        ed = fLevDistance()
        self.assertEqual(ed("Text", "Text"), 0)
        
        ed = fLevDistance()
        self.assertEqual(ed("Texmt", "sdText"), 3)

        em = [ [1,	2,	2,	3,	4,	5 ],    
               [2,	2,	3,	2,	3,	4 ],
               [3,	3,	3,	3,	2,	3 ],
               [4,	4,	4,	4,	3,	3 ],
               [5,	5,	5,	5,	4,	3 ] ]
               
        m = DistanceMatrix()
        fClassicalLevDistance().fill_matrix("Texmt", "sdText", m)
        for row in range(len(em)):
            for col in range(len(em[row])):
                self.assertEqual(em[row][col], m.get(row,col))

        m = fLevDistance().fill_matrix("Texmt", "sdText", DistanceMatrix())
        for row in range(len(em)):
            for col in range(len(em[row])):
                self.assertEqual(em[row][col], m.get(row,col))

        mp = [(4, 5), (3, 4), (2, 4), (1, 3), (0, 2), (0, 1), (0, 0)]
        i = 0
        for e in fMinPath()(m):
            self.assertEqual(e, mp[i])
            i+=1

        f = fDistanceMatch(fLevDistance) 
        self.assertEqual(f("Text 1", "Text 2"), True)

        f = fDistanceMatch(fLevDistance) 
        self.assertEqual(f("Text 1", "Tessxt 2"), False)
        
    
if __name__ == '__main__':
	unittest.main()
    
