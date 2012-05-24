


from ilps.common.process import PipedProcess, JavaClassRunner
from ilps import ILPS_LIB_HOME


import unittest, os


class TestProcess(unittest.TestCase):
    def test_process(self):
        def f1(): PipedProcess(None)
        def f2(): PipedProcess('java')(None)
    
        self.assertRaises(AssertionError, f1)
        self.assertRaises(AssertionError, f2)
        
        class Callback(object):
            def __init__(self, data = None): self.data = data
            def read(self, pipe): return pipe.read()
            def send(self, pipe): 
                if self.data != None: pipe.write(self.data)

        cls_file    = os.path.join(os.path.dirname(__file__), "echo_process.class")
        src_file    = os.path.join(os.path.dirname(__file__), "echo_process.java")
        destination = os.path.join(os.path.dirname(ILPS_LIB_HOME), 'test')
    
        if os.path.exists(cls_file): os.remove(cls_file)
        r = PipedProcess('javac')(Callback(), [ "-d %s" % destination, src_file ] )
        self.assertEqual(os.path.exists(cls_file), True)

        jr = JavaClassRunner('ilps.common.echo_process')
        jr.classpath = [ destination ]
        
        d = "Hello World"
        r = jr(Callback(d))
        self.assertEqual(d, r)
        
    
if __name__ == '__main__':
    unittest.main()


