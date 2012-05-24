

from ilps.tae.tokenizer import Tokenizer, WordTokenizer, RegexpTokenizer, Token, TokenSet

import unittest, os


class TestTokens(unittest.TestCase):
    def test_tokenizer(self):
        def f(): RegexpTokenizer(None)
        
        self.assertRaises(AssertionError, f)
        
        text = "A , B   \t, 73 2 C \n D"
        tokens = [ t for t in WordTokenizer()(text) ]
        self.assertEqual(len(tokens) > 0, True)

        for t in tokens:
            self.assertEqual(t[0], text[t[1]:t[1]+t[2]])
            
    def test_token_set(self):
        tokens = (["Amsterdam", 0, 9, Token.NE_LOC],  ["FIFA", 30, 4, Token.NE_ORG], ["Something", -1, 4, 0], ["Amstel", 73, 6, Token.NE_MISC] )
        s = TokenSet(tokens)
        
        self.assertEqual(s[0], tokens[0])
        self.assertEqual(s[1], tokens[1])
        self.assertEqual(s[2], tokens[2])
        self.assertEqual(s[3], tokens[3])
        self.assertEqual(len(s), len(tokens))

        def f(): return s[4]
        self.assertRaises(IndexError, f)

        def f(): s[0] = ("",1,1, 0)
        self.assertRaises(NotImplementedError, f)

        self.assertEqual(tokens[0] in s, True)
        self.assertEqual(tokens[1] in s, True)
        self.assertEqual(tokens[2] in s, True)
        self.assertEqual(tokens[3] in s, True)
        self.assertEqual(("",2,2,2) in s, False)

        i = 0
        for t in s:
            self.assertEqual(tokens[i], t)
            i += 1
        self.assertEqual(len(tokens), i)

        i = 0
        for t in s.tokens():
            self.assertEqual(tokens[i], t)
            i += 1
        self.assertEqual(len(tokens), i)

        r = [e for e in s.tokens(Token.NE_BITS)]
        self.assertEqual(len(tokens)-1, len(r))

        r = [e for e in s.tokens(Token.NE_ORG)]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0], tokens[1])
        
        rule = TokenSet.UndefPosition()
        r = [e for e in s.tokens(rule)]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0], tokens[2])

        rule = TokenSet.InInterval(20, 53)
        r = [e for e in s.tokens(rule)]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0], tokens[1])

        rule = TokenSet.InInterval(20, 58)
        r = [e for e in s.tokens(rule)]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0], tokens[1])

        rule = TokenSet.InInterval(20, 59)
        r = [e for e in s.tokens(rule)]
        self.assertEqual(2, len(r))
        self.assertEqual(r[0], tokens[1])
        self.assertEqual(r[1], tokens[-1])
        
        def f1(): TokenSet.InInterval(-1, 52)
        def f2(): TokenSet.InInterval(0, 0)
        def f3(): TokenSet.InInterval(0, -1)
        self.assertRaises(AssertionError, f1)
        self.assertRaises(AssertionError, f2)
        self.assertRaises(AssertionError, f3)
        
        rule = TokenSet.NOT(TokenSet.UndefPosition())
        r = [e for e in s.tokens(rule)]
        self.assertEqual(3, len(r))
        self.assertEqual(r[0], tokens[0])
        self.assertEqual(r[1], tokens[1])
        self.assertEqual(r[2], tokens[3])

        rule = TokenSet.OR(TokenSet.Type(Token.NE_ORG), TokenSet.Type(Token.NE_LOC))
        r = [e for e in s.tokens(rule)]
        self.assertEqual(2, len(r))
        self.assertEqual(r[0], tokens[0])
        self.assertEqual(r[1], tokens[1])

        rule = TokenSet.AND(TokenSet.InInterval(0, 35), TokenSet.Type(Token.NE_LOC))
        r = [e for e in s.tokens(rule)]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0], tokens[0])

        rule = TokenSet.AND(TokenSet.InInterval(0, 35), TokenSet.OR(TokenSet.Type(Token.NE_LOC), TokenSet.Type(Token.NE_ORG)))
        r = [e for e in s.tokens(rule)]
        self.assertEqual(2, len(r))
        self.assertEqual(r[0], tokens[0])
        self.assertEqual(r[1], tokens[1])

        rule = TokenSet.NOT(TokenSet.OR(TokenSet.Type(Token.NE_ORG), TokenSet.Type(Token.NE_LOC)))
        r = [e for e in s.tokens(rule)]
        self.assertEqual(2, len(r))
        self.assertEqual(r[0], tokens[2])
        self.assertEqual(r[1], tokens[3])
        
        tokens_to_compare = (  ["Amsterdam", 0, 9, Token.NE_LOC],  ["FIFA", 30, 4, Token.NE_ORG] )
        rule = TokenSet.EqualTokens(tokens_to_compare)
        r = [e for e in s.tokens(rule)]
        self.assertEqual(2, len(r))
        self.assertEqual(r[0], Token(tokens[0]))
        self.assertEqual(r[1], Token(tokens[1]))

        rule = TokenSet.NOT(TokenSet.EqualTokens(tokens_to_compare))
        r = [e for e in s.tokens(rule)]
        self.assertEqual(2, len(r))
        self.assertEqual(r[0], tokens[2])
        self.assertEqual(r[1], tokens[3])

        rule = TokenSet.OR(TokenSet.EqualTokens(tokens_to_compare), TokenSet.UndefPosition())
        r = [e for e in s.tokens(rule)]
        self.assertEqual(3, len(r))
        self.assertEqual(r[0], tokens[0])
        self.assertEqual(r[1], tokens[1])
        self.assertEqual(r[2], tokens[2])

        rule = TokenSet.AND(TokenSet.EqualTokens(tokens_to_compare), TokenSet.UndefPosition())
        r = [e for e in s.tokens(rule)]
        self.assertEqual(0, len(r))

        tokens_to_compare = (  ["nsjdjsh", 0, 9, Token.NE_LOC],  ["sdsd", 30, 4, Token.NE_ORG], ['dssd', -1, 4, 0])
        rule = TokenSet.EqualByPositionTokens(tokens_to_compare)
        r = [e for e in s.tokens(rule)]
        self.assertEqual(2, len(r))
        self.assertEqual(r[0], Token(tokens[0]))
        self.assertEqual(r[1], Token(tokens[1]))

        tokens_to_compare = (  ["ABC", 0, 72, Token.NE_LOC], )
        rule = TokenSet.IntersectedTokens(tokens_to_compare)
        r = [e for e in s.tokens(rule)]
        self.assertEqual(2, len(r))
        self.assertEqual(r[0], Token(tokens[0]))
        self.assertEqual(r[1], Token(tokens[1]))

        tokens_to_compare = (  ["ABC", 0, 72, Token.NE_LOC], )
        rule = TokenSet.NOT(TokenSet.IntersectedTokens(tokens_to_compare))
        r = [e for e in s.tokens(rule)]
        self.assertEqual(2, len(r))
        self.assertEqual(r[0], tokens[2])
        self.assertEqual(r[1], tokens[3])
        
        tokens_to_compare = (  ["ABC", 33, 41, Token.NE_LOC], )
        rule = TokenSet.IntersectedTokens(tokens_to_compare)
        r = [e for e in s.tokens(rule)]
        self.assertEqual(2, len(r))
        self.assertEqual(r[0], tokens[1])
        self.assertEqual(r[1], tokens[3])

        
    def test_token(self):
        t   = ("Text", 0, 4, 10)
        tt  = Token(t)
        ttt = Token("Text", 0, 4, 10)
        
        self.assertEqual(t[0], tt.text)
        self.assertEqual(t[1], tt.offset)
        self.assertEqual(t[2], tt.len)
        self.assertEqual(t[3], tt.type)
        
        self.assertEqual(tt[0], tt.text)
        self.assertEqual(tt[1], tt.offset)
        self.assertEqual(tt[2], tt.len)
        self.assertEqual(tt[3], tt.type)
        
        self.assertEqual(ttt[0], tt.text)
        self.assertEqual(ttt[1], tt.offset)
        self.assertEqual(ttt[2], tt.len)
        self.assertEqual(ttt[3], tt.type)

        self.assertEqual(t[0], ttt.text)
        self.assertEqual(t[1], ttt.offset)
        self.assertEqual(t[2], ttt.len)
        self.assertEqual(t[3], ttt.type)

        tt[0] = 'Text2'
        tt[1] = 100
        tt[2] = 5
        tt[3] = 11
        
        self.assertEqual(tt.text, 'Text2')
        self.assertEqual(tt.offset, 100)
        self.assertEqual(tt.len, 5)
        self.assertEqual(tt.type, 11)

        def f(): tt[4] = 100
        self.assertRaises(IndexError, f)

        def f(): return tt[4]
        self.assertRaises(IndexError, f)

        self.assertEqual(Token("a", 0, 1, 0) == ('a', 0, 1, 0), True)
        

if __name__ == '__main__':
    unittest.main()
