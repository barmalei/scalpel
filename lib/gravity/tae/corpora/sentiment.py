
from __future__ import with_statement

import re, codecs, os
from gravity.tae.corpora.corpora import Corpora
from gravity.tae.text import AnnotatedText

class Sentiment(AnnotatedText):
    def __init__(self, lang = "nl"):
        path, text = Sentiment.path("sentiment", lang), None;
        with codecs.open(path, encoding='iso-8859-1') as f: 
            text = f.read()
            
        super(Sentiment, self).__init__(text, re.compile(r"([^\t ]+)\s+(?P<SENT>[\+\-]+)"), re.compile(r"\s*#"), lang)
        self.polarities = {}
        for t in self.tokens(tag_name = "SENT"): self.polarities[t[0]] = t[-1]
    
    @classmethod
    def home(cls):
        return os.path.join(Corpora.corpora_home(), "ILPS")

    @classmethod
    def path(cls, name, lang):
        p = os.path.join(cls.home(), '%s.%s.txt' % (name, lang))
        if not os.path.exists(p) or os.path.isdir(p): raise BaseException("Wrong path '%s'" % p)
        return p

    def build_token(self, tag_name, text, off, length, tag):
        return (text, off, length, tag.count('+') - tag.count('-'))

    def polarity(self, text):
        text = text.lower()
        return self.polarities[text] if text in self.polarities else None 
        

if __name__ == '__main__':
    s = Sentiment()
    for t in s.tokens("SENT"):
        print(t)
    
    

