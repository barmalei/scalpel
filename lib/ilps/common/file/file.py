
from __future__ import with_statement
import codecs, os


class File(object):
    def __init__(self, path):
        assert path
        self.path = path

    def __lt__(self, other):
        i = None
        with codecs.open(self.path, 'w', 'utf-8') as f:
            try: 
                i = (e for e in other)
                for e in i:
                    if isinstance(e, unicode): f.write(e)
                    else: f.write(unicode(e))
                    f.write(u"\n")
                return
            except TypeError:
                pass
            
            if isinstance(other, unicode): f.write(other)
            else: f.write(unicode(other))
            
