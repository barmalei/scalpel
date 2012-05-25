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


#
#  Text is an object thatcan be easilyn transformed into string by 
#  str, unicode classes: 
#     - str/unicode string
#     - FileText
#     - XMLText
#
#  Collection is number of texts organazed somehow
# 
#  AnnotatedText/StructuredText is a text that can provide some infomation
#  about its structure (rokens) 
#
#  Corpus annotated text that can be built by parsing special formatted 
#  data 
#

from __future__ import with_statement
import codecs, re, StringIO, os, gzip, glob
from gravity import GRAVITY_LIB_HOME

from gravity.tae.tokenizer import Token
from gravity.common.xml.grabber import XmlPathFilter, XmlGrabber
from gravity.common.file.filewalker import FileWalker


class Text(object):
    def __init__(self, data, lang = 'en', encoding="latin-1"):
        assert lang and data != None 
        self.encoding, self.lang = encoding, lang
        self._text = self._set_data(data, encoding)
        
    # unicode string
    def text(self): return self._text

    def __unicode__(self): return self.text()
    def __str__(self): return self.text().encode('utf-8')
    
    #  should build unicode representation of text   
    def _set_data(self, data, encoding):
        return text if isinstance(data, unicode) else unicode(data, encoding)


class TextFileCollection(FileWalker):
    def __init__(self, root, fmask = "**/*.txt"):
        FileWalker.__init__(self, root)
        self.fmask = fmask
    
    def ls(self, mask = None):
        if mask == None: mask = self.fmask
        res = []
        def c(p): res.append(p)
        self.walk(callback = c, mask = FileWalker.FileMask(mask))
        return [ f[len(self.root) + 1:] for f in res ]

    def handle_file(self, path): return 0
                
    def text(self, item):
        with codecs.open(os.path.join(self.root, item), 'r', 'utf-8') as f:
            return f.read()
    

class TokenizedText(Text):
    def _set_data(self, data, encoding):
        buf, offset = StringIO.StringIO(), 0
        for t in data:
            if t[1] < 0 or t[2] < 0: raise BaseException("Unknown token location")
            for i in range(t[1] - offset): buf.write(u' ')
            buf.write(t[0])
            offset = t[1] + t[2]
        text = buf.getvalue()
        buf.close()
        return text


class TextFile(Text):
    def _set_data(self, data, encoding):        
        with codecs.open(data, 'r', encoding=encoding) as f: return f.read()


class TestTextFile(Text):
    def _set_data(self, data, encoding):        
        with codecs.open(os.path.join(GRAVITY_LIB_HOME, "corpora", "test", data), 'r', encoding=encoding) as f: return f.read()


class GzipTextFile(Text):
    def _set_data(self, data, encoding):        
        name   = os.path.basename(data)
        ext    = os.path.splitext(name)[1].lower()
        return getattr(self, ext[1:len(ext)])(data)

    def gz(self, path):
        return self.gzip(path)
        
    def gzip(self, path):
        f = None
        try:
            f = gzip.open(path, 'rb')  
            return f.read()
        finally:
            if f: f.close()

class XmlText(Text):
    def __init__(self, data, lang = 'en', filter = XmlPathFilter(".*")):
        self.grabber = XmlGrabber()
        self.grabber.addXmlElementFilter(XmlPathFilter(".*"))
        Text.__init__(self, data, lang)
    
    def _set_data(self, data, encoding):        
        text = []
        def listener(xml_path, element, filter): 
            text.append(element.text.strip())
    
        self.grabber(data, listener)
        return '\n'.join(text)


