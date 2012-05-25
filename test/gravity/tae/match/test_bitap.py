#!/usr/bin/env python

from gravity.tae.match.distance_matrix import DistanceMatrix
from gravity.tae.match.bitap.rj_set import fRjExact, fRjSubstitute, fRjInsert, fRjDelete, fRjKError
from gravity.tae.match.bitap.rj import fRj
from gravity.tae.match.bitap.distance import fBitapDistance, BitapDistanceMatrixSet
from gravity.tae.match.bitap.search import fBitapSearch

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
