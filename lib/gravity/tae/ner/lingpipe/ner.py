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
from gravity.tae.ner.ne import JavaBasedNER


class NER(JavaBasedNER):
    def __init__(self, lang='nl', model=None):
        JavaBasedNER.__init__(self, lang, model)

    def java_classpath(self):
        libs = super(NER, self).java_classpath()
        libs.append(os.path.join(self.home(), 'models'))
        libs.append(os.path.join(self.home(), 'lib'))
        return libs


if __name__ == '__main__':
    from gravity.tae import DEBUG_NER_TEXT
    print NER(lang='en')(DEBUG_NER_TEXT)
    
 