# Internal structure to keep annotated tokens:
#   [ token1, ..., tokenN ] where token[3] = (TAG1, ..., TAGM) or None
#   
class AnnotatedText(Text):  
    def __init__(self, text, 
                       line_parser_re = re.compile(r"([^ ]+) (?P<POS>[^ ]+) (?:[^ ]+)? (?P<NE>[^ ]+)"),
                       ignore_line_re = re.compile(r"-DOCSTART-"),
                       lang = 'en'):
        assert line_parser_re
        self.ignore_line_re, self.line_parser_re = ignore_line_re, line_parser_re
        mg, ig = line_parser_re.groupindex, line_parser_re.groups
        if ig == 0 or ig - len(mg) != 1: 
            raise BaseException("Wrong line annotations parser expression (groups detected = %d) " % len(mg))
    
        # swap keys and values in dict
        mg = dict([(v, k) for (k, v) in mg.iteritems()])
    
        # store ordered list of possible tag names
        self.tags_groups = sorted(mg.keys())
        self.tags_names  = [ mg[i] for i in self.tags_groups ]
    
        # get token text value group index
        self.token_group_index = -1
        for i in range(ig):
            if (i + 1) not in mg:
                self.token_group_index = i + 1
                break
                
        Text.__init__(self, text, lang)
    
    def _set_data(self, text, encoding):
        class TAGS(tuple):
            def __getitem__(inner_self, key):
                if isinstance(key, int) or isinstance(key, long):
                    return super(TAGS, inner_self).__getitem__(key)
                else:
                    i = self.tags_names.index(key)
                    return super(TAGS, inner_self).__getitem__(i)
        
        r = self.line_parser_re
        
        off, tokens = 0, []
        for l in text.splitlines():
            l = l.strip()
            if len(l) == 0 or self.ignore_line(l): 
                tokens.append((l, off, 0, None))
                continue
                        
            m = r.match(l)
            if m == None: 
                tokens.append((l, off, 0, None))
                continue
            
            token, tags = m.group(self.token_group_index), TAGS([ m.group(i) for i in self.tags_groups])
            token_len = len(token)
            tokens.append((token, off, token_len, tags))
            off += (token_len + 1)
        
        self._tokens = tokens
        return self._build_text()
 
    def ignore_line(self, line): 
        return self.ignore_line_re != None and self.ignore_line_re.search(line) != None
    
    def tokens(self, tag_name = None):
        if tag_name == None: 
            for token in self._tokens: 
                if token[3] != None: yield (token[0], token[1], token[2], token[3])
        else:
            i = self.tags_names.index(tag_name)
            for token in self._tokens: 
                tags = token[3]
                if tags != None and tags[i] != 'O':
                    yield self.build_token(tag_name, token[0], token[1], token[2], tags[i])
            
    def iob_tokens(self, tag_name):
        def flush(r, off, p): 
            if len(r) == 0: return None
            t = ' '.join(r)
            return self.build_token(tag_name, t, off, len(t), p)
            
        i = self.tags_names.index(tag_name)

        r, p, off = [], None, -1
        for token in self._tokens: 
            tags, t = token[3], None
            if tags == None or tags[i] == 'O':
                t = flush(r, off, p)
                r, p, off = [], None, -1
                if t: yield t
                continue
                
            if tags[i][1] != '-': raise BaseException("%s is not IOB formatted tag" % tag_name)

            prefix, tag = tags[i][0:1], tags[i][2:]
            if (p != None and tag != p) or prefix == 'B':
                t = flush(r, off, p) 
                r, p, off = [], None, -1
                if t: yield t

            if len(r) == 0: off = token[1]
            r.append(token[0])
            p = tag

        if len(r) > 0: yield flush(r, off, p)

    def build_token(self, tag_name, text, off, length, tag):
        return (text, off, length, tag)

    def _build_text(self):
        buf, offset = StringIO.StringIO(), 0
        for t in self._tokens:
            if t[3] == None: continue
            for i in range(t[1] - offset): buf.write(u' ')
            buf.write(t[0])
            offset = t[1] + t[2]
        return buf.getvalue()


