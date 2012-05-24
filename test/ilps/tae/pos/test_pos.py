

from ilps.tae.tokenizer import Token, TokenSet
from ilps.tae.pos.pos import POS
from ilps import ILPS_LIB_HOME
from ilps.tae.corpora.conll import CoNLL2002

import unittest, os


class TestPOS(unittest.TestCase):

    def test_pos(self):

        self.assertEqual(len(POS.list()), 2)
        for n in ('tnt', 'stanford'):
            self.assertEqual(isinstance(POS.pos(n), POS), True)

        txt = "This is center of Amsterdam !"
        n = POS.pos("stanford", 'en')(txt)
        
        self.assertEqual(len(n), len(txt.split()))
        self.validate_tokens(txt, n)
        self.assertEqual((n[-1][3] & Token.POS_PUNCT) > 0, True)
        self.assertEqual((n[-2][3] & Token.POS_NOUN) > 0, True)
        self.assertEqual((n[-2][3] & Token.POS_PUNCT) > 0, False)
    
        import platform
        if platform.platform().lower().find("linux") >= 0:
            txt = "Dat is de center."
            def test_lang(): POS.pos("tnt", 'en')
            self.assertRaises(AssertionError, test_lang)
            n = POS.pos("tnt", 'nl')(txt)
            self.assertEqual(len(n), 5)
            self.validate_tokens(txt, n)
            self.assertEqual((n[-1][3] & Token.POS_PUNCT) > 0, True)
            self.assertEqual((n[-2][3] & Token.POS_NOUN) > 0, True)
            self.assertEqual((n[-2][3] & Token.POS_PUNCT) > 0, False)
            self.assertEqual((n[-3][3] & Token.POS_ART) > 0, True)
        else:
            print "Skip testing TNT POS tagger. It is possible on Linux platform only."

    def validate_tokens(self, txt, tokens):
        assert len(tokens) > 0
        for t in tokens: self.assertEqual(t[0], txt[t[1]:t[1] + t[2]])

if __name__ == '__main__':
    unittest.main()
