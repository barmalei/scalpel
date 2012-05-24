import unittest

from ilps.tae.match.lev_distance import fLevDistance, fLevDistance2, fClassicalLevDistance, fLevDistanceDiag, fLevPath
from ilps.tae.match.distance_matrix import DistanceMatrix, UprightDistanceMatrix, HybridSubsetDistanceMatrix, UprightSubsetDistanceMatrix
from ilps.tae.distance import fMinPath, operations_to_text

from ilps.tae.match import c_lev_distance 


TEXTS = [ ("a", "b"), ("a", "a"), ("abc", "a"), ("a", "abc"), ("abc", "abc"), ("abcdef", "fghdts"),  ("dsd sdf4 fs", "ddsdsd dsdsd"), ("a bsd c sdsd klb", "a    bsd   c sdsd      klb"), (u"abc \u03A0 gk \u03A3 lmn \u03A9", u"abcdef \u03A0 gk \u03A3  \u03A9") ]

class TestLevdistance(unittest.TestCase):

    # test Levenshtein distance (including diagonal) calculation for 
    # two identical strings
    def test_lev1(self): 
        s1 = s2 = "abcdef gk lmn"
        self.assertEqual(fLevDistance()(s1, s2) , 0)        
        self.assertEqual(fLevDistance2()(s1, s2) , 0)        
        self.assertEqual(fClassicalLevDistance()(s1, s2) , 0)        
        self.assertEqual(fLevDistanceDiag()(s1, s2) , 0)        
       
        # C code testing  
        self.assertEqual(c_lev_distance.fLevDistance()(s1, s2) , 0)        
        self.assertEqual(c_lev_distance.fLevDistanceDiag()(s1, s2) , 0)        
        
        # unicode strings (contains Greek characters)
        s1 = s2 = u"abcdef \u03A0 gk \u03A3 lmn \u03A9"
        self.assertEqual(c_lev_distance.fLevDistance()(s1, s2) , 0)        
        self.assertEqual(c_lev_distance.fLevDistanceDiag()(s1, s2) , 0)        

    # test Levenshtein distance (including diagonal) calculation for 
    # set of string
    def test_lev2(self): 
        for t in TEXTS:
            s1, s2 = t[0], t[1]

            d = fClassicalLevDistance()(s1, s2)
            self.assertEqual(fLevDistance()(s1, s2) , d)        
            self.assertEqual(fLevDistance2()(s1, s2) , d)       
            
            # C-code             
            self.assertEqual(c_lev_distance.fLevDistance()(s1, s2) , d)        
            self.assertEqual(c_lev_distance.fLevDistanceDiag(len(s1))(s1, s2) , d)        
           
            # diagonal levenshtein
            self.assertEqual(fLevDistanceDiag(len(s1))(s1, s2) , d)        
            
            # test diag bounds handling
            self.assertEqual(fLevDistanceDiag(10*len(s1))(s1, s2) , d)        
            self.assertEqual(c_lev_distance.fLevDistanceDiag(10*len(s1))(s1, s2) , d)        
           

    def test_lev3(self): 
        for t in TEXTS:
            s1, s2 = t[0], t[1]

            d = fClassicalLevDistance()(s1, s2)
        
            m1 = DistanceMatrix()
            fClassicalLevDistance().fill_matrix(s1, s2, m1)
         
            m2 = DistanceMatrix()
            fLevDistance().fill_matrix(s1, s2, m2)
         
            m3 = DistanceMatrix()
            fLevDistance2().fill_matrix(s1, s2, m3)
         
            m4 = DistanceMatrix(111)
            fLevDistanceDiag(len(s1) - 1).fill_matrix(s1, s2, m4)
         
            m5 = fLevDistanceDiag(len(s1) - 1).matrix(s1, s2)
            
            # C-code
            m6 = c_lev_distance.fLevDistance().matrix(s1, s2)       
           
            m6_1 = DistanceMatrix()
            c_lev_distance.fLevDistance().fill_matrix(s1, s2, m6_1)
            m7 = c_lev_distance.fLevDistanceDiag(len(s1) - 1).matrix(s1, s2)
            
            m7_1 = DistanceMatrix(def_value = 111)
            c_lev_distance.fLevDistanceDiag(len(s1) - 1).fill_matrix(s1, s2, m7_1)

            
            self.assertEqual(m1, m2)        
            self.assertEqual(m2, m3)        
            self.assertEqual(m3, m4)        
            self.assertEqual(m4, m5)        
            self.assertEqual(m5, m6)        
            self.assertEqual(m6, m7)        
            self.assertEqual(m6, m6_1)        
            self.assertEqual(m7, m7_1)        


            # test C and Python diagonal 
            m8 = c_lev_distance.fLevDistanceDiag(2).matrix(s1, s2)
            m9 = fLevDistanceDiag(2).matrix(s1, s2)
            self.assertEqual(m6, m7) 

    def test_lev4(self): 
        for t in TEXTS:
            s1, s2 = t[0], t[1]
       
            m1 = DistanceMatrix()
            fClassicalLevDistance().fill_matrix(s1, s2, m1)
         
            m2 = UprightDistanceMatrix()
            fClassicalLevDistance().fill_matrix(s1, s2, m2)
           
            m3 = HybridSubsetDistanceMatrix()
            fClassicalLevDistance().fill_matrix(s1, s2, m3)
            
            m4 = UprightSubsetDistanceMatrix(len(s1))
            fClassicalLevDistance().fill_matrix(s1, s2, m4)
         
            self.assertEqual(m1, m2)        
            self.assertEqual(m2, m3)        
            self.assertEqual(m3, m4)        

    def test_lev5(self): 
        for t in TEXTS:
            s1, s2 = t[0], t[1]
       
            m1 = DistanceMatrix()
            fClassicalLevDistance().fill_matrix(s1, s2, m1)
            p1 = fMinPath()(m1)
            self.assertEqual(p1, fLevPath()(m1))        
            self.assertEqual(s2, operations_to_text(p1, s1, s2))

         
            m2 = UprightDistanceMatrix()
            fClassicalLevDistance().fill_matrix(s1, s2, m2)
            p2 = fMinPath()(m2)
            self.assertEqual(p2, fLevPath()(m2))        
            self.assertEqual(s2, operations_to_text(p2, s1, s2))

            m3 = HybridSubsetDistanceMatrix()
            fClassicalLevDistance().fill_matrix(s1, s2, m3)
            p3 = fMinPath()(m3)
            self.assertEqual(p3, fLevPath()(m3))        
            self.assertEqual(s2, operations_to_text(p3, s1, s2))

            m4 = UprightSubsetDistanceMatrix(len(s1))
            fClassicalLevDistance().fill_matrix(s1, s2, m4)
            p4 = fMinPath()(m4)
            self.assertEqual(p4, fLevPath()(m4))        
            self.assertEqual(s2, operations_to_text(p4, s1, s2))

            self.assertEqual(p1, p2)        
            self.assertEqual(p2, p3)        
            self.assertEqual(p3, p4)        
            
            # C implementation 
            # m5 = fLevDistanceDiag(len(s1) - 1).matrix(s1, s2)
            # p5 = c_lev_distance.fLevPath()(m5)
            # self.assertEqual(p4, p5)        


    def test_lev6(self): 
        for t in TEXTS:
            s1, s2 = t[0], t[1]
       
            m1 = DistanceMatrix(def_value = 111)
            fLevDistanceDiag(3).fill_matrix(s1, s2, m1)
         
            m2 = UprightDistanceMatrix(def_value = 111)
            fLevDistanceDiag(3).fill_matrix(s1, s2, m2)
            
            m3 = HybridSubsetDistanceMatrix(def_value = 111)
            fLevDistanceDiag(3).fill_matrix(s1, s2, m3)
        
            m4 = UprightSubsetDistanceMatrix(7, def_value = 111)
            fLevDistanceDiag(3).fill_matrix(s1, s2, m4)

            m5 = fLevDistanceDiag(3).matrix(s1, s2, def_value = 111)

            m6 = c_lev_distance.fLevDistanceDiag(3).matrix(s1, s2, def_value = 111)

            self.assertEqual(m1, m2)        
            self.assertEqual(m2, m3)        
            self.assertEqual(m3, m4)        
            self.assertEqual(m4, m5)        
            self.assertEqual(m5, m6)        
                        
                        
if __name__ == '__main__':
    unittest.main()

    
    
