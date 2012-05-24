import cPickle, os


from ilps.tae.tokenizer import TokenSet, Token
import ilps.tae.ner.ne

def _store_tokens(name, tokens):
    path = os.path.abspath(os.path.join('data', name + ".pickle"))
    print "Store to ", path
    f = open(path, 'w')
    try:     cPickle.dump(tokens, f, protocol = 2)
    finally: f.close()

def _load_tokens(name):
    path = os.path.abspath(os.path.join('data', name + ".pickle"))
    print "Load from ", path
    f = open(path, 'r')
    try:     return cPickle.load(f)
    finally: f.close()


def store_tokens(tokens, method, ner_id, lang, model = 'default'):
    if model == None: model = 'default'
    _store_tokens(ner_id + "." + lang + "." + model + "." + method, tokens)

def load_tokens(method, ner_id, lang, model = 'default'):
    if model == None: model = 'default'
    return _load_tokens(ner_id + "." + lang + "." + model + "." + method)

#
# NER/Corpus filter
# 1) NER: recognized entities that are not represented in Corpus
# 2) Corpus: get Corpus entities that have not been recognized 
#
class NotIntersectedSet(TokenSet.IntersectedTokens):
    # ner token is input
    def match(self, token):
        return not super(self.__class__, self).match(token)

class AllExactMatchSet(TokenSet.MatchToTokens):
    # ner token
    def match_tokens(self, token1, token2):
        return token1[1] == token2[1] and token1[2] == token2[2]

class EntityIntersectionStat(object):
    def __init__(self, ner_tokens, corpus_tokens, res_name="unknown"):
        assert ner_tokens and corpus_tokens and res_name
        
        self.res_name = res_name
        
        print "Calculating statistics .... "
        corpus_tokens = [t for t in corpus_tokens]
        self.corpus_defined_entities = len(corpus_tokens)  
        
        self.intersections = 0
        self.exact_match, self._exact_match = 0, []
        self.single_entity, self._single_entity = 0, []
        self.multiple_entities, self._multiple_entities = 0, []
        
        self.noise_in_entity, self._noise_in_entity = 0, []
        self.not_completed_entity, self._not_completed_entity = 0, []
        
        self.exact_match_type_error, self._exact_match_type_error = 0, []
        self.exact_match_no_type_error, self._exact_match_no_type_error = 0, []
        self.wrong_grouped_entities, self._wrong_grouped_entities= 0, []

        ner_tokens_set = TokenSet(ner_tokens)
        for t in ner_tokens_set.tokens(TokenSet.IntersectedTokens(corpus_tokens)):
            ner_off1, ner_off2 = t[1], t[1] + t[2] - 1
            if len(t.matched) > 1: 
                self.multiple_entities += 1
                ss_off1, ss_off2 = t.matched[0][1], t.matched[0][1]  + t.matched[0][2] - 1  
                es_off1, es_off2 = t.matched[-1][1], t.matched[-1][1]  + t.matched[-1][2] - 1  
            
                if ss_off1 == ner_off1 and es_off2 == ner_off2:
                    l = len(t.matched) - 1
                    for m in t.matched:
                        l += m[2]
                    if l == t[2]: self.wrong_grouped_entities += 1
            else:
                self.single_entity += 1
                c_off1, c_off2 = t.matched[0][1], t.matched[0][1]  + t.matched[0][2] - 1  
          
                if ner_off1 == c_off1 and ner_off2 == c_off2 : 
                    self.exact_match += 1
                    self._exact_match.append(t)
                    
                    if t.matched[0][3]  == t[3]:
                        self.exact_match_no_type_error += 1
                        self._exact_match_no_type_error.append(t)
                    else:
                        self.exact_match_type_error += 1
                        self._exact_match_type_error.append(t)
            
                elif ner_off1 < c_off1 or ner_off2 > c_off2: 
                    self.noise_in_entity += 1
                    self._noise_in_entity.append(t)
                elif ner_off1 > c_off1 or ner_off2 < c_off2: 
                    self.not_completed_entity += 1
                    self._not_completed_entity.append(t)
        
            self.intersections += 1
    
        print "Step 1 is done"
        self.not_in_corpus = len([e for e in ner_tokens_set.tokens(NotIntersectedSet(corpus_tokens))])
        print "Step 2 is done"
        self.not_in_ner    = len([e for e in TokenSet(corpus_tokens).tokens(NotIntersectedSet(ner_tokens))])
        print "Step 3 is done"
     #   self.pickle_results()
    
    
    def pickle_results(self):
        store_tokens(self.res_name + "-match.pickle", self._exact_match)
        store_tokens(self.res_name + "-te-match.pickle", self._exact_match_type_error)
        store_tokens(self.res_name + "-ne-match.pickle", self._exact_match_no_type_error)
        
    def __str__(self):
        text = [
                "===============================================\n",
                "Amount of intersected entities     | %5d/%d\n" % (self.intersections, self.corpus_defined_entities),
                "===============================================\n",
                "     1. Single intersections       |\n",   
                "          Exact match intersected  | %5d\n" %  self.exact_match,
                "             No error              | %5d\n" %  self.exact_match_no_type_error,
                "             Type mismatch         | %5d\n" %  self.exact_match_type_error,
                "          Noise text in entity     | %5d\n" %  self.noise_in_entity,
                "          Partially recognized     | %5d\n" %  self.not_completed_entity,
                "     2. Multiple intersections     | %5d\n" %  self.multiple_entities,
                "          Wrong grouped            | %5d\n" %  self.wrong_grouped_entities,
                "          Noise in                 | %5d\n" % (self.multiple_entities - self.wrong_grouped_entities),
                "     3. Not intersected entities   | \n",
                "          Not recognized entities  | %5d\n" % self.not_in_ner,
                "          Not in a corpus          | %5d\n" % self.not_in_corpus,
                "===============================================\n"
                ]
        return ''.join(text)


