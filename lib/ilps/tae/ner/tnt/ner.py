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

import os

from   ilps.tae.tokenizer import Token
from   ilps.tae.internal.tnt import TNTExternalTool
import ilps.tae.ner.ne 
        
        
class NER(ilps.tae.ner.ne.NER, TNTExternalTool):
    def __init__(self, lang='nl'):
        if lang != 'nl': raise BaseException("Only dutch language is supported")
        ilps.tae.ner.ne.NER.__init__(self, lang)
        TNTExternalTool.__init__(self, lang, ilps.tae.ner.ne.NER.NamedEntityGlue())
        self.tags_map = { u"MISC":Token.NE_MISC, u"PER":Token.NE_PER, u"LOC":Token.NE_LOC, u"ORG":Token.NE_ORG }
        
    def home(self):
        return os.path.join(super(self.__class__, self).home(), 'ner')
        
    def command(self):
        h = os.path.join(self.home(),  "ner")
        return os.path.join(h, "bin", "tokenize -n ")  + " | " + os.path.join(h, "bin", "ner") 


if __name__ == '__main__':
    from ilps.tae import DEBUG_NER_TEXT
    print NER()(DEBUG_NER_TEXT)
