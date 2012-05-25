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

from   gravity.tae.tokenizer import Token
from   gravity.tae.text import fTokensAligner
from   gravity.tae.internal.tnt import TNTExternalTool
import gravity.tae.pos.pos


class POS(gravity.tae.pos.pos.POS, TNTExternalTool): 
    def __init__(self, lang = "nl"):
        assert lang == 'nl'
        TNTExternalTool.__init__(self, lang, None, fTokensAligner(fTokensAligner.fRegexpTokenFinder()))
        self.tags_map = {  'LET':Token.POS_PUNCT, 'N': Token.POS_NOUN, 'ADJ':Token.POS_ADJ, 'WW':Token.POS_VERB, 
                           'TW':Token.POS_NUM,  'VNW': Token.POS_PRONOUN, 'VZ':Token.POS_PREP, 'BW':Token.POS_ADVERB,
                           'LID':Token.POS_ART, 'VG':Token.POS_UNKNOWN, 'TSW':Token.POS_UNKNOWN }
        
    def home(self):
        return os.path.join(super(self.__class__, self).home(), 'pos')
        
    def command(self):
        return os.path.join(self.home(), 'bin', 'pos')


if __name__ == '__main__':
    from gravity.tae import DEBUG_POS_TEXT
    print POS()(DEBUG_POS_TEXT)