def show_corpus_characterestics(corpus):
    print "=========================== Evaluated CORPUS characteristics:"
    print "Number of entities: %d" % len([t for t in corpus.ne_tokens()])
    print "           persons: %d" % len([t for t in corpus.ne_tokens(Token.NE_PER)])
    print "          location: %d" % len([t for t in corpus.ne_tokens(Token.NE_LOC)])
    print "     organizations: %d" % len([t for t in corpus.ne_tokens(Token.NE_ORG)])
    print "              misc: %d" % len([t for t in corpus.ne_tokens(Token.NE_MISC)])



def evaluate_all(corpus, model = None):
    evaluate('tnt', corpus, model)
    evaluate('stanford', corpus, model)
    evaluate('lingpipe', corpus, model)
    
    
def evaluate(ner_id, corpus, model = None):
    t = run_recognizer(ner_id, corpus, model)
    s = EntityIntersectionStat(t, corpus.ne_tokens(), id)
    print s

def run_recognizer(ner_id, corpus, model = None):
    lang = corpus.lang
    
    if model == None:
        ner  = ilps.tae.ner.ne.NER.ner(ner_id, lang) 
    else: 
        ner = ilps.tae.ner.ne.NER.ner(ner_id, lang, model)
        
    tokens = [ t for t in ner(corpus) ]
    store_tokens(tokens, ner_id, lang, "recognized", model)
    return tokens

def run_all_recognizers_and_store_results(corpus, model = None):
    run_recognizer("tnt", corpus, model)
    run_recognizer("stanford", corpus, model)
    run_recognizer("lingpipe", corpus, model)

def calculate_recognition_quality(ner_id, corpus, model = None):
    tokens = load_all_recognized_tokens(ner_id, corpus.lang, model)
    print EntityIntersectionStat(tokens, corpus.ne_tokens())

