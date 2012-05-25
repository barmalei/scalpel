#       This progra m is free software; you can redistribute it and/or modify
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

import re, os

from   gravity.tae.tokenizer import Tokenizer
from   gravity.tae.text import fTokensAligner
from   gravity.common.process import PipedProcess
from   gravity.common.internal.misc import ExternalTool
from   gravity import GRAVITY_LIB_HOME


class TNTExternalTool(Tokenizer, ExternalTool):
    def __init__(self, lang='nl', tokens_glue = None, tokens_aligner =fTokensAligner(fTokensAligner.fRegexpTokenFinder())):
        assert tokens_aligner
        Tokenizer.__init__(self, lang)
        self.text_parse_re  = re.compile('([^/\s]+/[A-Z0]+)', re.U)
        self.tokens_aligner = tokens_aligner
        self.glue = tokens_glue

    def _tokenize(self, text):        
        p, r, offset = [], [], 0

        for match in self.text_parse_re.finditer(self.run_external_tool(text)):
            m = match.group().split('/')
            p.append(m[0])
            tp = self.map_tag(m[1])
            
            if self.glue != None:
                t = self.glue(m[0], offset, tp)
                if t: r.append(t)
            elif tp != None:
                r.append([m[0], offset, len(m[0]), tp])

            offset += (1 + len(m[0]))

        if self.glue != None:
            t = self.glue.flush()
            if t: r.append(t)
        
        # !!! useful for experements, but redundant for software
        self._processed_text = u' '.join(p)
        
        self.tokens_aligner(text, self._processed_text, r) 
        return r
        
    def map_tag(self, tag): 
        return self.tags_map[tag] if tag in self.tags_map else None
        
    def command(self): raise NotImplementedError()
        
    def home(self):
        return os.path.join(GRAVITY_LIB_HOME, 'quartz')
        
    def run_external_tool(self, text):
        assert text
        class Callback(PipedProcess.Callback): 
            def __init__(self, text): self.text = text
            def send(self, pipe): 
                pipe.write(text.encode('latin-1', 'ignore'))
                pipe.close()
                
            def read(self, pipe): 
                r = pipe.read().decode('latin-1')
                return r
                
        return PipedProcess(self.command())(Callback(text))

