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

import glob, os, sys, time, xml.parsers.expat, xml.dom.minidom, fnmatch


class FileWalker(object):
    class FileMask(object):
        def __init__(self, mask): self.mask = mask
            
        def __call__(self, path):
            if self.mask: return fnmatch.fnmatch(path, self.mask)
            return True
            
    """ 
    This class is abstraction to walk through the all files are located  
    in the specified directory and its sub directories. Call walk method
    whenever you want to go through the folder content. Implementation 
    of the walker class have to override 'handle_file' method that is 
    called every time a new file has been found. 
    """
    def __init__(self, root):
        """ 
        Class initialiser 'root' argument is a path to folder to be walked.
        """

        if not os.path.isdir(root): raise IOError(root)            
        self.root = os.path.abspath(root)
        self.start_time = self.end_time = None   
        self.number_of_files = self.amount_of_data = 0
        self.max_files_to_walk = -1

    def __call__(self, callback = None, mask = None):
        return self.walk(callback, mask)

    def walk(self, callback = None, mask = None):
        """ 
        Starts walking through the directory and its sub directories 
        content 
        """
        try:
            self.mask = mask
            self.callback = callback
            self.number_of_files = amount_of_data = 0
            self.start_time = time.gmtime()
            os.path.walk(self.root, self.__walk__, '')    
            self.end_time = time.gmtime()  
        finally:
            self.mask = None
            self.callback = None
                        
    def handle_file(self, path):
        """ 
        Abstract method that is executed every time a new file has 
        been found. Override it to be notified a new file was found. 
        """
        raise NotImplementedError()                                

    def stat(self):
        """ 
        This method provides statistic regarding amount of data 
        have been passed, elapsed time, etc. 
        """
        st1 = time.strftime("%d %b %Y %H:%M:%S", self.start_time)
        st2 = time.strftime("%d %b %Y %H:%M:%S", self.end_time)        
        return "\nElapsed time: %s - %s\nHandled files: %d\nBytes: %d" % (st1, st2, self.number_of_files, self.amount_of_data)        
     
    def __str__(self): return self.stat()
        
    def __walk__(self, arg, dirname, names):
        """ Private method """
        for file in names:
            path_to_file = os.path.join(dirname, file)
            if os.path.isfile(path_to_file) and (not self.mask or self.mask(path_to_file)):
                self.amount_of_data  = self.amount_of_data + self.handle_file(path_to_file)
                self.number_of_files = self.number_of_files + 1  
                if self.callback: self.callback(path_to_file)


class TouchFileWalker(FileWalker):
    """ 
    This is the simplest FileWalker implementation 
    that does nothing except tries to open handled files in 
    read mode. 
    """
    
    def handle_file(self, file_path):
        """ 
        Overrides abstract method of parent class to be informed
        a new file has been found. This implementation opens found files in
        read mode. Addidtinally it passes opened files path and handler as 
        input arguments of 'handle_stream' method.
        """
        f = None
        res = 0
        try:
            f   = open(file_path, 'r')    
            res = self.handle_stream(file_path, f)
        finally:       
            if f != None: f.close()

        return res

    def handle_stream(self, file_path, file_stream):
        """ 
        This method is supposed to be used by classes that want to
        do something with the given file content. For example, read file 
        content.The basic implementation does nothing. 
        """
        return 0
        
        
class ReadFileWalker(TouchFileWalker):
    """ 
    This walker implementation tries to read content of every found
    in the given folder file. 
    """
    
    def handle_stream(self, file_path, file_stream):
        """ 
        This method overrides parent class method to read content of 
        the file. 
        """
        data = file_stream.read()
        self.handle_content(file_path, data)
        return len(data)

    def handle_content(self, file_path, data):
        """ 
        This method is executed every time a content of a file has been
        successfully read. Override it if special action has to be done with 
        file content. 
        """
        pass
        
        
