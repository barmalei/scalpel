
from ilps.tae.tokenizer import Token            
from ilps.tae.corpora.sonar import SonarFileCollection
            
class CloudTokenSet(object):
    class TopScored(object):
        def __init__(self, max_items = -1):
            self.max_items = max_items
            
        def __call__(self, tokens):
            if self.max_items > 0:
                m = min(self.max_items, len(tokens))
            else:
                m = len(tokens)
                
            c = 0
            for t in sorted(tokens, key= lambda k: tokens[k], cmp = lambda a, b: 1 if b.score > a.score else -1 ): 
                if c == m: break
                yield tokens[t]
                c += 1
    
    class CloudToken(Token):
        def __init__(self, token):
            Token.__init__(self, token[0], -1, -1, token[3])
            self.score = 0
        
    def __init__(self, tokens = {}):
        self.counted, self.tokens = 0, {}
        self.__add__(tokens);

    def tokens(self):
        for k in self.tokens: yield k

    def __radd__(self, tokens): return self.__add__(tokens)
    
    def __add__(self, tokens):
        for t in tokens:
            k = (t[0], t[3]) 
            if k in self.tokens: 
                ct = self.tokens[k]
            else:
                ct = CloudTokenSet.CloudToken(t)
                self.tokens[k] = ct
            
            ct.score = ct.score + 1
            self.counted += 1

        return self
        
    def __str__(self):
        r = [ u"30 of %d top scored terms :" % self.counted]
        for t in CloudTokenSet.TopScored(30)(self.tokens):
            r.append(t[0] + u" - " + unicode(t.score))
        return u"\n".join(r).encode('utf-8')
        

class ParsimoniusCloudTokenSet(CloudTokenSet):
    def __add__(self, tokens):
        for t in tokens:
            k = (t[0], t[3]) 
            if k in self.tokens: 
                ct = self.tokens[k]
            else:
                ct = CloudTokenSet.CloudToken(t)
                self.tokens[k] = ct
            
            ct.score = ct.score + 1
            self.counted += 1

        return self
    


sonar = SonarFileCollection()
cloud = CloudTokenSet()
c = 100
s = 0
text = None
for path in sonar.ls():
    print "Handle: " + path
    
    if text == None:
        text   = sonar.text(path)
    cloud += text.tokens()
    c-= 1
    s += len(str(text))
    if c == 0: break

print cloud
print s

