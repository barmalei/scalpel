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

from ilps.tae.stemmer.snowball.so import Stemmer as SnowballStemmer

import ilps.tae.stemmer.stemmer

class Stemmer(ilps.tae.stemmer.stemmer.Stemmer):
    def __init__(self, lang = "nl"):
        super(self.__class__, self).__init__(lang)
        self.stemmer_lang = {'nl':'dutch', 'en':'english' }[lang] 
        assert self.stemmer_lang in SnowballStemmer.algorithms(), "No stemmer found for language %s" % lang

    def info(self):
        return "Snowball stemmer (Porter algorithm implementation)"

    def __call__(self, tokens):
        stemmer = SnowballStemmer.Stemmer(self.stemmer_lang)
        for t in tokens:  
            stem = stemmer.stemWord(t[0].lower())
            yield (stem, t[1], t[2], 0)


if __name__ == '__main__':
    from ilps.tae import DEBUG_STEMMER_TOKENS
    print [ e for e in Stemmer('en')(DEBUG_STEMMER_TOKENS) ]
