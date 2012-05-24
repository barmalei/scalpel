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


from ilps.tae.distance import fDistance
from ilps.tae.match.distance_matrix import DistanceMatrix
from ilps.tae.match.ham_distance import fHammingDistance

import unittest

class TestHamming(unittest.TestCase):
    def test_hamming(self):
        def f1(): fHammingDistance()("Pattern 1", "Pattern")
        def f2(): fHammingDistance()("Pattern", "Pattern 2")
        def f3(): fHammingDistance()(None, "Pattern 2")
        def f4(): fHammingDistance()(None, None)
        def f5(): fHammingDistance()("pattern", None)

        self.assertRaises(AssertionError, f1)
        self.assertRaises(AssertionError, f2)
        self.assertRaises(AssertionError, f3)
        self.assertRaises(AssertionError, f4)
        self.assertRaises(AssertionError, f5)
        
        self.assertEqual(fHammingDistance()("Pattern 1", "Pattern 2"), 1)
        self.assertEqual(fHammingDistance()("Pattern", "Pattern"), 0)
        self.assertEqual(fHammingDistance()("", ""), 0)

        em =  [ [  1, 0, 0, 0, 0, 0, 0 ],
                [  0, 1, 0, 0, 0, 0, 0 ],
                [  0, 0, 2, 0, 0, 0, 0 ],
                [  0, 0, 0, 3, 0, 0, 0 ],
                [  0, 0, 0, 0, 4, 0, 0 ],
                [  0, 0, 0, 0, 0, 4, 0 ],
                [  0, 0, 0, 0, 0, 0, 4 ] ]

        m = fHammingDistance().fill_matrix("abcdefg", "cbdrtfg", DistanceMatrix())
        for row in range(len(em)):
            for col in range(len(em[row])):
                self.assertEqual(em[row][col], m.get(row, col))
  
  
if __name__ == '__main__':
	unittest.main()
	
