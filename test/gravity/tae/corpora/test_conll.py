

from gravity.tae.corpora.conll import CoNLL, CoNLL2002, CoNLL2003, CoNLL2000
from gravity.tae.tokenizer import Token

import unittest, os, re


class TestCoNLL(unittest.TestCase):

    def test_conll(self):
        self.assertEqual(os.path.exists(CoNLL.home()), True)
        def f(): CoNLL.path('ddd')
        self.assertRaises(BaseException, f)
        def f(): CoNLL2002.path('ddd')
        self.assertRaises(BaseException, f)
        def f(): CoNLL2003.path('ddd')
        self.assertRaises(BaseException, f)
        def f(): CoNLL2000.path('ddd')
        self.assertRaises(BaseException, f)

    def test_conll2000(self):
        def f(): CoNLL2000.testa('d')
        self.assertRaises(BaseException, f)
        def f(): CoNLL2000.testb('d')
        self.assertRaises(NotImplementedError, f)
        def f(): CoNLL2000.train('d')
        self.assertRaises(BaseException, f)
        def f(): CoNLL2000.testa('en').baseline()
        self.assertRaises(NotImplementedError, f)

        c = CoNLL2000.testa("en")
        self._test_corpus(c)
        c = CoNLL2000.train("en")
        self._test_corpus(c)


    def test_conll2002(self):
        def f(): CoNLL2002.testa('d')
        self.assertRaises(BaseException, f)
        def f(): CoNLL2002.testb('d')
        self.assertRaises(BaseException, f)
        def f(): CoNLL2002.train('d')
        self.assertRaises(BaseException, f)
        
        c = CoNLL2002.testa("nl")
        b = c.baseline()
        self.assertEqual(b['phrases'], len([ e for e in c.ne_tokens()]))
        self._test_corpuses(CoNLL2002, "nl")
        self._test_corpuses(CoNLL2002, "es")
        
    def test_conll2003(self):
        c = CoNLL2003.testa("en")
        b = c.baseline()
        self.assertEqual(b['phrases'], len([ e for e in c.ne_tokens()]))
        self._test_corpuses(CoNLL2003, 'en')
        
    def test_eval(self):
        c = CoNLL2000.testa("en")
        t     = [ e for e in c.iob_tokens('SYN') ]
        all_t = [e for e in c.tokens() ]
        r = c.conlleval(t)
        self._test_self_eval_result(r, all_t, t)

        self._test_self_eval(CoNLL2002.testa("nl"))
        self._test_self_eval(CoNLL2002.testb("nl"))
        self._test_self_eval(CoNLL2002.train("nl"))

        self._test_self_eval(CoNLL2002.testa("es"))
        self._test_self_eval(CoNLL2002.testb("es"))
        self._test_self_eval(CoNLL2002.train("es"))

        self._test_self_eval(CoNLL2003.testa("en"))
        self._test_self_eval(CoNLL2003.testb("en"))
        self._test_self_eval(CoNLL2003.train("en"))
        
    def _test_self_eval(self, c):
        t     = [ e for e in c.ne_tokens() ]
        all_t = [e for e in c.tokens() ]
        
        r = c.conlleval(t)
        self._test_self_eval_result(r, all_t, t)

        for tag in ('LOC', 'MISC', 'ORG', 'PER'):
            self.assertEqual(r[tag+'_FB1'], 100.0)
            self.assertEqual(r[tag+'_recall'], 100.0)
            self.assertEqual(r[tag+'_precision'], 100.0)

    def _test_self_eval_result(self, r, all_t, t):
        self.assertEqual(r['accuracy'], 100.0)
        self.assertEqual(r['FB1'], 100.0)
        self.assertEqual(r['recall'], 100.0)
        self.assertEqual(r['precision'], 100.0)
        self.assertEqual(r['phrases'], r['correct_phrases'])
        self.assertEqual(r['tokens'], len(all_t))
        self.assertEqual(r['phrases'], len(t))
    
    def _test_corpuses(self, clz, lang):
        c = clz.testa(lang)
        self._test_corpus(c)
        c = clz.testb(lang)
        self._test_corpus(c)
        c = clz.train(lang)
        self._test_corpus(c)

    def _test_corpus(self, corpus):
        text = corpus.text()
        for t in corpus.tokens():
            if t[0] != None and text[t[1]:t[1] + t[2]] != t[0]:
                raise BaseException("Wrong entity '%s' location (%d, %d)" % (t[0], t[1], t[2]))        

        tags_names = corpus.tags_names

        if 'POS' in tags_names:
            for t in corpus.tokens('POS'):
                if t[0] != None and text[t[1]:t[1] + t[2]] != t[0]:
                    raise BaseException("Wrong entity '%s' location (%d, %d)" % (t[0], t[1], t[2]))        

        if 'NE' in tags_names:
            for t in corpus.iob_tokens('NE'):
                if t[0] != None and text[t[1]:t[1] + t[2]] != t[0]:
                    raise BaseException("Wrong entity '%s' location (%d, %d)" % (t[0], t[1], t[2]))        

        if 'SYN' in tags_names:
            for t in corpus.iob_tokens('SYN'):
                if t[0] != None and text[t[1]:t[1] + t[2]] != t[0]:
                    raise BaseException("Wrong entity '%s' location (%d, %d)" % (t[0], t[1], t[2]))        

        # c, tokens = 0, [e for e in corpus.tokens('NE')]
        # for t in ne_tokens:
        #     c += len(t[0].split(' '))
        # 
        # if c != len(tokens): raise BaseException("Wrong NE entity combining (%d != %d)" % (c, len(tokens)))        


if __name__ == '__main__':
    unittest.main()
    
    
    