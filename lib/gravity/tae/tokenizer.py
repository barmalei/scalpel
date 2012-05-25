import re        

def _allocate_bit(bit = 0l):
    _allocate_bit.allocate_bit_value = _allocate_bit.allocate_bit_value << 1l
    return _allocate_bit.allocate_bit_value | bit   
_allocate_bit.allocate_bit_value = 1l

def _collect_variables(scope, prefix, tp = None):
    assert scope and prefix and len(prefix) > 1
    return set( [scope[k] for k in scope if k.find(prefix) == 0 and (tp == None or isinstance(scope[k], tp)) ])

def _collect_variables_repr(scope, prefix, tp = None):
    assert scope and prefix and len(prefix) > 1l
    r = {}    
    for k in scope: 
        if k.find(prefix) == 0 and (tp == None or isinstance(scope[k], tp)):
            r[scope[k]] = unicode(k[len(prefix):])  
    return r

def _acc_bits(b):
    a = 0l
    for bb in b: a |= bb
    return a 


class Token(object):
    POS_PUNCT     = _allocate_bit() 
    POS_VERB      = _allocate_bit()
    POS_ADVERB    = _allocate_bit()
    POS_PREP      = _allocate_bit()
    POS_CONJ      = _allocate_bit()
    POS_ART       = _allocate_bit()
    POS_NOUN      = _allocate_bit()
    POS_NUM       = _allocate_bit()
    POS_ADJ       = _allocate_bit()
    POS_PRONOUN   = _allocate_bit()
    POS_UNKNOWN   = _allocate_bit()

    # CoNLL 2000 chunks
    SYN_CHUNK_NP     = _allocate_bit()
    SYN_CHUNK_VP     = _allocate_bit()
    SYN_CHUNK_PP     = _allocate_bit()
    SYN_CHUNK_ADVP   = _allocate_bit()
    SYN_CHUNK_ADJP   = _allocate_bit()
    SYN_CHUNK_CONJP  = _allocate_bit()
    SYN_CHUNK_INTJ   = _allocate_bit()
    SYN_CHUNK_LST    = _allocate_bit()
    SYN_CHUNK_PRT    = _allocate_bit()
    SYN_CHUNK_SBAR   = _allocate_bit()
    SYN_CHUNK_UCP    = _allocate_bit()

    STR_SENTENSE  = _allocate_bit()
    STR_ARTICLE   = _allocate_bit()
    STR_PARAGRAPH = _allocate_bit()
     
    NE_ORG        = _allocate_bit()
    NE_LOC        = _allocate_bit()
    NE_PER        = _allocate_bit()
    NE_MISC       = _allocate_bit()
    NE_UNKNOWN    = _allocate_bit()
    
    POS_SET  = _collect_variables(locals(), "POS_", long)
    STR_SET  = _collect_variables(locals(), "STR_", long) 
    NE_SET   = _collect_variables(locals(), "NE_",  long) 
    SYN_CHUNK_SET = _collect_variables(locals(), "SYN_CHUNK_",  long) 
    
    _NE_REPR  = _collect_variables_repr(locals(), "NE_", long)
    _POS_REPR = _collect_variables_repr(locals(), "POS_", long)
    _STR_REPR = _collect_variables_repr(locals(), "STR_", long)
    _SYN_CHUNK_REPR = _collect_variables_repr(locals(), "SYN_CHUNK_", long)
    
    POS_BITS  = _acc_bits(POS_SET)
    NE_BITS   = _acc_bits(NE_SET)
    STR_BITS  = _acc_bits(STR_SET)
    SYN_CHUNK_BITS  = _acc_bits(SYN_CHUNK_SET)

    @classmethod
    def repr(cls, type):
        r = [u"NE="]
        
        ne_type = type & Token.NE_BITS 
        if ne_type > 0l and (ne_type in Token._NE_REPR):
            r.append(Token._NE_REPR[ne_type])
        else:r.append(u"UNKNOWN")
        
        r.append(u" POS=")
        pos_type = type & Token.POS_BITS 
        if pos_type > 0 and (pos_type in Token._POS_REPR):
            r.append(Token._POS_REPR[pos_type])
        else: r.append(u"UNKNOWN")

        r.append(u" STR=")
        str_type = type & Token.STR_BITS 
        if str_type > 0 and (str_type in Token._STR_REPR):
            r.append(Token._STR_REPR[str_type])
        else: r.append(u"UNKNOWN")
        return u''.join(r)           

    def __init__(self, *data):
        assert data        
        if len(data) == 1 and (isinstance(data[0], list) or isinstance(data[0], tuple)): data = data[0]        

        if len(data) == 4: tdata = data
        else:
            tdata = [None, -1, -1, 0]
            for i in range(len(data)): tdata[i] = data[i]      
            
        self.text, self.offset, self.len, self.type = tdata[0], tdata[1], tdata[2], tdata[3]
        if self.type == None: self.type = 0l
        
    def tuple(self): 
        return (self.text, self.offset, self.len, self.type)

    def __eq__(self, other):
        if other != None and len(other) == len(self):
            for i in range(len(self)): 
                if self[i] != other[i] : return False
            return True
            
        return False

    def __unicode__(self): 
        return  u"".join([ u"{ '", unicode(self.text), u"' [", unicode(self.offset), u"..", unicode(self.offset +  self.len - 1),  u"] ", Token.repr(self.type), u" }" ])

    def __repr__(self):
        return repr(self.text)  + ", " + str(self.offset) + ", " + str(self.len) + ", " + Token.repr(self.type)

    def __len__(self): return 4
    
    def __getitem__(self, key): 
        if key == 0: return self.text
        elif key == 1: return self.offset
        elif key == 2: return self.len
        elif key == 3: return self.type
        else: raise IndexError("%d" % key)
    
    def __setitem__(self, key, value):
        if key == 0: self.text = value
        elif key == 1: self.offset = value
        elif key == 2: self.len = value
        elif key == 3: self.type = value
        else: raise IndexError("%d" % key)

    def __delitem__(self, key): raise NotImplementedError()