class XMLFileWalker(ReadFileWalker):
    """ 
    This is walker implementation that applyes XML SAX parser to every 
    found file 
    """
    
    failed_files = {}
    
    class XMLListener(object):
        """ Basic SAX listener defintion."""
        
        def start_document(self, document_path):
            """ Invoked before the given file parsing """
            pass
     
        def end_document(self, document_path):
            """ 
            Invoked after the given document parsing has been
            completed.
            """
            pass
     
        def start_element(self, name, attrs):
            pass
        
        def end_element(self, name):
            pass
        
        def char_data(self, data):
            pass
     
    
    class PrintXMLListener(XMLListener):
        """ 
        Simple SAX listener implemetation. Does nothing except printing 
        all events have happened during parsing.
        """

        def start_document(self, document_path):
            print "Parse document: ", document_path

        def end_document(self, document_path):
            print "End parse document: ", document_path
        
        def start_element(self, name, attrs):
            print 'Element:', name, attrs
                    
        def end_element(self, name):
            print 'End element:', name
        
        def char_data(self, data):
            print 'Character data:', repr(data)
             
    
  
    def  __init__(self, root, xmllistener=None):
        """ 
        Construct XML walker with the given listener. Listener is 
        optional. Empty implementation listener is used by default. 
        """
        
        ReadFileWalker.__init__(self, root)
        
        if xmllistener == None:
            xmllistener = XMLFileWalker.XMLListener()
        
        if isinstance(xmllistener, self.XMLListener) == False:
            raise ValueError()
       
        self.xmllistener = xmllistener
        
    def handle_content(self, file_path, file_content):
        """ Overrides method to handle a file content with XML parser. """
        self.xmllistener.start_document(file_path)
        xmlparser = self.__create_parser__()      
        try:
            xmlparser.Parse(file_content, True)     
            self.xmllistener.end_document(file_path)
        except Exception, ex:
            print 'Error: XML parsing error occurred in ', file_path
            self.failed_files[file_path] = ex
        
    def  stat(self):
        res = super(XMLFileWalker, self).stat()
        return res + "\nFailed XMLs: " + str(len(self.failed_files))  
        
    def __create_parser__(self):
        """ Creates configured XML parser. """
        xmlparser = xml.parsers.expat.ParserCreate()
        xmlparser.StartElementHandler  = self.xmllistener.start_element
        xmlparser.EndElementHandler    = self.xmllistener.end_element
        xmlparser.CharacterDataHandler = self.xmllistener.char_data
        return xmlparser 



class DOMFileWalker(ReadFileWalker):
    """ 
    This is walker implementation that applyes XML DOM parser to every 
    found file 
    """

    def __init__(self, root):
        ReadFileWalker.__init__(self, self.root)
        self.failed_files = {}
    
    
    def handle_content(self, file_path, file_content):
        """ Overrides method to handle a file content with XML parser. """
        try:
            dom = xml.dom.minidom.parseString(file_content)     
        except Exception, ex:
            print 'Error: DOM XML parsing error occurred in ', file_path
            self.failed_files[file_path] = ex
            
    def  stat(self):
        res = super(ReadFileWalker, self).stat()
        return res + "\nFailed XMLs: " + str(len(self.failed_files))  
        

def __validate_xml (path):
    """ Function doc """
    file = open(path)
    xml.parsers.expat.ParserCreate().Parse(file.read())   
    file.close()


class LevelStatFileWalker(FileWalker):
    def __init__(self, root):
        FileWalker.__init__(self, root)
        self.root_level = len(self.root.split('/'))
        self.levels = {}
   
    def handle_file(self, path):
        l = len(os.path.dirname(path).split('/'))
        if l in self.levels : self.levels[l] = self.levels[l] + 1 
        else:                 self.levels[l] = 1
        return 0
                            
    def stat(self):
        res = super(self.__class__, self).stat()
        
        print res
        for key in self.levels:
            res = res + "\n level = %d, files = %d" % (key - self.root_level, self.levels[key])
        return res


def main():   
   
   
    WALKER_TYPES = { 'touch':TouchFileWalker, 'read':ReadFileWalker, 
                     'readxml_sax':XMLFileWalker, 'readxml_dom':DOMFileWalker, 
                     'level_stat':LevelStatFileWalker } 
 
    USAGE_INFO   = "\
Usage: python " + __file__ + "\
 <folder to walk> <walker type>\n\
where <walker type> can be:\n\
  touch - just to touch files.\n\
  read  - read files content.\n\
  readxml_sax - parse files as XMLs using SAX parser.\n\
  readxml_dom - parse files as XMLs using DOM parser."
      
    if len(sys.argv) != 3:
        print USAGE_INFO
        return 1
        
    root = sys.argv[1]
    type = sys.argv[2]
    
    if not type in WALKER_TYPES:
        print 'Walker type is invalid.\n', USAGE_INFO
        return 1
    
    walker = WALKER_TYPES[type](root)
    
    print "\n>>> Walk through '", root, "' folder."
    print ">>> Apply ", type, " walker to the folder content."
    walker.walk()
    
    print 50*'>'
    print walker.stat()
    print "\n", 50*'<' 
    print 'Done'
   
    return 0


if __name__ == '__main__':
	#main()
	def filter(name):
	    import re
	    c = re.compile(r".*\.py$")
	    return c.match(name) != None
	    
	t = TouchFileWalker("../../.")
	t.walk(filter)
	print t
