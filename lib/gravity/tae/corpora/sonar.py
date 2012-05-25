
import os

from gravity.tae.text import TextFileCollection, Text
from pynlpl.formats import folia
from gravity import GRAVITY_LIB_HOME


class SonarText(object):
    def __init__(self, data):
        self._data = data
    
    def __unicode__(self):
        return unicode(self._data)

    def __str__(self):
        return unicode(self._data).encode('utf-8')
        
    def tokens(self):
        pos = 0
        for e in self._data.data: 
            for w in e.items():
                if w.__class__ == folia.Word:
                    ww = unicode(w)
                    yield (ww, pos, len(ww), 0)
                    pos += len(ww) + 1
                elif w.__class__ == folia.Paragraph:
                    pos += 1
                    
    def _self_check(self):
        t = unicode(self)
        for i in self.tokens(): 
            if i[0] != t[i[1]:i[1] + i[2]]: 
                raise "Field '%s' doesn't much text field '%s'" % (i[0].encode('utf-8'), t[i[1]:i[1] + i[2]].encode('utf-8'))
        

class SonarFileCollection(TextFileCollection):
    def __init__(self, root = os.path.join(GRAVITY_LIB_HOME, 'corpora/sonar'), fmask = "**/*.pos"):
        TextFileCollection.__init__(self, root, fmask)
    
    def text(self, item):
        return SonarText(folia.Document(file=os.path.join(self.root, item)))



if __name__ == '__main__':
    s = SonarFileCollection()
    c = s.ls()
    # for f in s.ls(): print f
    # print s.text(c[0])
#     c = [ i for i in s.ls("*") ] 
#     s.text(c[0])._self_check()