class TextBulk(Text):
    SEPARATOR     = u"...........,,....................,,.............."
    SEPARATOR_LEN = len(SEPARATOR)
    SEPARATOR_RE  = re.compile(SEPARATOR, re.U)
    
    def __init__(self, texts = [], lang='en', encoding = "latin-1"):
        Text.__init__(self, u'', lang, encoding)
        for t in texts: self += t
        
    def text(self):
        return self._text

    def _set_data(self, text, encoding):
        self._text, self._chunks  = u'', []

    def __len__(self): return len(self._chunks)
    
    def __getitem__(self, key):
        if key >= len(self._chunks) or key < 0: raise IndexError("%d" % key)
        return self._text[0:self._chunks[key]] if key == 0 else self._text[self._chunks[key - 1] + TextBulk.SEPARATOR_LEN:self._chunks[key]]

    def __setitem__(self, key, value):
        raise NotImplementedError()
        
    def __delitem__(self, key):
        raise NotImplementedError()

    def __contains__(self, item):
        raise NotImplementedError()
        
    def __iter__(self):
        class Iter(object):
            def __init__(self, bulk): 
                self.bulk, self.i = bulk, 0
            def __iter__(self): return self
            def next(self): 
                if self.i >= len(self.bulk): raise StopIteration()
                self.i += 1
                return self.bulk[self.i-1]
        
        return Iter(self)

    def align_tokens_to_chunks(self, tokens):        
        assert tokens

        ti = chunk_start = 0
        for chunk_end in self._chunks:
            text = self._text[chunk_start:chunk_end]

            tr = []
            while ti < len(tokens):
                t  = tokens[ti]
                ts = t[1]
                te = ts + t[2] - 1

                if ts > chunk_end: break
                if te > chunk_end: raise BaseException()
                                
                t[1] = ts - chunk_start
                tr.append(t)
                ti += 1
            
            yield (text, tr)
            chunk_start = chunk_end + TextBulk.SEPARATOR_LEN

    def __radd__(self, text):
        return self.__add__(text)

    def __iadd__(self, text):
        return self.__add__(text)
        
    def __add__(self, text):
        assert text 
        
        text = text if isinstance(text, unicode) else unicode(text)
        
        if len(self._chunks) == 0: 
            self._text = text
            self._chunks.append(len(text))
        else:                      
            self._text = u"".join([self._text, TextBulk.SEPARATOR, text])
            self._chunks.append(len(self._text))
            
        return self


class fMatch(object):        
    def __call__(self, text, pattern):
        assert text and pattern
        return self._match(unicode(text), unicode(pattern))
        
    # true/false
    def _match(self, text, pattern):
        raise NotImplementedError() 


class fSearch(object):
    #  None: if nothing has been found
    #  tuple(text, offset, len, type): if an substring has been found   
    def __call__ (self, text, pattern, offset = 0):
        assert text and pattern and offset >= 0 
        return self._search(unicode(text), unicode(pattern), offset)
    
    def _search(self, text, pattern, offset=0):
        raise NotImplementedError() 


def fSearchAll(search, text, pattern, offset = 0):
    while True:
        r = search(text, pattern, offset)
        if r == None: break
        yield r
        offset = r[1] + r[2]


class fStandardSearch(fSearch):
    def _search(self, text, pattern, offset = 0):
        i = text.find(pattern, offset)
        return None if i < 0 else (pattern, i, len(pattern), 0)

class fRegexpSearch(fSearch):
    def _search(self, text, pattern, offset = 0):
        p = re.compile(pattern)
        m = p.search(text, offset)
        if m == None: return None
        ft = text[m.start():m.end()]
        return (ft, m.start(), len(ft), 0)


class fStandardMatch(fMatch):
    def _match(self, text, pattern): return text == pattern

    
class fTextsAligner(object):    
    def  __call__(self, original_text, processed_text, offsets):
        assert original_text and processed_text and offsets
        return self._align(unicode(original_text), unicode(processed_text), offsets)
    
    #  return aray of aligned offsets
    def _align(self, original_text, processed_text, offsets):
        return offsets   


class fTokensAligner(object):
    class fRegexpTokenFinder(fSearch):
        split_pattern = re.compile(r'\s+',re.U)
        def _search (self, text, pattern, pos):
            a = [ re.escape(e) for e in self.split_pattern.split(pattern) ]
            r = re.compile(r'[ \t\n\r\\\/\,\.]+'.join(a), re.U)
            m = r.search(text, pos)
            return (pattern, m.start(), m.end() - m.start(), 0) if m else None
            
    def __init__(self, token_finder = fRegexpTokenFinder()):
        assert token_finder
        self.token_finder = token_finder

    def __call__(self, original_text, processed_text, tokens):
        offset, offsets = 0, []
        for t in tokens:
            r = self.token_finder(original_text, processed_text[t[1]:t[1] + t[2]], offset)
            if r:
                offset = r[1] + r[2]   
                t[1], t[2] = r[1], r[2]
            else:  
                t[1] = -1


if __name__ == '__main__':
    for t in TextFileCollection(".", "**/ner/*.py").ls(): print t
    pass


