

from ilps.tae.text import Text, TextBulk, TextFile, TokenizedText, GzipTextFile, XmlText 
from ilps.tae.text import fRegexpSearch, fMatch, fSearch, AnnotatedText
from ilps.tae.text import fStandardSearch, fStandardMatch, fSearchAll, fTokensAligner
from ilps.tae.tokenizer import WhiteSpaceTokenzier

import unittest, os, re

test_dir  = os.path.dirname(__file__)
txt_file  = os.path.join(test_dir, "text.txt")
assert os.path.exists(txt_file)


class TestText(unittest.TestCase):

    def test_text(self):
        def f1(): Text(None)
        def f2(): Text('', lang = None)
        def f3(): Text('', lang = '')
        
        self.assertRaises(AssertionError, f1)
        self.assertRaises(AssertionError, f2)
        self.assertRaises(AssertionError, f3)

        t = Text('')
        self.assertEqual(t.text(), '')
        self.assertEqual(isinstance(t.text(), unicode), True)

        t = Text('text')
        self.assertEqual(t.text(), 'text')
        self.assertEqual(isinstance(t.text(), unicode), True)

        t = TextFile(txt_file)
        self.assertEqual(t.text(), 'text file')
        self.assertEqual(isinstance(t.text(), unicode), True)
        
    
    def test_text_bulk(self):
        b = TextBulk()
        
        b += Text("a")
        b += "b"
        b += "abc"

        self.assertEqual(3, len(b))
        self.assertEqual('a', b[0])
        self.assertEqual('b', b[1])
        self.assertEqual('abc', b[2])

        def f1(): b[1] = 's'
            
        self.assertRaises(NotImplementedError, f1)

        t, i = '', 0
        for tt in b: 
            if i > 0: t += TextBulk.SEPARATOR
            t += tt
            i+=1
        
        self.assertEqual(t, b.text())
            
        b = TextBulk()  
        b = b + Text("a")
        self.assertEqual(1, len(b))
        self.assertEqual('a', b[0])

        b = TextBulk()  
        b = "a" + b
        self.assertEqual(1, len(b))
        self.assertEqual('a', b[0])

        b1 = TextBulk(['a', 'b'])  
        self.assertEqual(2, len(b1))
        self.assertEqual('a', b1[0])
        self.assertEqual('b', b1[1])
        
                 #01234567890123456789
        text1 =  "Abra kadabra bbb"
        text2 =  "Pimps pumps pomps"
        tokens = [ ['Abra', 0, 4, 0], ['bbb', 13, 3, 0], ['pumps', len(text1) + TextBulk.SEPARATOR_LEN + 6, 5, 0  ] ]
        b  = TextBulk( [text1, text2] )
        ch = [ t for t in b.align_tokens_to_chunks(tokens) ]
        
        self.assertEqual(len(ch), 2)
        self.assertEqual(len(b), 2)
        
        t1, t2 = ch[0], ch[1]
        self.assertEqual(text1, t1[0])
        self.assertEqual(text2, t2[0])
        
        def validate_token(t1, t2, off2):
            self.assertEqual(t1[0], t2[0])
            self.assertEqual(t1[2], t2[2])
            self.assertEqual(t1[3], t2[3])
            self.assertEqual(t2[1], off2)
            
        validate_token(tokens[0], t1[1][0], 0)
        validate_token(tokens[1], t1[1][1], 13)
        validate_token(tokens[2], t2[1][0], 6)
        
    def test_fmatch(self):
        def f1(): fMatch()('d', '')
        def f2(): fMatch()('', 'd')
        def f3(): fMatch()(None, 'ss')
        def f4(): fMatch()('dd', None)
        def f5(): fSearch()('d', '')
        def f6(): fSearch()('', 'd')
        def f7(): fSearch()(None, 'ss')
        def f8(): fSearch()('dd', None)
            
        self.assertRaises(AssertionError, f1)
        self.assertRaises(AssertionError, f2)
        self.assertRaises(AssertionError, f3)
        self.assertRaises(AssertionError, f4)
        self.assertRaises(AssertionError, f5)
        self.assertRaises(AssertionError, f6)
        self.assertRaises(AssertionError, f7)
        self.assertRaises(AssertionError, f8)

        t = fStandardSearch()("vish@gravitysoft.org", "gra", 4)
        self.assertEqual("gra", t[0])
        self.assertEqual(5, t[1])
        self.assertEqual(3, t[2])

        t = fStandardSearch()("vish@gravitysoft.org", "gra", 10)
        self.assertEqual(t, None)

        self.assertEqual(fStandardMatch()("a", "a"), True)
        self.assertEqual(fStandardMatch()("b", "a"), False)
        
        t = fRegexpSearch()("vish@gravitysoft.org", r"\@[a-zA-Z0-9]+", 4)
        self.assertEqual("@gravitysoft", t[0])
        self.assertEqual(4, t[1])
        self.assertEqual(12, t[2])

        t = fRegexpSearch()("vish@gravitysoft.org", r"\@[a-zA-Z0-9]+", 5)
        self.assertEqual(t, None)
        
        t = "abcabcaaa"
        r = [ e for e in fSearchAll(fStandardSearch(), t, 'a') ]
        self.assertEqual(len(r), 5)
        self.assertEqual(r[0][1], 0)
        self.assertEqual(r[1][1], 3)
        self.assertEqual(r[2][1], 6)
        self.assertEqual(r[3][1], 7)
        self.assertEqual(r[4][1], 8)
        
    def test_token_aligner(self):
                #           1         2         3          4         5          6         7    
                #01234567890123456789012345678901 23456789012345678901 2345678901234567890123456789        
        otext = "  Amsterdam is capital of The  \t Netherlands. Den  \n,Haag is just a Dutch city."
                
                #           1         2         3         4         5         6         7    
                #01234567890123456789012345678901234567890123456789012345678901234567890123456789        
        ptext = "Amsterdam is capital of The Netherlands. Den Haag is just a Dutch city."        
        
        tokens = ( ["Amsterdam", 0, 9, 0], ["The Netherlands", 24, 15, 0], ["Den Haag", 41, 8, 0], ["Dutch", 60, 5, 0] )
        for tt in tokens:
            self.assertEqual(ptext[tt[1]:tt[1] + tt[2]], tt[0])

        fTokensAligner()(otext, ptext, tokens)
        self.assertEqual(tokens[0][1], 2)
        self.assertEqual(tokens[0][2], 9)
        self.assertEqual(tokens[1][1], 26)
        self.assertEqual(tokens[1][2], 18)
        self.assertEqual(tokens[2][1], 46)
        self.assertEqual(tokens[2][2], 11)
        self.assertEqual(tokens[3][1], 68)
        self.assertEqual(tokens[3][2], 5)

    def test_tokenized_text(self):
        text = "The   ZIP   file          format is \n\n a common archive   and   compression   standard. \n\t This module provides tools \n to create ,  read,  write."
        
        tokens = [ t for t in WhiteSpaceTokenzier()(text) ]
        self.assertEqual(len(tokens) > 0, True)
        
        ttext = TokenizedText(tokens).text()
        for t in tokens:
            self.assertEqual(t[0], ttext[t[1]:t[1] + t[2]])
            self.assertEqual(t[0], text[t[1]:t[1] + t[2]])

    def test_gzipped_text(self):
        t = GzipTextFile(os.path.join(test_dir, 'text.txt.gz'))
        self.assertEqual(len(t.text()) > 0, True)
        self.assertEqual(t.text(), TextFile(txt_file).text())
        
    def test_xml_text(self):
        t = XmlText(os.path.join(test_dir, 'text.xml'))
        self.assertEqual(len(t.text()) > 0, True)
        self.assertEqual(len(t.text().split("\n")), 2)


    def test_annotated_text(self):
        def test_pos(tokens, text):
            for t in tokens:
                self.assertEqual(text[t[1]:t[1] + t[2]], t[0])
        
        
        def f(): AnnotatedText('abcd', line_parser_re = None)
        self.assertRaises(AssertionError, f)
        
        txt = '''
        WORD1 TAG11 TAG21
        
        WORD2 TAG12 TAG21
        WORD3 TAG11 O
        '''

        a = AnnotatedText(txt, line_parser_re = re.compile(r'([^ ]+) (?P<TAG1>[^ ]+) (?P<TAG2>[^ ]+)'))
        self.assertEqual(len(a.tags_names), 2)
        self.assertEqual(a.tags_names, ['TAG1', 'TAG2'])
        self.assertEqual(len(a.tags_groups), 2)
        self.assertEqual(a.tags_groups, [2, 3])

        tokens = [t for t in a.tokens()]
        self.assertEqual(len(tokens), 3)
        self.assertEqual(len(a._tokens), 6)
        i, tt = 0, (('TAG11', 'TAG21'), ('TAG12', 'TAG21'), ('TAG11', 'O'))
        for t in ('WORD1', 'WORD2', 'WORD3'): 
            self.assertEqual(t, tokens[i][0])
            self.assertEqual(tt[i], tokens[i][3])
            i+=1

        test_pos(tokens, str(a))

        tokens = [t for t in a.tokens('TAG1')]
        self.assertEqual(len(tokens), 3)

        tokens = [t for t in a.tokens('TAG2')]
        self.assertEqual(len(tokens), 2)

        def f(): tokens = [t for t in a.tokens('TAG3')]
        self.assertRaises(ValueError, f)

        txt = '''
        TAG11 WORD1 I-TAG21
        
        WARNING
        
        TAG12 WORD2 B-TAG21
        TAG11 WORD3 O
        
        O WORD4 I-TAG21
        O WORD5 B-TAG21
        O WORD6 I-TAG21
        O WORD7 O
        '''
        a = AnnotatedText(txt, line_parser_re = re.compile(r'(?P<TAG1>[^ ]+) ([^ ]+) (?P<TAG2>[^ ]+)'), ignore_line_re = re.compile(r'WARNING'))
        self.assertEqual(len(a.tags_names), 2)
        self.assertEqual(a.tags_names, ['TAG1', 'TAG2'])
        self.assertEqual(len(a.tags_groups), 2)
        self.assertEqual(a.tags_groups, [1, 3])
   
        tokens = [t for t in a.tokens()]
        self.assertEqual(len(tokens), 7)
        self.assertEqual(len(a._tokens), 13)
        
        tokens = [t for t in a.iob_tokens('TAG2')]
        tt, i   = ('WORD1', 'WORD2', 'WORD4', 'WORD5 WORD6'), 0
        self.assertEqual(len(tokens), 4)
        for t in tokens: 
            self.assertEqual(t[0], tt[i])
            self.assertEqual(t[3], 'TAG21')
            i+=1
        test_pos(tokens, str(a))


if __name__ == '__main__':
    unittest.main()
