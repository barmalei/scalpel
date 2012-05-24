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


from ilps.tae.match.distance_matrix import DistanceMatrix
from ilps.tae.match.bitap.rj_set import fRjExact, fRjSubstitute, fRjInsert, fRjDelete, fRjKError
from ilps.tae.match.bitap.rj import fRj
from ilps.tae.match.bitap.distance import fBitapDistance, BitapDistanceMatrixSet
from ilps.tae.match.bitap.search import fBitapSearch

import unittest


class TestBitap(unittest.TestCase):
    def test_alphabet(self):
        def f1(): fRj.Alphabet()
        def f2(): fRj.Alphabet('')
        def f3(): fRj.Alphabet(None)
        self.assertRaises(TypeError, f1)
        self.assertRaises(AssertionError, f2)
        self.assertRaises(AssertionError, f3)
        
        v = 'abc'
        a = fRj.Alphabet(v)
        c = a.characters()
        self.assertEqual(len(c), 3)
        for i in range(len(v)): self.assertEqual(v[i] in c, True)
        
        self.assertEqual(a.S('z'), a._zeroRj)
        
    def test_rj(self):
        rj = fRjExact("pattern")
        

    def test_search(self):
                        #01234567890123456789
        text, pattern = "Test acd abcd", "abc"

        f = fBitapSearch(fRjInsert) 
        r = f(text, pattern)
        
        f = fBitapSearch(fRjDelete) 
        r = f(text, pattern)

        f = fBitapSearch(fRjSubstitute()) 
        r = f(text, pattern)

        f = fBitapSearch(fRjKError(errors = 2)) 
        r = f(text, pattern)


    def test_distance(self):
        text, pattern = "Test acd abcd", "abc"
        
        f = fBitapDistance(fRjInsert)
        m = f.fill_matrix(text, pattern, DistanceMatrix())  
        print "Distance matrix:\n", m.toString(text, pattern)

        f = fBitapDistance(fRjInsert)
        print "Distance:", f("texts", "tddext")
       
        b = BitapDistanceMatrixSet(fRjInsert, "test string", "test pattern")
        print "Distance matrixes set:\n", b 
    

if __name__ == '__main__':
    unittest.main()