def load_all_recognized_tokens(ner_id, lang = 'nl', model = None):
    return load_tokens(ner_id, lang, "recognized", model)

def load_all_matched_tokens(ner_id, lang = 'nl', model = None):
    return load_tokens(ner_id, lang, "recognized.all-matched", model)

def load_matched_wrongtyped_tokens(ner_id, lang = 'nl', model = None):
    return load_tokens(ner_id, lang, "recognized.wrongtype", model)

def load_exact_matched_tokens(ner_id, lang = 'nl', model = None):
    return load_tokens(ner_id, lang, "recognized.exact-matched", model)

def calc_recognized_types_distribution_for_exact(ner_id, lang = 'nl', model = None):
    t = load_exact_matched_tokens(ner_id, lang, model)
    s = TokenSet(t)
    misc = s.tokens(Token.NE_MISC)
    loc  = s.tokens(Token.NE_LOC)
    per  = s.tokens(Token.NE_PER)
    org  = s.tokens(Token.NE_ORG)
    print "======== %s Recognized entities type distribution :" % ner_id
    print "LOCATIONS    : %4d  %3d" % (len(loc), (len(loc)*100)/len(t)) 
    print "PERSONS      : %4d  %3d" % (len(per), (len(per)*100)/len(t)) 
    print "ORGANIZATION : %4d  %3d" % (len(org), (len(org)*100)/len(t)) 
    print "MISC         : %4d  %3d" % (len(misc),(len(misc)*100)/len(t)) 
    print "============================="
    print "AMOUNT       : %4d  100" % len(t) 
    
    
def calc_recognized_types_distribution_for_wrongly_recognized_entities(ner_id, lang = 'nl', model = None):
    t = load_matched_wrongtyped_tokens(ner_id, lang, model)
    s = TokenSet(t)
    misc = s.tokens(Token.NE_MISC)
    loc  = s.tokens(Token.NE_LOC)
    per  = s.tokens(Token.NE_PER)
    org  = s.tokens(Token.NE_ORG)
    print "======== %s Recognized entities type distribution :" % ner_id
    print "LOCATIONS    : %4d  %3d" % (len(loc), (len(loc)*100)/len(t)) 
    print "PERSONS      : %4d  %3d" % (len(per), (len(per)*100)/len(t)) 
    print "ORGANIZATION : %4d  %3d" % (len(org), (len(org)*100)/len(t)) 
    print "MISC         : %4d  %3d" % (len(misc),(len(misc)*100)/len(t)) 
    print "============================="
    print "AMOUNT       : %4d  100" % len(t) 


def calc_types_distribution_for_completly_wrongly_recognized_entities(ner_id, lang = 'nl', model = None):
    class NotMatchLocationSet(TokenSet.MatchSet):
        def __init__(self, tokens):
            super(self.__class__, self).__init__(tokens, False)
        
        def match_tokens(self, token1, token2):
            return token1[1] >= 0 and token2[1] >= 0 and (token1[1] != token2[1] or token1[2] != token2[2])  
    
    a = load_all_recognized_tokens(ner_id, lang, model)
    r = load_all_matched_tokens(ner_id, lang, model)
    nm = TokenSet.NotMatchSet(TokenSet.MatchLocationSet(r))
    s = TokenSet(TokenSet(a).tokens(nm))

    misc = s.tokens(Token.NE_MISC)
    loc  = s.tokens(Token.NE_LOC)
    per  = s.tokens(Token.NE_PER)
    org  = s.tokens(Token.NE_ORG)
    print "======== %s Recognized entities type distribution :" % ner_id
    print "LOCATIONS    : %4d  %3d" % (len(loc), (len(loc)*100)/len(s)) 
    print "PERSONS      : %4d  %3d" % (len(per), (len(per)*100)/len(s)) 
    print "ORGANIZATION : %4d  %3d" % (len(org), (len(org)*100)/len(s)) 
    print "MISC         : %4d  %3d" % (len(misc),(len(misc)*100)/len(s)) 
    print "============================="
    print "AMOUNT       : %4d  100" % len(s) 



