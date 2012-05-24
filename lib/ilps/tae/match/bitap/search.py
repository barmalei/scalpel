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

from ilps.tae.text  import fSearch
from ilps.tae.distance import fDistance
from rj_set import fRjExact

#
#  Bitap search algorithm implementation 
#
class fBitapSearch(fSearch):   
    def __init__(self, fRj = fRjExact):
        assert fRj
        self._fRj = fRj
    #
    #  The method returns tuple (offset, len) where:
    #   -- offset is an offset of found fragment of the text which matches 
    #             the given pattern
    #   -- len    is length of found fragment of text which matches the 
    #             given pattern
    #   None if there is no match has been found
    #
    def _search(self, text, pattern, offset = 0):
        m = len(pattern)
        for rj_tuple in self.fRjGenerator(text, pattern, offset):
             j, rj, prj, lb = rj_tuple[0], rj_tuple[1], None, 0
            
             #  Rj can be organized as a chain of Rj functions where every 
             #  following Rj brings more error. The code below tries to find
             #  Rj that gives the best match quality   
             while rj: 
                lb = rj.lastBit()
                if lb == 0: break
                
                prj = rj
                rj = rj.related_rj               
             
             #  Rj function says (j - m, j) characters match pattern  
             if lb: 
                #
                # calculate offset and length of the pattern found in the given text 
                # depending on Rj function has been used the found fragment length 
                # can be longer or shorter than original pattern. To decide if the 
                # fragment doesn't exact match the pattern Rj function is asked 
                # how many INSERTION and DELETION operations have been done.
                #
                ln  = m - prj.operationsDone(fDistance.DELETION) + prj.operationsDone(fDistance.INSERTION) 
                return (None, j - ln + 1, ln, 0)
        return None 
 
    #
    #  The generator generates tuples that contains two elements:  
    #    -- j  :  index of text character for which Rj function has been calculated
    #    -- Rj :  Rj function (pattern bits) calculated for j character of the text 
    #             and the given pattern 
    #
    def fRjGenerator(self, text, pattern, offset = 0):
        # instantiate Rj function by class reference
        if isinstance(self._fRj, type): 
            rj = self._fRj(pattern)
        else:
            rj = self._fRj
            rj.set_pattern(pattern)
            
        # yield initial Rj function state
        yield (-1, rj)
        
        # yield Rj for all character of the given text
        for j in range(offset, len(text)): yield (j, rj(text[j]))


    def debug(self, text, pattern):
        fun = self._fRj
        
        h_line = "-"*(len(pattern)*2 + 12)
        if isinstance(fun, type): name = fun.__name__
        else:                     name = fun.__class__.__name__
        s  = "\n" + name + ":\n"
    
        showheader = True
        for rj_tuple in self.fRjGenerator(text, pattern): 
            if showheader:
                showheader = False
                crj        = rj_tuple[1].count_related_rj() + 1
                for i in range(crj): s += (h_line )
                s += "\n"
                for i in range(crj): s += ("  | - " + " ".join(pattern) + " |   ")
                s += "\n"
                for i in range(crj): s += (h_line)
            s = self._str_rj(text, rj_tuple[1], rj_tuple[0], s) + " |  R(%s)" % rj_tuple[0]

        return s        
          
    def _str_rj(self, text, rj, j, s): 
        if rj.related_rj: s = self._str_rj(text, rj.related_rj, j, s) + " |   "       
        else: s += "\n"        
        
        if j == -1: s += "- | " + str(rj)
        else:       s += text[j] + " | " +  str(rj)              
        return s      
  
if __name__ == '__main__':
	pass
