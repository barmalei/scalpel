import re

from gravity.tae.tokenizer import Tokenizer, WordTokenizer
from gravity.tae.corpora.sentiment import Sentiment

class SentimentTokenizer(object):
    def __init__(self, lang="nl"):
        self.corpora = Sentiment(lang)
        
    def __call__(self, t):
        if not hasattr(t, "__iter__"): t = WordTokenizer(self.corpora.lang)(t)
        
        for tt in t:
            p = self.corpora.polarity(tt[0])
            if p != None: yield (tt[0], tt[1], tt[2], p)


class Polarity(object):
    def __call__(self, tokens):
        r = 0
        for t in tokens: r += t[-1]
        return r


if __name__ == '__main__':
    from gravity.tae.text import TestTextFile
    s = SentimentTokenizer()
    for t in s(TestTextFile("nrc1.nl.txt")): print(t)
    print(Polarity()(s(TestTextFile("nrc1.nl.txt"))))

