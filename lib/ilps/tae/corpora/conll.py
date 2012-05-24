#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from __future__ import with_statement

import re, codecs, os, StringIO, tempfile

from ilps.tae.tokenizer import Token
from ilps.tae.text import AnnotatedText
from ilps.tae.corpora.corpora import Corpora
from ilps.common.process import PipedProcess

# map not standard CoNLL language codes to standard
LANGS_MAP = { "nl":"ned", "es":"esp", "en":"eng", "de":"deu"}


class CoNLL(AnnotatedText):
    class ConnlevalOutputParser(object):
        def send(self, pipe): pass
        def read(self, pipe):
            class Results(dict):
                def __init__(self, lines):
                    assert lines
                    self.lines = lines
                
                def __str__(self): return ''.join(self.lines)
            
            lines = pipe.readlines()
            res   = Results(lines)

            m = re.compile(r"[^0-9]*([0-9]+)\s+(tokens)[^0-9]+([0-9]+)\s+(phrases)\;(.*)").match(lines[0].strip())
            g = m.groups()
            for i in range((len(g)-1)/2):
                j = 2*i + 1
                res[m.group(j+1)] = int(m.group(j))
            
            m = re.compile(r"[^0-9]*([0-9]+)[^0-9]+([0-9]+)[^0-9]*").match(m.group(len(g)))
            res['found_phrases']   = int(m.group(1))
            res['correct_phrases'] = int(m.group(2))

            m = re.compile(r"(accuracy)\s*\:\s*([0-9]+[.][0-9]+)\%\;\s*(precision)\s*\:\s*([0-9]+[.][0-9]+)\%\;\s*(recall)\s*\:\s*([0-9]+[.][0-9]+)\%\;\s*(FB1)\:\s*([0-9]+[.][0-9]+)").match(lines[1].strip())
            for i in range(len(m.groups())/2):
                j = 2*i + 1
                res[m.group(j)] = float(m.group(j+1))

            r = re.compile(r"\s*(\w+)\s*\:\s*(\w+)\s*\:\s*([0-9]+[.][0-9]+)\%\s*\;\s*(\w+)\s*\:\s*([0-9]+[.][0-9]+)\%\s*\;\s*(\w+)\s*\:\s*([0-9]+[.][0-9]+)\s*")
            for i in range(len(lines) - 2):
                l = lines[i + 2].strip()
                if len(l) == 0: continue
                m = r.match(l)
                g = m.groups()
                p = g[0]
                for k in range((len(g) - 1)/2):
                    j = 2*k + 2
                    res[p + '_' + m.group(j)] = float(m.group(j+1))
                
            return res

    def __init__(self, path, line_parser_re, lang):
        assert path and line_parser_re
        self.path = path
        with codecs.open(path, encoding='iso-8859-1') as f:
            AnnotatedText.__init__(self, f.read(), line_parser_re = line_parser_re, lang = lang)

    @classmethod
    def home(cls):
        return os.path.join(Corpora.corpora_home(), cls.__name__)
    
    @classmethod
    def path(cls, name, lang):
        p = os.path.join(cls.home(), 'data', '%s.%s' % (LANGS_MAP[lang], name))
        if not os.path.exists(p) or os.path.isdir(p): raise BaseException("Wrong path '%s'" % p)
        return p

    @classmethod
    def testa(cls, lang):
        return cls(path = cls.path('testa', lang), lang = lang)

    @classmethod
    def testb(cls, lang):
        return cls(path = cls.path('testb', lang), lang = lang)
    
    @classmethod
    def train(cls, lang):
        return cls(path = cls.path('train', lang), lang = lang)

    def _clone_token(self, t):
        return (t[0], t[1], t[2], t[3])

    def pos_tokens(self, type_filter = None):
        for e in self.iob_tokens('POS', type_filter): yield e

    def ne_tokens(self, type_filter = None):
        for e in self.iob_tokens('NE', type_filter): yield e

    def syn_tokens(self, type_filter = None):
        for e in self.iob_tokens('SYN', type_filter): yield e

    def build_token(self, tag_name, text, offset, length, tag):
        return (text, offset, length, self.tags_map[tag_name][tag])

    def iob_tokens(self, tag_name = None, type_filter = None):
        if type_filter == None: 
            for t in super(CoNLL, self).iob_tokens(tag_name): yield t
        else:
            for t in super(CoNLL, self).iob_tokens(tag_name):
                if (t[3] & type_filter) > 0: yield t
    
    def tokens(self, tag_name = None, type_filter = None):
        if type_filter == None: 
            for t in super(CoNLL, self).tokens(tag_name): yield t
        else:
            for t in super(CoNLL, self).tokens(tag_name):
                if (t[3] & type_filter) > 0: yield t

    #  Convert CoNLL formattted file into tsv (stanford for instance uses it for)
    #  tsv:
    #    <entity>\tab<ne_type>\n
    def to_tsv(self, output_path, delim = "\t", tag_map = { 'PER':'PERSON', 'LOC':'LOCATION', 'MISC':'MISC', 'ORG':'ORGANIZATION', 'O':'O'}):
        assert output_path and delim and tag_map
    
        with codecs.open(output_path, mode='w', encoding='utf-8') as o:       
            with codecs.open(self.path, encoding='iso-8859-1') as f:
                for line in f.readlines():
                    line = line.strip()
                    if len(line) > 0 and line.find('-DOCSTART-') < 0:
                        t = line.split(' ')
                        tp = t[-1]
                        if tp != 'O': tp = tp[tp.index('-') + 1:]
                        o.write(u"%s%s%s\n" % (t[0], delim, tag_map[tp]))
            o.write(u'\n')

    def _eval_fields (self, tokens, tag_name, types_map):
        tag_name_index = self.tags_names.index(tag_name)
      
        def find_next_match_token(i, tokens, t): 
            t_s, t_e  = t[1], t[1] + t[2] - 1
            
            if i < 0: i = 0
            
            for j in range(i, len(tokens), 1):
                rt_s, rt_e = tokens[j][1], tokens[j][1] + tokens[j][2] - 1
                if rt_s < 0 or rt_e < t_s: 
                    continue
                
                if t_s >= rt_s and t_e <= rt_e:
                    prefix =  'B-' if t_s == rt_s else 'I-'
                    t_t    =  tokens[j][3] #((tokens[j][3] & t_bits) | b_bit) ^ b_bit 
                    return (j, prefix, types_map[t_t], t_t)
                #elif (t_s < rt_s and t_e >= rt_s) or (t_s <= rt_e and t_e > rt_e): 
                 #   print "Entity location inconsistency '%s'(ner) = [%d, %d], '%s'(corpus) = [%d, %d]" % (tokens[j][0].encode('utf-8'), rt_s, rt_e, t[0].encode('utf-8'), t_s, t_e)  
                #    raise BaseException("Entity location inconsistency '%s'(ner) = [%d, %d], '%s'(corpus) = [%d, %d]" % (tokens[j][0], rt_s, rt_e, t[0], t_s, t_e)  )
                    
                return (j, '', 'O', 0)
                
            return (len(tokens), '', 'O', 0)
        
        li = 0
        ner, pt_type, i = None, 'O', -1
        
        for l in codecs.open(self.path, encoding='iso-8859-1').readlines():
            if self._tokens[li][2] == 0: 
                pt_type = 'O'
                yield ''
            else:
                w  = self._tokens[li][0]
                l  = l.strip()
                lt = l.split(' ')[-1].strip()

                ner = find_next_match_token(i, tokens, self._tokens[li])
                if lt == 'O':
                    yield w + ' O ' + ner[1] + ner[2]
                    pt_type = 'O' 
                else:
                    prefix, suffix = lt[0:2], lt[2:len(lt)]

                    if prefix != 'B-' and prefix != 'I-': raise BaseException("Wrong prefix in '%s'" % l)

                    if suffix != ner[2] or prefix == 'B-': yield w + ' ' + lt + ' ' + ner[1] + ner[2]
                    elif prefix == 'I-':
                        if ner[1] == 'B-' and pt_type != suffix: yield w + ' ' +  lt + ' I-' + ner[2]
                        else: yield w + ' ' + lt + ' ' + ner[1] + ner[2]
                    else:
                        raise BaseException("Unknown tag name %s" % lt)
                    pt_type = suffix

                i = ner[0]
            li += 1 

    def conlleval(self, tokens, tag_name = 'SYN', eval_script_name = 'conlleval.txt'):
        def reverse_map(m):
            mm = {}
            for k in m:
                v = m[k]
                if v in mm: raise BaseException(str(v) + " is in map " + str(m))
                mm[v] = k
            return mm    

        f  = tempfile.mkstemp(text = True)
        ff = None
        try:
            ff = open(f[1], 'w')
            for l in self._eval_fields(tokens, tag_name, reverse_map(self.tags_map[tag_name])):
                ff.write(l.encode("iso-8859-1") + "\n")
            ff.flush()
            ff.close()
            return PipedProcess(os.path.join(self.home(), "bin", eval_script_name) + "< %s" % f[1])(CoNLL.ConnlevalOutputParser())
        finally:
            if os.path.exists(f[1]): os.remove(f[1])
            
    def baseline(self, baseline_script_name = 'baseline.txt', eval_script_name = 'conlleval.txt'):
        class BaselineOutput(object):
            def read(self2, pipe):
                tmp = tempfile.mkstemp('a','b', self.home(), text = True)
                with open(tmp[1], 'w') as f:
                    for line in pipe.readlines(): f.write(line)
                return tmp[1]

            def send(self, pipe): pass
        
        p  = PipedProcess(os.path.join(self.home(), "bin", baseline_script_name) + " " +  self.__class__.path('train', self.lang) + " " + self.path)
        fn = p(BaselineOutput())
        try:
            return PipedProcess(os.path.join(self.home(), "bin", eval_script_name) + "< %s" % fn)(CoNLL.ConnlevalOutputParser())
        finally: 
            if fn != None: os.remove(fn)


