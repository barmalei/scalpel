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

import os

from ilps import ILPS_LIB_HOME
from ilps.tae.tokenizer import Tokenizer, Token
from ilps.common.internal.misc import list_module_implementations, instantiate_module_implementation
from ilps.tae.internal.jvm import JavaBasedTagger

class NER(Tokenizer):    
    class NamedEntityGlue(object):
        def __init__(self):
            self.names, self.type, self.offset = [], None, -1
    
        def __call__(self, name, offset, tp): return self.glue(name, offset, tp)

        def glue(self, name, offset, tp):
            t = None
            
            if self.type != None and tp != self.type:
                n = u' '.join(self.names)
                t = [n, self.offset, len(n), self.type]    
                self.type, self.names = None, []
                    
            if tp != None:
                self.names.append(name) 
                if self.type == None:
                    self.type = tp
                    self.offset = offset
            return t
    
        def flush(self):
            return self.glue(None, None, None)
                
    def __init__(self, lang='nl'):
        Tokenizer.__init__(self, lang)
                
    def info(self): raise NotImplementedError()
        
    @classmethod
    def list(cls):
        return list_module_implementations(cls)

    @classmethod
    def ner(cls, name, *args):
        m = cls.__module__.split('.')
        m = '.'.join(m[0:len(m)-1])
        m = __import__(m + "." + name + "." + cls.__name__.lower(), globals(), locals(), [cls.__name__], -1)
        return getattr(m, cls.__name__)(*args)


class JavaBasedNER(NER, JavaBasedTagger):
    def __init__(self, lang='nl', model=None):
        NER.__init__(self, lang)
        JavaBasedTagger.__init__(self, lang, model)
        self.tags_map = { 'LOC':Token.NE_LOC, 'PER':Token.NE_PER, 'ORG':Token.NE_ORG, 'MISC':Token.NE_MISC }
        
    def java_class(self):
        return "ilps.tae.ner.%s.%s" % (os.path.basename(self.home()), self.__class__.__name__)


if __name__ == '__main__':
    print NER.list()

