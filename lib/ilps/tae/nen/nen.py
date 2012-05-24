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

import re
from ilps.tae.tokenizer import Token


class NormRule(object):
    def __call__(self, text, keys, tokens):
        raise NotImplementedError()


class MatchPersonNameRule(object):
    def __init__(self):
        self.title_re       = re.compile(r'^(mr|meneer|mv|mevrouw|mrs|ms|dr|sir|lady|lord|dame|miss)\b.*\w', re.I)
        self.name_re        = re.compile(r"[A-Za-z][A-Za-z_0-9\-]+", re.I)
        self.dutch_prefixes = re.compile(r"(vanden|van|den|de|bij|der|des|voor|het|onder|ver|ter|ten|te|op|uit)\s+\w+", re.I)
    
    def __call__(self, text, keys, tokens):
        if not self._is_person(text, tokens[text]):
            return None
        
        f_name1, l_name1 = self._parse_name(text)  
        for k in keys:
            t = tokens[k]
            if self._is_person(text, t):
                f_name2, l_name2 = self._parse_name(k)
                if (f_name1 == None or f_name1 == f_name2) and (l_name1 == None or l_name1 == l_name2):
                    return k

    def _is_person(self, text, tokens):
        for t in tokens: 
            if t[3] & (Token.NE_PER | Token.NE_MISC) > 0: return True
        return False

    def _parse_name(self, name):
        name  = self._cut_title(name)
        
        m = self.dutch_prefixes.search(name)
        if m: 
            last_name  = name[m.start():]
            first_name = name[:m.start()].strip() if m.start() > 0 else None  
        else:    
            names = name.split()
            if len(names) > 1:
                first_name = names[0]
                names[0] = ''
                last_name  =  ' '.join(names).strip()
            else:
                first_name = names[0]
            
        return (first_name, last_name)
    
    def _cut_title(self, name):
        m = self.title_re.match(name)
        return name[m.end(1) + 1:] if m else name


class NEN(object):
    class TokenDictionary(dict):
        splitter_re = re.compile(r"\s+")
    
        def __init__(self, tokens):
            for t in tokens:
                w = self.splitter_re.split(t[0])
                w = ' '.join(w)
                t[0] = w
                self[w] = t
                
        def __setitem__(self, key, value):
            if key in self:
                super(self.__class__, self).__getitem__(key).append(value)
            else:
                super(self.__class__, self).__setitem__(key, [ value ])

        def move(self, src_key, dest_key):
            src_tokens  = self[src_key]
            dest_tokens = self[dest_key]
            for t in src_tokens:
                t[0] = dest_key
                dest_tokens.append(t)
            

    def __init__(self, rules = []):
        self.rules = rules

    def __call__(self, tokens):
        t_dict  = NEN.TokenDictionary(tokens)
        t_keys  = t_dict.keys()
        t_keys.sort(reverse=True)
        for rule in self.rules:
            for i in range(len(t_keys)):
                k = t_keys[i]
                r = rule(k, self._key_generator(i + 1, t_keys), t_dict)
                if r: t_dict.move(k, r)
        
        return tokens
        
    def _key_generator(self, start_i, keys):
        for i in range(start_i, len(keys), 1): yield keys[i] 
    


#m = MatchPersonNameRule()
#print m._parse_name("Karl Van de Dale")


n = NEN(rules = [ MatchPersonNameRule() ])

print n([["Van   Halen",1,1, Token.NE_PER], ["Domer Van Halen",1,1, Token.NE_PER]])