class CoNLL2000(CoNLL):
    #  CC - Coordinating conjunction 
    #  CD - Cardinal number 
    #  DT - Determiner 
    #  EX - Existential there 
    #  FW - Foreign word 
    #  IN - Preposition or subordinating conjunction 
    #  JJ - Adjective 
    #  JJR - Adjective, comparative 
    #  JJS - Adjective, superlative 
    #  LS - List item marker 
    #  MD - Modal 
    #  NN - Noun, singular or mass 
    #  NNS - Noun, plural 
    #  NNP - Proper noun, singular 
    #  NNPS - Proper noun, plural 
    #  PDT - Predeterminer
    #  POS - Possessive ending 
    #  PRP - Personal pronoun 
    #  PRP$ - Possessive pronoun 
    #  RB - Adverb 
    #  RBR - Adverb, comparative 
    #  RBS - Adverb, superlative 
    #  RP - Particle 
    #  SYM - Symbol 
    #  TO - to 
    #  UH - Interjection 
    #  VB - Verb, base form 
    #  VBD - Verb, past tense 
    #  VBG - Verb, gerund or present participle 
    #  VBN - Verb, past participle 
    #  VBP - Verb, non-3rd person singular present
    #  VBZ - Verb, 3rd person singular present 
    #  WDT - Wh-determiner 
    #  WP - Wh-pronoun 
    #  WP$ - Possessive wh-pronoun 
    #  WRB - Wh-adver
    POS_TAG_MAP =  { 'NNP': Token.POS_NOUN,
                     'NNS': Token.POS_NOUN,
                     'NN': Token.POS_NOUN,
                     'NNPS': Token.POS_NOUN,
                     'VB': Token.POS_VERB,
                     'VBD': Token.POS_VERB,
                     'VBG': Token.POS_VERB,
                     'VBN': Token.POS_VERB,
                     'VBP': Token.POS_VERB,
                     'VBZ': Token.POS_VERB,
                     'MD' : Token.POS_VERB,
                     'PRP': Token.POS_PRONOUN,
                     'PRP$':Token.POS_PRONOUN,
                     'JJ': Token.POS_ADJ,
                     'JJS': Token.POS_ADJ,
                     'JJR': Token.POS_ADJ,
                     'IN': Token.POS_PREP,
                     'CD': Token.POS_NUM,
                     'CC' : Token.POS_CONJ,
                     'RB': Token.POS_ADVERB,
                     'RBR': Token.POS_ADVERB,
                     'RBS': Token.POS_ADVERB, 
                     'WDT':Token.POS_UNKNOWN,
                     'WRB':Token.POS_UNKNOWN,
                     'POS':Token.POS_UNKNOWN,
                     'DT':Token.POS_UNKNOWN,
                     'WP':Token.POS_UNKNOWN,
                     'WP$' :Token.POS_UNKNOWN,
                     'TO' :Token.POS_UNKNOWN,
                     'RP' :Token.POS_UNKNOWN,
                     'LS' :Token.POS_UNKNOWN,
                     'SYM' :Token.POS_UNKNOWN,
                     'FW' :Token.POS_UNKNOWN,
                     'EX' :Token.POS_UNKNOWN,
                     'PDT' :Token.POS_UNKNOWN,
                     'UH' :Token.POS_UNKNOWN,
                     ':'  : Token.POS_PUNCT,
                     "''"  : Token.POS_PUNCT,
                     "\'"  : Token.POS_PUNCT,
                     "["  : Token.POS_PUNCT,
                     "]"  : Token.POS_PUNCT,
                     "$"  : Token.POS_PUNCT,
                     "@"  : Token.POS_PUNCT,
                     "#"  : Token.POS_PUNCT,
                     "%"  : Token.POS_PUNCT,
                     "("  : Token.POS_PUNCT,
                     ")"  : Token.POS_PUNCT,
                     "-"  : Token.POS_PUNCT,
                     "``"  : Token.POS_PUNCT,
                     "!"  : Token.POS_PUNCT,
                     "?"  : Token.POS_PUNCT,
                     "\""  : Token.POS_PUNCT,
                     "\"\""  : Token.POS_PUNCT,
                     ','  : Token.POS_PUNCT,
                     '.'  : Token.POS_PUNCT, 
                     'NN|SYM': Token.POS_UNKNOWN }  # !!! very strange case, not clear wether it follows IOB standard !!!

    #  CoNLL 2000 declares 11 different chunks:
    #  { ADJP, ADVP, CONJP, INTJ, LST, NP, PP, PRT, SBAR, VP, UCP }.
    #  despite the large number of chunk types, the NP, VP and PP types account 
    #  for 95% of all chunk occurrences.    
    SYN_CHUNK_MAP = {
                        'VP'   : Token.SYN_CHUNK_VP,
                        'NP'   : Token.SYN_CHUNK_NP,
                        'PP'   : Token.SYN_CHUNK_PP, 
                        'ADJP' : Token.SYN_CHUNK_ADJP, 
                        'ADVP' : Token.SYN_CHUNK_ADVP,
                        'CONJP': Token.SYN_CHUNK_CONJP,
                        'INTJ' : Token.SYN_CHUNK_INTJ,
                        'LST'  : Token.SYN_CHUNK_LST,
                        'PRT'  : Token.SYN_CHUNK_PRT,
                        'SBAR' : Token.SYN_CHUNK_SBAR,
                        'UCP'  : Token.SYN_CHUNK_UCP
                    }


    def __init__(self, path, lang = 'en'):
        if lang != 'en': raise BaseException("Unsupported language %s" % lang)
        self.tags_map = { 'POS': CoNLL2000.POS_TAG_MAP, 'SYN':CoNLL2000.SYN_CHUNK_MAP }
        CoNLL.__init__(self, path = path, line_parser_re = re.compile(r"([^ ]+) (?P<POS>[^ ]+) (?P<SYN>[^ ]+)"), lang = lang)

    @classmethod
    def home(cls): return os.path.join(CoNLL.home(), '2000')

    @classmethod
    def testb(cls, lang):
        # no testb data set is available for this corpus
        raise NotImplementedError()

    def baseline(self, baseline_script_name = 'baseline', eval_script_name = 'conlleval'):
        # no baseline script is available for this corpus
        raise NotImplementedError()


