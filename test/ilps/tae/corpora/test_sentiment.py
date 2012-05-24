import re

from ilps.tae.sentiment import SentimentTokenizer, Polarity
from ilps.tae.corpora.sentiment import Sentiment
from ilps.tae.text import TextFile, Text
from ilps.tae.tokenizer import WordTokenizer

import unittest, os, re

ROOT = os.path.dirname(__file__)

tf1 = TextFile(os.path.join(ROOT, "sentiment-xps15-3.9.txt"))
tf2 = TextFile(os.path.join(ROOT, "sentiment-xps17-4.2.txt"))
tf3 = TextFile(os.path.join(ROOT, "sentiment-iwork-4.0.txt"))

ct1 = len([t for t in WordTokenizer()(tf1)])
ct2 = len([t for t in WordTokenizer()(tf2)])
ct3 = len([t for t in WordTokenizer()(tf3)])

class TestSentiment(unittest.TestCase):

    def test_sentiment_corpus(self):
        s = Sentiment()
        w = [ t for t in s.tokens() ]
        self.assertEquals(len(w), 4971)

        def f(): Sentiment(lang="en")
        self.assertRaises(BaseException, f)
        
        self.assertEquals(s.polarity("zweetspoor"), -2)
        self.assertEquals(s.polarity("Zweetspoor"), -2)
        self.assertEquals(s.polarity("ZWEETSPOOR"), -2)
        self.assertEquals(s.polarity("zonneklaar"), 4)
        self.assertEquals(s.polarity("Zonneklaar"), 4)
        self.assertEquals(s.polarity("ZONNEKLAAR"), 4)
        self.assertEquals(s.polarity("ZONNeKLAAR"), 4)

        self.assertEquals(s.polarity("Not found token"), None)
        
        
    def test_sentiment(self):
        st = SentimentTokenizer()
        p1 = Polarity()(st(tf1))
        p2 = Polarity()(st(tf2))
        p3 = Polarity()(st(tf3))
        self.assertTrue(p1 > 0)
        self.assertTrue(p2 > 0)
        self.assertTrue(p3 > 0)
        self.assertTrue(float(p1)/ct1 < float(p2)/ct2);
        self.assertTrue(float(p1)/ct1 < float(p3)/ct3);

        def f(): SentimentTokenizer(lang="en")
        self.assertRaises(BaseException, f)

        st = SentimentTokenizer()
        r1 = [t for t in st(tf1)]
        r2 = [t for t in st(WordTokenizer()(tf1))]
        self.assertTrue(len(r1) == len(r2))
        
        for i in range(len(r1)): 
            self.assertTrue(r1[i] == r2[i])
        
    
    def test_sentiment(self):
        txt =  " zonneklaar zooi zonneklopper zoonlief zorgelijk"
        t  = Text(txt)
        st = SentimentTokenizer()
        p  = Polarity()(st(t))
        self.assertEquals(p,1)

        txt =  " zonneklaar ,dsds zooi ssss\n\n !; zonneklopper qwertyu zoonlief. hsdjs zorgelijk"
        t  = Text(txt)
        p  = Polarity()(SentimentTokenizer()(t))
        self.assertEquals(p,1)


if __name__ == '__main__':
    unittest.main()


