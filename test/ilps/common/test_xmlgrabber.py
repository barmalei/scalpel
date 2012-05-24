
import os, codecs, StringIO

from   ilps.common.xml.grabber import XmlGrabber 
from   ilps.common.xml.grabber import TrueXmlElementFilter
from   ilps.common.xml.grabber import XmlPathFilter 
from   ilps.common.xml.grabber import XmlElement 
from   ilps.common.xml.grabber import XmlElementsCollector 
from   ilps.common.xml.grabber import XmlElementFilter 
 
import unittest


xml_file  = os.path.join(os.path.dirname(__file__), "test.xml")
assert os.path.exists(xml_file)
counter = 0

class TestGrabber(unittest.TestCase):

    def test_xml_element(self):
        e = XmlElement('a/b/c', { 'a':'test' }, 'text')
        self.assertEqual(e.path, 'a/b/c')
        self.assertEqual(e.text, 'text')
        self.assertEqual(e.attr, { 'a':'test' })
        self.assertEqual(e.name, 'c')
        self.assertEqual(e.kids(), [])

    def test_xml_elements_collector(self):
        def f1(): 
            g = XmlGrabber()
            b = XmlElementsCollector('root')
            g.addXmlElementFilter(TrueXmlElementFilter())
            g.grab(xml_file, b)
            
        self.assertRaises( NotImplementedError, f1)

        class MyXmlElementsCollector(XmlElementsCollector):
            def grabbed(self, path, element, filter):
                self.root_element().add_kid(element)

        g = XmlGrabber()
        b = MyXmlElementsCollector('root')
        g.addXmlElementFilter(TrueXmlElementFilter())
        g.grab(xml_file, b)
        
        self.assertEqual(len(str(b.root_element())), 10026)


    def test_xml_filter(self):
        def f():
            e = XmlElementFilter()
            e.accept(None)
            
        self.assertRaises(NotImplementedError, f)
        
        
        e = TrueXmlElementFilter()
        self.assertEqual(e.accept(None),True)

        f = XmlPathFilter(['f/a'])
        self.assertEqual(f.accept(XmlElement('f/a')), True)
        self.assertEqual(f.accept(XmlElement('a')), False)
        self.assertEqual(f.accept(XmlElement('a/f')), False)
        self.assertEqual(f.accept(XmlElement('f')), False)

        f = XmlPathFilter('f/a')
        self.assertEqual(f.accept(XmlElement('f/a')), True)
        self.assertEqual(f.accept(XmlElement('a')), False)
        self.assertEqual(f.accept(XmlElement('a/f')), False)
        self.assertEqual(f.accept(XmlElement('f')), False)


        f = XmlPathFilter('.*a')
        self.assertEqual(f.accept(XmlElement('f/a')), True)
        self.assertEqual(f.accept(XmlElement('a')), True)
        self.assertEqual(f.accept(XmlElement('b')), False)
        self.assertEqual(f.accept(XmlElement('f/a/a')), True)
        self.assertEqual(f.accept(XmlElement('f/aaa')), True)

        f = XmlPathFilter(r'(.*/)?a')
        self.assertEqual(f.accept(XmlElement('f/a')), True)
        self.assertEqual(f.accept(XmlElement('a')), True)
        self.assertEqual(f.accept(XmlElement('b')), False)
        self.assertEqual(f.accept(XmlElement('f/a/a')), True)
        self.assertEqual(f.accept(XmlElement('f/aaa')), True)


    def test_xmlgrabber(self):
        global counter 
        
        def listener1(xml_path, element, filter):
            global counter
            counter += 1
        
        counter = 0
        grabber = XmlGrabber()
        grabber.addXmlElementFilter(XmlPathFilter([ ".*/selectiepositiedragerannotatie"  ]))
        grabber.grab(xml_file, listener1)
        self.assertEqual(0, counter)
        
        counter = 0
        grabber = XmlGrabber(False)
        grabber.addXmlElementFilter(XmlPathFilter(".*/selectiepositiedragerannotatie" ))
        grabber.grab(xml_file, listener1)
        self.assertEqual(1, counter)



if __name__ == '__main__':
    unittest.main()
