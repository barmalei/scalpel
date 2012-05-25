import unittest

import os, sys

from gravity.common.file.filewalker import FileWalker, TouchFileWalker, ReadFileWalker, XMLFileWalker, DOMFileWalker

class TestFileWalkerModule(unittest.TestCase):
    def test_filewalker(self):        
        #  folder is required
        def t(): FileWalker(__file__)
        self.assertRaises(IOError, t)        

        #  not implemented
        def t(): (FileWalker(self._path('fw')))()
        self.assertRaises(NotImplementedError, t)        

    def test_touchfilewalker(self):  
        # correct stat
        tf = TouchFileWalker(self._path("fw"))
        tf()
        self.assertEqual(tf.number_of_files, 5)
        self.assertEqual(tf.amount_of_data, 0)
        
        # test correctness callback result
        r = []
        def t(p): r.append(p);
        tf(t)
        self.assertEqual(len(r), 5)
        for i in r: 
            self.assertTrue(os.path.exists(i) and (not os.path.isdir(i)))
            
        r = []
        def t(p): r.append(p);
        tf(t, FileWalker.FileMask("*.*"))
        self.assertEqual(len(r), 5)
        for i in r: 
            self.assertTrue(os.path.exists(i) and (not os.path.isdir(i)))
        self.assertEqual(tf.number_of_files, 5)

        r = []
        def t(p): r.append(p);
        tf(t, FileWalker.FileMask("*.py"))
        self.assertEqual(len(r), 0)
        self.assertEqual(tf.number_of_files, 0)

        r = []
        def t(p): r.append(p);
        tf(t, FileWalker.FileMask("**/sub1/*.*"))
        self.assertEqual(len(r), 3)
        self.assertEqual(tf.number_of_files, 3)

    def test_readfilewalker(self):  
        # correct stat
        tf = ReadFileWalker(self._path("fw"))
        r = []
        def t(p): r.append(p);
        tf()
        self.assertEqual(tf.number_of_files, 5)
        self.assertTrue(tf.amount_of_data > 0)
        for i in r: 
            self.assertTrue(os.path.exists(i) and (not os.path.isdir(i)))

    def _path(self, p):
        return os.path.join(os.path.dirname(__file__), p)

    
if __name__ == '__main__':
    unittest.main()
