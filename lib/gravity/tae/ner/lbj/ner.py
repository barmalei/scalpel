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
from  gravity.tae.text import fTokensAligner
from  gravity.tae.ner.ne import JavaBasedNER


class NER(JavaBasedNER):
    def __init__(self, lang='nl', model=None):
        super(NER, self).__init__(lang, model)
        self.memory = "-mx2G"

    def _tokenize(self, text):        
        tokens, pos = super(NER, self)._tokenize(text), 0
        s = fTokensAligner.fRegexpTokenFinder()
        for t in tokens:
            r = s(text, t[0], pos)
            if r:
                t[1], t[2], pos = r[1], r[2], r[1] + r[2]
            else:
                print "Entity '%s' location cannot be identified properly" % t[0]
                #raise BaseException("Entity '%s' location cannot be identified properly" % t[0])

        return tokens

    def java_classpath(self):
        libs = super(NER, self).java_classpath()
        libs.append(self.home())
        libs.append(os.path.join(self.home(), 'bin'))
        libs.append(os.path.join(self.home(), 'Data'))
        libs.append(os.path.join(self.home(), 'Config'))
        return libs


if __name__ == '__main__':
    from gravity.tae import DEBUG_NER_TEXT
    print NER()(DEBUG_NER_TEXT)