class CoNLL2002(CoNLL):
    POS_TAG_MAP =  { 'Punc' : Token.POS_PUNCT,
                      'V'   : Token.POS_VERB,
                      'Adv' : Token.POS_ADVERB,
                      'Adj' : Token.POS_ADJ,
                      'Prep': Token.POS_PREP,
                      'Conj': Token.POS_CONJ,    
                      'Art' : Token.POS_ART,
                      'N'   : Token.POS_NOUN,
                      'Num' : Token.POS_NUM,
                      'Pron': Token.POS_PRONOUN,
                      'Misc': Token.POS_UNKNOWN,
                      'Int' : Token.POS_UNKNOWN }

    NE_TAG_MAP = { 'LOC'   : Token.NE_LOC, 
                    'PER'   : Token.NE_PER,
                    'ORG'   : Token.NE_ORG,
                    'MISC'  : Token.NE_MISC,
                    'O'     : Token.NE_UNKNOWN }

    def __init__(self, path, lang):
        if lang != 'nl' and lang != 'es':  raise BaseException("Unsupported language %s" % lang)
        self.tags_map = { 'POS': CoNLL2002.POS_TAG_MAP , 'NE': CoNLL2002.NE_TAG_MAP }
        if lang == 'nl':
            CoNLL.__init__(self, path = path, line_parser_re = re.compile(r"([^ ]+) (?P<POS>[^ ]+) (?P<NE>[^ ]+)"), lang = lang)
        else:
            CoNLL.__init__(self, path = path, line_parser_re = re.compile(r"([^ ]+) (?P<NE>[^ ]+)"), lang = lang)

    def conlleval(self, tokens, tag_name = 'NE'):
        return super(CoNLL2002, self).conlleval(tokens, tag_name = tag_name)

    @classmethod
    def home(cls):
        return os.path.join(CoNLL.home(), '2002')

                
