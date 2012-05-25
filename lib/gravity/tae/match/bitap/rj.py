#!/usr/bin/env python
#       
#       Copyright 2010 Andrei <vish@gravitysoft.org>
#       
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

from gravity.common.bits import BitsWiseStorage 

#
#  Basic Rj function implementation. 
#  Rj function is bit array where every bit is used as an indication whether
#  the given pattern match the given fragment of text by j character. This
#  function is key for bitap search. Rj function defines a level of difference 
#  for two string it compares. The special thing about Rj is it is set to 1
#  for -1 character.
#
class fRj(BitsWiseStorage):
    #
    #  Alphabet for the given pattern. Special structure that accumulates
    #  all characters have been used in the given pattern and its 
    #  Rj functions. Rj function specifies how the given character matches 
    #  the pattern where it has been mentioned. 
    #
    class Alphabet(object):
        def __init__(self, pattern):
            assert pattern and len(pattern) > 0
            self._characters = frozenset(pattern)            
            self._S = {}
            self._zeroRj = fRj(pattern)
            
            m = len(pattern)
            for ch in self._characters:
                rj = fRj(pattern)
                rj.setBits(range(m), 1)
                self._S[ch] = rj(ch)    
            
            self._pattern = pattern
            
        def characters(self): return self._characters        
    
        def S(self, ch):
            # take in account if a character is not in alphabet return zero Rj function
            return self._S[ch] if ch in self._S else self._zeroRj
    
        def __str__(self):
            s = "    " +  " ".join([ ch for ch in self._characters])
            for i in range(len(self._pattern)):
                s += "\n" + self._pattern[i] + " |"
                for a in self._characters:
                    s += " " + str(self.S(a).getBit(i))             
            return s
    
    def __init__(self, pattern = None, related_rj = None):
        if related_rj: 
            if isinstance(related_rj, type): 
                self._related_rj = related_rj(pattern)
            else:                            
                self._related_rj = related_rj
        else: 
            self._related_rj = None
            
        if pattern: self.set_pattern(pattern)
            
    @property
    def related_rj(self): return self._related_rj 
        
    @property
    def pattern(self): return self._pattern
   
    def __call__(self, ch): return self.compute(ch) 

    #
    #  This is the key method which computes the next value of the Rj function
    #
    def compute(self, ch):
        r = self.getBit(-1)
        for i in range(len(self.pattern)): 
            v = int(r and self.pattern[i] == ch)
            r = self.getBit(i)  
            self.setBit(i, v)
        return self
  
    def operationsDone(self, op): return 0

    def set_pattern(self, pattern):
        assert pattern and len(pattern) > 0
        self._pattern = pattern
        BitsWiseStorage.__init__(self, len(pattern))
        if self.related_rj: self.related_rj.set_pattern(pattern)
   
    def count_related_rj(self):
        c = 0
        rj = self
        while rj.related_rj: 
            c += 1
            rj = rj.related_rj
        return c        
        
   
class fRjBase(fRj): 
    def set_pattern(self, pattern):
        super(fRjBase, self).set_pattern(pattern)
        self._alphabet = fRj.Alphabet(pattern)
       
    def alphabet(self): return self._alphabet
                
    
        
    
if __name__ == '__main__':
	pass
