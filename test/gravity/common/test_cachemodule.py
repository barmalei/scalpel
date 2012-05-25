import unittest

from gravity.common.cache import Cache

class TestCacheModule(unittest.TestCase):
 
    data = [ 0,1,2,3,4,5 ]
 
    @Cache(keyarguments=[None, 'index'], maxSize=3)
    def cached_method(self, index):
        return self.data[index]
    
    def test_cache(self):        
        # fill cache
        self.assertEqual(self.cached_method(0), 0)
        self.assertEqual(self.cached_method(1), 1)
        self.assertEqual(self.cached_method(2), 2)

        # change cached method output and check whether
        # cache still stores old values  
        self.data = [9,9,9,9,9,9]
        self.assertEqual(self.cached_method(0), 0)
        self.assertEqual(self.cached_method(1), 1)
        self.assertEqual(self.cached_method(2), 2)

        self.assertNotEqual(self.cached_method(3), 3)


if __name__ == '__main__':
    unittest.main()