def save_noise_entities(ner_id, corpus, model = None):
    a  = load_all_recognized_tokens(ner_id, corpus.lang, model)
    ct = corpus.ne_tokens()
 
    if model == None: model = 'default'
    f1 = open(ner_id + "." + corpus.lang + "." + model + ".multiple.txt", "w")
    f2 = open(ner_id + "." + corpus.lang + "." + model + "-single.txt", "w")

    for t in TokenSet(a).tokens(TokenSet.MatchIntersectedSet(ct)):
        ner_off1, ner_off2 = t[1], t[1] + t[2] - 1

        # multiple intersection
        if len(t.matched) > 1: 
            ss_off1, ss_off2 = t.matched[0][1], t.matched[0][1]  + t.matched[0][2] - 1  
            es_off1, es_off2 = t.matched[-1][1], t.matched[-1][1]  + t.matched[-1][2] - 1  
        
            f1.write(str(t) + "\n")
            for m in t.matched:
                f1.write(">>> " + str(Token(m)) + "\n")
        else:
            #  single intersection
            c_off1, c_off2 = t.matched[0][1], t.matched[0][1]  + t.matched[0][2] - 1  
      
            # exact matched tokens are not interested
            if ner_off1 == c_off1 and ner_off2 == c_off2 : continue
                
            f2.write(str(t) + "\n")
            for m in t.matched:
                f2.write(">>> " + str(Token(m)) + "\n")
    f1.close()
    f2.close()
    
def calc_3vote_result(corpus, model = None):
    def tokens_to_dict(tokens):
        m = {}
        for t in tokens: 
            m[(t[1], t[2])] = t 
        return m

    def intersect_tokens_arrays(tokens1, tokens2):
        d1 = tokens_to_dict(tokens1)
        d2 = tokens_to_dict(tokens2)
        r  = []
        for pair in d1.items():
            key, value = pair 
            if key in d2: r.append(value)
        
        return r

    t1 = load_all_recognized_tokens('tnt', corpus.lang, model)
    t2 = load_all_recognized_tokens('lingpipe', corpus.lang, model)
    t3 = load_all_recognized_tokens('stanford', corpus.lang, model)

    t = intersect_tokens_arrays(t3, t2)
    t = intersect_tokens_arrays(t, t1)
    return t


def calc_2vote_result(corpus, model = None):
    def tokens_to_dict(tokens):
        m = {}
        for t in tokens: 
            m[(t[1], t[2])] = [ t, 1 ] 
        return m

    def intersect_tokens_arrays(tokens1, tokens2, tokens3):
        d1 = tokens_to_dict(tokens1)
        d2 = tokens_to_dict(tokens2)
        d3 = tokens_to_dict(tokens3)
    
        for pair in d2.items():
            key, value = pair 
            if key in d1: d1[key][1] += 1 
            else: d1[key] = value

        for pair in d3.items():
            key, value = pair 
            if key in d1: d1[key][1] += 1 
    
        r  = []
        for pair in d1.items():
            key, value = pair 
            if value[1] > 1: r.append(value[0])
        
        return r

    t1 = load_all_recognized_tokens('tnt', corpus.lang, model)
    t2 = load_all_recognized_tokens('lingpipe', corpus.lang, model)
    t3 = load_all_recognized_tokens('stanford', corpus.lang, model)

    r = intersect_tokens_arrays(t1, t2, t3)
    stat = EntityIntersectionStat(r, corpus.ne_tokens(), "at least 2 votes")
    print stat
    return r