class CoNLL2003(CoNLL):
    def __init__(self, path, lang = 'en'):
        if lang != 'en': raise BaseException("Unsupported language %s" % lang)
        self.tags_map = { 'POS': CoNLL2000.POS_TAG_MAP , 'NE': CoNLL2002.NE_TAG_MAP, 'SYN':CoNLL2000.SYN_CHUNK_MAP }
        CoNLL.__init__(self, path = path, line_parser_re = re.compile(r"([^ ]+) (?P<POS>[^ ]+) (?P<SYN>[^ ]+) (?P<NE>[^ ]+)"), lang = lang)
    
    @classmethod
    def home(cls):
        return os.path.join(CoNLL.home(), '2003')
        
    def conlleval(self, tokens, tag_name = 'NE', eval_script_name = 'conlleval'):
        return super(CoNLL2003, self).conlleval(tokens, tag_name= tag_name, eval_script_name = eval_script_name)

    def baseline(self, baseline_script_name = 'baseline', eval_script_name = 'conlleval'):
        return super(CoNLL2003, self).baseline(baseline_script_name, eval_script_name)

    # not completely settled method
    def convert_to_2002(self):
        with codecs.open(self.path + ".2002", mode='w', encoding='iso-8859-1') as f:
            prev_ne_tag = None
            for t in self._tokens: 
                if t[3] == None: 
                    f.write(t[0])
                    prev_ne_tag = None
                else:
                    ne, pos = t[3]['NE'], t[3]['POS']
                    if ne == 'O': 
                        f.write(t[0] + " " + pos + " O")
                        prev_ne_tag = None
                    else:
                        prefix, tg = ne[0:1], ne[2:]
                        if prefix == 'B': 
                            f.write(t[0] + " " + pos + " " + ne)
                        elif prev_ne_tag != tg:
                            f.write(t[0] + " " + pos + " B-" + tg)
                        else:
                            f.write(t[0] + " " + pos + " " + ne)
                        prev_ne_tag = tg
                f.write("\n")

    

# a = CoNLL2003.testa("en")    
# a.conlleval([t for t in a.ne_tokens()])


# t = CoNLL2002.train("nl")    
# t.to_tsv(output_path="ned.train.tsv")
# 
# t = CoNLL2002.testa("nl")    
# t.to_tsv(output_path="ned.testa.tsv")
# 
# t = CoNLL2002.testb("nl")    
# t.to_tsv(output_path="ned.testb.tsv")



# b = CoNLL2003.testb("en")    
# t = CoNLL2003.train("en")    
# a.convert_to_2002()
# b.convert_to_2002()
# t.convert_to_2002()
    