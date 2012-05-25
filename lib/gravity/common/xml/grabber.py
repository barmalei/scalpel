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

from __future__ import with_statement

import os, re, xml.parsers.expat, StringIO


class XmlElementFilter(object):
    def accept(self, element): raise NotImplementedError()
    
class TrueXmlElementFilter(XmlElementFilter):
    def accept(self, element):
        return True
    
class XmlPathFilter(XmlElementFilter):
    def __init__(self, expr):
        assert expr
        self._expr_is_array = isinstance(expr, list)
        self._expr = [re.compile(e) for e in expr] if self._expr_is_array else re.compile(expr)
        
    def accept(self, element):
        if self._expr_is_array:
            for expr in self._expr: 
                if expr.match(element.path): return True
            return False
        return True if self._expr.match(element.path) else False
    

class XmlElement(object):
    """ Class doc """
    def __init__ (self, path, attr = None, text = None):
        assert path and len(path.strip()) > 0
        self._path = path
        self._attr = attr
        self._text = text
        self._name = path.split('/')[-1]
       
    @property   
    def path(self): return self._path
       
    @property
    def name(self): return self._name
       
    @property   
    def attr(self): return self._attr
       
    def to_xml(self, buf, shift=''):
        buf.write("\n%s<%s%s>\n" % (shift, self.name, self.attr2str())) 
        
        kids = self.kids()
        if len(kids) == 0: 
            buf.write(shift)
            buf.write(' ')
            buf.write(self.text2str())
        else:
            nshift = shift + ' '
            for kid in kids: kid.to_xml(buf, nshift)
           
        buf.write("\n%s</%s>" % (shift, self.name))
        
    def __str__(self): 
        buf = None
        try:
            buf = StringIO.StringIO()
            self.to_xml(buf)
            return buf.getvalue()
        finally:
            if buf != None: buf.close()

    def _set_text(self, text): self._text = text
    def _get_text(self): return self._text

    def attr2str(self):
        if self.attr:
            res = []
            for a in self.attr: 
                res.append(' ')
                res.append(a)
                res.append("=\'%s\'" % self.attr[a])
            return ''.join(res)
        return ''

    def text2str(self):
        return '' if self.text == None else ''.join(['<![CDATA[', self.text, ']]>'])
    
    def kids(self): return []
    
    text = property(_get_text, _set_text)


class XmlElementsCollector(object):
    class CXmlElement(XmlElement):
        def __init__(self, path, attr):
            XmlElement.__init__(self, path, attr, None)
            self._kids = []
            
        def kids(self): return self._kids
        
        def add_kid(self, kid): 
            assert kid
            self._kids.append(kid)
    
    
    def __init__(self, root_name):
        assert root_name
        self._root_element = XmlElementsCollector.CXmlElement(root_name, {})

    def __call__(self, fpath, element, filter):
        return self.grabbed(fpath, element, filter)

    def grabbed(self, fpath, element, filter):
        raise NotImplementedError()

    def root_element(self): return self._root_element
        
        

class XmlGrabber(object):

    @staticmethod
    def createXMLParser (obj):
        xmlparser = xml.parsers.expat.ParserCreate()
        xmlparser.StartElementHandler  = obj._startElement
        xmlparser.EndElementHandler    = obj._endElement
        xmlparser.CharacterDataHandler = obj._charData
        return xmlparser 
   
    def __init__ (self, ignore_empty = True):
        self._ignore_empty, self._filters = ignore_empty, []
    
    def addXmlElementFilter(self, filter):
        assert filter
        self._filters.append(filter) 

    def __call__(self, fpath, listener=None):
        return self.grab(fpath, listener)

    def grab(self, fpath, listener=None):
        assert os.path.exists(fpath) and os.path.isfile(fpath)
        parser = XmlGrabber.createXMLParser(self)
        self._listener  = listener
        self._fpath     = fpath
        self._paths     = []
        self._leaf_flag = False
        self._kept_attr = None
        try:     parser.Parse(open(fpath, 'r').read(), True)
        finally: self._listener = None

    def accept(self, element):
        for filter in self._filters:
            if filter.accept(element): return filter
        return None
        
    def _startElement(self, name, attr):
        self._paths.append(name)
        self._leaf_flag = True
        self._kept_attr = attr
        self._kept_text = []       
              
    def _endElement(self, name):
        try:
            if self._leaf_flag:
                content = '\n'.join(self._kept_text)
                if self._ignore_empty and len(content.strip(' \n\r\t')) == 0: return
                
                element = XmlElement('/'.join(self._paths), self._kept_attr, content) 
                filter  = self.accept(element)
                self.grabbed(self._fpath, element, filter)
                if filter and self._listener: 
                    self._listener(self._fpath, element, filter)
        finally:  
            self._leaf_flag = False
            self._paths.pop()      
            
    def _charData(self, data):
        if len(data.strip()) > 0: self._kept_text.append(data) 

    def grabbed(self, fpath, element, filter):
        pass


