from gravity.tae.match import lev_distance 
from gravity.tae import distance
from gravity.tae.match.c_lev_distance import fLevDistanceDiag
from gravity.tae.match.c_lev_distance import fLevPath


s1 = "Test Den   Haag entity"
s2 = "Test Den Haag entity"
m1 = fLevDistanceDiag(2).matrix(s1, s2, 111)
print m1.toString(s1, s2)

m2 = lev_distance.fLevDistanceDiag(2).matrix(s1, s2, 111)
print m2.toString(s1, s2)
print m1 == m2


p1_1 = fLevPath()(m1)
p1_2 = fLevPath()(m2)
print p1_1
print p1_2


p2_1 = lev_distance.fLevPath()(m1)
p2_2 = lev_distance.fLevPath()(m2)
print p2_1
print p2_2


print m2.toString(s1, s2, p1_2)

assert m1 == m2
assert p1_1 == p1_2 and p1_2 == p2_1 and p2_1 == p2_2

##    01234567890123456
s1 = "Test  amsterdamm    entity"
s2 = "Test Amsterdam entity"

print "==="*40


m = fLevDistanceDiag(24).matrix(s2, s1, 222)
print m.toString(s2, s1, fLevPath()(m))



