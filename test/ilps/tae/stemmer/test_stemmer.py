

from ilps.tae.tokenizer import Token, WordTokenizer
from ilps.tae.stemmer.snowball.stemmer import Stemmer

import unittest, os


class TestStemmer(unittest.TestCase):

    def test_stemmer(self):
        self.assertEqual(len(Stemmer.list()), 1)
        # for n in ('snowball',):
        #     self.assertEqual(isinstance(Stemmer.stemmer(n), Stemmer), True)

        txt = "Words inconsistent  movies  selected "
        t  = [ e for e in WordTokenizer()(txt) ]
        st = [ e for e in Stemmer("en")(t) ]
        self.validate_tokens(txt, t)
        self.validate_tokens_by_loc(t, st)
        i = 0
        for e in ("word", "inconsist", "movi", "select"):
            self.assertEqual(st[i][0], e)
            i += 1


    def validate_tokens(self, txt, tokens):
        assert len(tokens) > 0
        for t in tokens: self.assertEqual(t[0], txt[t[1]:t[1] + t[2]])

    def validate_tokens_by_loc(self, t1, t2):
        self.assertEqual(len(t1), len(t2))
        for i in range(len(t1)): 
            self.assertEqual(t1[i][1] >= 0, True)
            self.assertEqual(t2[i][1] >= 0, True)
            self.assertEqual(t1[i][1], t2[i][1])
            self.assertEqual(t1[i][2], t2[i][2])


if __name__ == '__main__':
    unittest.main()
