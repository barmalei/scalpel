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

import ilps.tae.pos.pos
from ilps.tae.corpora.conll import CoNLL2000
from ilps.tae.internal.jvm import JavaBasedTagger


class POS(ilps.tae.pos.pos.POS, JavaBasedTagger):
    def __init__(self, lang='nl', model=None):
        ilps.tae.pos.pos.POS.__init__(self, lang)
        JavaBasedTagger.__init__(self, lang, model)
        self.memory, self.tags_map = "-mx512M", CoNLL2000.POS_TAG_MAP

    def home(self):
        return os.path.join(super(POS, self).home(), 'pos')

    def java_class(self):
        return "ilps.tae.pos.stanford.POS"

    def java_classpath(self):
        libs = super(POS, self).java_classpath()
        libs.append(os.path.join(self.home(), 'stanford-postagger.jar'))
        libs.append(os.path.join(self.home(), 'models'))
        return libs

      
if __name__ == '__main__':
    from ilps.tae import DEBUG_POS_TEXT
    print POS()(DEBUG_POS_TEXT)
    
