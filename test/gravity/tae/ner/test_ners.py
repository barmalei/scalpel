

from gravity.tae.tokenizer import Token, TokenSet
from gravity.tae.ner.ne import NER, JavaBasedNER
from gravity import GRAVITY_LIB_HOME
from gravity.tae.corpora.conll import CoNLL2002

import unittest, os


class TestNERs(unittest.TestCase):

    def test_ner(self):
        glue = NER.NamedEntityGlue()
        tokens = [ ("Den", 0, 3, Token.NE_LOC), ("Haag", 4, 4, Token.NE_LOC), ("mmm", 9, 3, 0), (u"Amsterdam", 14, 9, Token.NE_LOC), ("mmm", 24, 3, 0), 
                   ("van", 28, 3, Token.NE_PER) , ("der", 32, 3, Token.NE_PER), ("Saar", 36, 4, Token.NE_PER)
                 ]
        
        res = []
        for t in tokens:
            r = glue(t[0], t[1], t[3])
            if r: res.append(r)
        
        self.assertEqual(len(res), 4)
        self.assertEqual(res[0][0], "Den Haag")
        self.assertEqual((res[0][3] & Token.NE_LOC) > 0, True)
        self.assertEqual(tuple(res[1]), tokens[2])
        self.assertEqual(tuple(res[2]), tokens[3])
        
        r = glue.flush()
        if r: res.append(r)
        
        self.assertEqual(len(res), len(tokens) - 3)
        self.assertEqual(res[0][0], "Den Haag")
        self.assertEqual((res[0][3] & Token.NE_LOC) > 0, True)
        self.assertEqual(tuple(res[1]), tokens[2])
        self.assertEqual(tuple(res[2]), tokens[3])
        self.assertEqual(tuple(res[3]), tokens[4])
        self.assertEqual(res[4], ["van der Saar", 28, 12, Token.NE_PER])

        self.assertEqual(JavaBasedNER().home(), os.path.join(GRAVITY_LIB_HOME, "ner"))
        
        self.assertEqual(len(NER.list()), 5)
        for n in ('lingpipe', 'stanford', 'lbj', 'tnt'):
            self.assertEqual(isinstance(NER.ner(n), NER), True)

        txt = "Amsterdam is amsterdam"
        n = NER.ner("lingpipe", 'nl', 'conll2002')(txt)
        self.assertEqual(len(n), 2)
        self.validate_tokens(txt, n)
        
        txt = "Amsterdam is capital of The Netherlands."
        n = NER.ner("stanford", 'nl', 'conll2002')(txt)
        self.assertEqual(len(n), 2)
        self.validate_tokens(txt, n)

        txt = "Amsterdam is capital of The Netherlands."
        n = NER.ner("lbj", 'en')(txt)
        self.assertEqual(len(n), 2)
        self.validate_tokens(txt, n)
        
        import platform
        if platform.platform().lower().find("linux") >= 0:
            txt = "Amsterdam is capital of The Netherlands."
            
            def f(): NER.ner("tnt", 'en')
            self.assertRaises(BaseException, f)
            
            n = NER.ner("tnt", 'nl')(txt)
            self.assertEqual(len(n), 2)
            self.validate_tokens(txt, n)
        else:
            print "Skip testing TNT tagger. It is possible on Linux platform only."

    def validate_tokens(self, txt, tokens):
        assert len(tokens) > 0
        for t in tokens: self.assertEqual(t[0], txt[t[1]:t[1] + t[2]])

    def validate_corpus_tokens(self, corpus, tokens):
        assert len(tokens) > 0
        ts = TokenSet(corpus.ne_tokens())
        r  = [ e for e in ts.tokens(TokenSet.EqualByPositionTokens(tokens)) ]
        
    def eval_ner(self, name, corpus, baseline, lang = "nl", model="conll2002"):
        t = NER.ner(name, lang, model)(corpus) if name != 'tnt' else  NER.ner(name, lang)(corpus)
        self.validate_corpus_tokens(corpus, t)
        r = corpus.conlleval(t)
        self.assertEqual(baseline['FB1'] < r['FB1'], True)
        self.assertEqual(baseline['recall'] < r['recall'], True)
        self.assertEqual(baseline['accuracy'] < r['accuracy'], True)
        
    def test_ner_quality(self):
        print "Evaluating NERs quality against CoNLL 2002 baseline"
        c = CoNLL2002.testb("nl")
        b = c.baseline()
        self.eval_ner("lingpipe", c, b)
        self.eval_ner("stanford", c, b)

        import platform
        if platform.platform().lower().find("linux") >= 0:
            self.eval_ner("tnt", c, b)
        else:
            print "Skip evaluating TNT tagger. It is possible on Linux platform only."
        

if __name__ == '__main__': 
    unittest.main()