class TokenSet(object):
    class Match(object):
        def __call__(self, tokens):
            for t in tokens: 
                try:           
                    if self.match(t): yield t
                except StopIteration: break    
                
        def match(self, token): raise NotImplementedError()

    class OR(Match):
        def __init__(self, *args):
            self.m = [a for a in args]

        def match(self, token): 
            for m in self.m: 
                if m.match(token): return True
            return False

    class AND(OR):
        def match(self, token): 
            for m in self.m: 
                if not m.match(token): return False
            return True

    class NOT(Match):
        def __init__(self, m): self.m = m
        def match(self, token): return not self.m.match(token)
            
    class Type(Match):
        def __init__(self, type = Token.NE_BITS): self.type = type
        def match(self, token): return (token[3] & self.type) > 0l

    class UndefPosition(Match):
        def match(self, token): return token[1] < 0 or token[2] < 0

    class InInterval(Match):
        def __init__(self, offset, ln):
            assert offset >= 0 and ln > 0
            self.offset1 = offset
            self.offset2 = offset + ln - 1

        def match(self, token):
            off1 = token[1]
            if off1 < 0: return False
            
            # interrupt to speed up
            if off1 > self.offset2: raise StopIteration()
            return self.offset1 <= off1 and (off1 + token[2] - 1) <= self.offset2

    #
    #  Test which tokens of the given tokens set match the specified tokens  
    class MatchToTokens(Match):
        def __init__(self, tokens, single_match=True):
            assert tokens
            self.tokens, self.ln, self.single_match = tokens, len(tokens), single_match
            
        def __call__(self, tokens):
            self.startup()
            for t in tokens:
                try:
                    t = Token(t)
                    t.matched = []
                    m = self.match(t)
                    if m: 
                        t.matched = m
                        yield t 
                except StopIteration: pass  

        def startup(self): pass
        def start_index(self, token): return 0
        def match_tokens(self, token1, token2): raise NotImplementedError()
        
        def match(self, token):            
            index = self.start_index(token)
            if self.single_match:
                while index < self.ln:
                    t = self.tokens[index]
                    if self.match_tokens(token, t): return [t]
                    index += 1
                return None
            else:
                m = []
                while index < self.ln:
                    t = self.tokens[index]
                    if self.match_tokens(token, t): m.append(t)
                    index += 1
                return m if len(m) > 0 else None
            
    class EqualTokens(MatchToTokens):
        def match_tokens(self, token1, token2): 
            return token1[0] == token2[0] and token1[1] == token2[1] and token1[2] == token2[2] and token1[3] == token2[3]  
    
    class EqualByPositionTokens(MatchToTokens):
        def match_tokens(self, token1, token2):
            return False if token1[1] < 0 or token2[1] < 0 else token1[1] == token2[1] and token1[2] == token2[2]  

    class IntersectedTokens(MatchToTokens):
        def __init__(self, tokens, single_match=False):
            TokenSet.MatchToTokens.__init__(self, tokens, single_match)
                    
        def start_index(self, token): return self.ln if token[1] < 0 else 0 
            
        def match_tokens(self, token1, token2):
            if token1[1] < 0 or token2[1] < 0: return False            
            
            t1_off1, t2_off1 = token1[1], token2[1]
            t1_off2, t2_off2 = t1_off1 + token1[2] - 1, t2_off1 + token2[2] - 1
            b = t1_off2 < t2_off1 or t1_off1 > t2_off2
            return not b

    def __init__(self, tokens):
        assert tokens
        self._tokens = tokens

    def __call__(self, rule = None): 
        for t in self.tokens(rule): yield t

    def tokens(self, rule=None):
        if rule == None:
            for t in self._tokens: yield t
        else:
            if isinstance(rule, (int, long)): rule = TokenSet.Type(rule)
            for t in rule(self._tokens): yield t
   
    def __len__(self): return len(self._tokens)
    def __getitem__(self, key): return self._tokens[key]
    def __iter__(self, args = None): return self._tokens.__iter__()
    def __setitem__(self, key, value): raise NotImplementedError()
    def __delitem__(self, key):raise NotImplementedError()

    def __contains__(self, item):
        for t in self._tokens: 
            if t[0] == item[0] and t[1] == item[1] and t[2] == item[2] and t[3] == item[3]: 
                return True
        return False
        
    def __unicode__(self):
        return u"\n".join([unicode(Token(t)) for t in self._tokens])


class Tokenizer(object):
    def __init__(self, lang = 'en'):
        assert lang
        self.lang = lang
        
    def __call__(self, text):
        assert text
        return self._tokenize(unicode(text))
        
    def _tokenize(self, text):    
        raise NotImplementedError()


class RegexpTokenizer(Tokenizer):
    def __init__(self, regexp, lang = 'en'):
        assert regexp
        Tokenizer.__init__(self, lang)
        self.regexp = regexp

    def _tokenize(self, text): 
        for match in self.regexp.finditer(text):
            offset, end = match.start(), match.end()
            yield (match.group(), offset, end - offset, 0)


class WhiteSpaceTokenzier(RegexpTokenizer):
    def __init__(self, lang = 'en'):
        RegexpTokenizer.__init__(self, re.compile(r'[^\s]+', re.U), lang)


class WordTokenizer(RegexpTokenizer):
    def __init__(self, lang="en"):
        RegexpTokenizer.__init__(self, re.compile(r'\w+', re.U), lang)



