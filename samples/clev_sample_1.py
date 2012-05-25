from gravity.tae.match import lev_distance 
from gravity.tae.match.c_lev_distance import fLevTextsAligner
from gravity.tae.match.c_lev_distance import fLevPath
from gravity.tae.match.c_lev_distance import fLevDistanceDiag


## Offsets:  01234567890123456789012345
s1    =     "Test  Amsterdamm    entity"  # original string 
s2    =     "Test amsterdam entity"       # processed string 
loc   =  [5, 13]                          # "Amsterdamm" entity locations in processed string 
delta = 2                                 # diagonal size is 2*delta + 1  

res = fLevTextsAligner(delta)(s1, s2, loc)
print "Location of 'Amsterdamm' entity in original string is ", res
print "Text is '%s'" % s1[res[0]:res[1]+1]


# to visualize the results build and show levenshtein matrix
# together with calculated minimal path
m = fLevDistanceDiag(2).matrix(s1, s2, 111)
print m.toString(s1, s2, fLevPath()(m))
