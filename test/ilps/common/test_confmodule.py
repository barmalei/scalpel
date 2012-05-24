import unittest

import os, sys

from ilps.common.configuration import Configuration
import ConfigParser

class TestConfigurationModule(unittest.TestCase):
    def test_config(self):        
        c = Configuration()
        c.read(self._config_path())

        # option doesn't exits
        self.assertTrue(not c.has_option("section", "optionxxx"))        

        # option exits
        self.assertTrue(c.has_option("section", "option"))        
        
        # section doesn't exits
        self.assertTrue(not c.has_section("sectionxxx"))        

        # section exits
        self.assertTrue(c.has_section("section"))        
        
        # option doesn't exits
        def t(): c.get("section", "optionxxx")
        self.assertRaises(ConfigParser.NoOptionError, t)        

        # section doesn't exits
        def t(): c.get("sectionxxx", "option")
        self.assertRaises(ConfigParser.NoSectionError, t)        

        # fetch value
        self.assertEqual(c.get("section", "option"), "value")        


    def test_config_inheritance(self):        
        c = Configuration()
        c.read(self._config_path())

        # inherited option
        self.assertTrue(c.has_option("section", "base_option"))        

        # inherited option value
        self.assertEqual(c.get("section", "base_option"), "base_option_value")        

        # overrided option value
        self.assertEqual(c.get("section", "base_option3"), "override")        

        # test if inherited options are in list
        l = c.options("base_section")
        self.assertTrue("base_option" in l)        
        self.assertTrue("base_option2" in l)        
        self.assertEqual(len(l), 3)       

        # test if inherited options are in list
        l = c.options("section")
        self.assertTrue("base_option" in l)        
        self.assertTrue("base_option2" in l)        
        self.assertEqual(len(l), 4)       

        # test items method
        i = c.items("section")
        self.assertTrue(("base_option","base_option_value") in i)        
        self.assertTrue(("base_option2","base_option_value2") in i)       
        self.assertTrue(("option","value") in i)       
        self.assertTrue(("base_option3", "override") in i)       
        self.assertEqual(len(i), 4)       
        
    def test_config_refernces(self):        
        c = Configuration()
        c.read(self._config_path())

        # inherited option
        v1 = c.get("refsection", "option")
        v2 = c.get("base_section", "base_option")
        self.assertEqual(v1, v2)        


    def _config_path(self):
        return os.path.join(os.path.dirname(__file__), "test_config.conf")

    
if __name__ == '__main__':
    unittest.main()