def calc_parametrized_vote_result(corpus, model = None):
    def tokens_to_dict(tokens, weight = 0.25):
        m = {}
        for t in tokens: 
            m[(t[1], t[2])] = [ t, weight ] 
        return m

    def intersect_tokens_arrays(tokens1, w1, tokens2, w2, tokens3, w3):
        d1 = tokens_to_dict(tokens1, w1)
        d2 = tokens_to_dict(tokens2, w2)
        d3 = tokens_to_dict(tokens3, w3)

        for pair in d2.items():
            key, value = pair 
            if key in d1: d1[key][1] += value[1] 
            else: d1[key] = value

        for pair in d3.items():
            key, value = pair 
            if key in d1: d1[key][1] += value[1] 
            else: d1[key] = value

        r  = []
        for pair in d1.items():
            key, value = pair 
            if value[1] >= 0.5: r.append(value[0])
        
        def sk(t): return t[1]
        return sorted(r, key = sk)
#        return r

    t1 = load_all_recognized_tokens('tnt', corpus.lang, model)
    t2 = load_all_recognized_tokens('lingpipe', corpus.lang, model)
    t3 = load_all_recognized_tokens('stanford', corpus.lang, model)


    r = intersect_tokens_arrays(t1, 0.25, t2, 0.25, t3, 0.5)
    stat = EntityIntersectionStat(r,[ e for e in corpus.ne_tokens() ], "parametrized votes")
    print stat
    return r



from ilps.tae.corpora.conll import CoNLL2002
from ilps.tae.corpora.conll import CoNLL2003
#corpus = CoNLL2003.testb("en")

corpus = CoNLL2002.testb("nl")


#show_corpus_characterestics(corpus)

#corpus = CoNLL2003.testb("en")
#corpus = CoNLL2002.testb("es")


# r = calc_parametrized_vote_result(corpus)
# print len(r)


evaluate('stanford2', corpus) 
#save_nose_entities('stanford', corpus)

#save_nose_entities('tnt', corpus)
    

#r1 = TokenSet(tnt_am).tokens(AllExactMatchSet(lpipe_am))
#r2 = TokenSet(r1).tokens(AllExactMatchSet(st_am))
#r3 = TokenSet(lpipe_t).tokens(AllExactMatchSet(st_t))
#c = corpus.ne_tokens()


#calc_types_distribution_for_completly_wrongly_recognized_entities('tnt')
#calc_types_distribution_for_completly_wrongly_recognized_entities('lpipe')
#calc_types_distribution_for_completly_wrongly_recognized_entities('st')

#print " >>>", len(lpipe_t), len(lpipe_am), len(lpipe_ne_m), len(lpipe_te_m)

#print "Exact match intersection TNT and LingPipe     ", len(r1), len(TokenSet(r1).tokens(AllExactMatchSet(c)))
#print "Exact match intersection TNT and Stanford     ", len(r2), len(TokenSet(r2).tokens(AllExactMatchSet(c)))
#print "Exact match intersection Stanford and LingPipe", len(r3), len(TokenSet(r3).tokens(AllExactMatchSet(c)))



#show_corpus_characterestics(corpus)

#t = run_recognizer('stanford', corpus)
# t = calc_parametrized_vote_result(corpus)
# print EntityIntersectionStat(t, [ e for e in corpus.ne_tokens() ], "stanford")
# print corpus.conlleval(t)


#t = calc_parametrized_vote_result(corpus)



#t = load_all_recognized_tokens('tnt', corpus.lang)
# t = load_all_recognized_tokens('lingpipe', corpus.lang, model)
# t = load_all_recognized_tokens('stanford', corpus.lang, model)
#r = intersect_tokens_arrays(t1, 0.25, t2, 0.25, t3, 0.5)

#calc_parametrized_vote_result(corpus)
#c = [ e for e in corpus.ne_tokens() ]
#t = run_recognizer("stanford", corpus)
#print corpus.conlleval(t)


#print EntityIntersectionStat(t, corpus.tokens('NE'), "st")
#print(len(t))






