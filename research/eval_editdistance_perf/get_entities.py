
import os, codecs, time

from ilps.common.xml.grabber import XmlElementsCollector, XmlGrabber, XmlPathFilter 

from ilps.tae.ner.tnt.ner import NER
from ilps.tae.ner.tnt.ner import fEntityLocator

from ilps.tae.match.lev_distance import fClassicalLevenshteinDistance, fLevenshteinDistance, fLevenshteinPath, fLevenshteinDistance2


from ilps.tae.match.distance import  fDiagDistance, fDistancePath, fMinPath
from ilps.tae.match.distance_matrix import UprightDistanceMatrix, UprightSubsetDistanceMatrix, DistanceMatrix, HybridSubsetDistanceMatrix 
from ilps.tae.match.bitap.distance import fBitapDistance
from ilps.tae.match.bitap.rj_set import fRjExact, fRjSubstitute, fRjInsert, fRjDelete, fRjKError
from ilps.tae.match.bitap.rj import fRj

data_dir = os.path.join(os.path.dirname(__file__), "data")


def measure(f):
    def ff(s=None):
        start_time = time.time() 
        f(s)
        print "'%s' elapsed time : " % f.__name__, (time.time() - start_time)
    
    return ff

def fetch_text(xml_file):
    assert os.path.exists(xml_file)
        
    output_file_name = xml_file + ".txt"
    with codecs.open(output_file_name, 'w', "utf-8") as f:
        def listener(path, element, filter):
            f.write(element.text)
        
        grabber = XmlGrabber()
        grabber.addXmlPathFilter(XmlPathFilter([ ".*/samenvatting"  ]))
        grabber.grab(xml_file, listener)

    return output_file_name


def prepare_data(folder):
    assert os.path.isdir(folder)
    res = []    
    for path in os.listdir(folder):
        path = os.path.join(folder, path)
        if  os.path.isfile(path) and path.find(".txt") < 0: 
            res.append(fetch_text(path))    
    return res
    
    
def read_file(path):
    assert os.path.isfile(path)
    with codecs.open(path, 'r', "utf-8") as f:
        return f.read()         
  
 
#
#  fietstas implementation, just for test purposes
#
def compute_edit_distance(source_text, target_text):
    """Compute edit distance between source text and target text"""
    m, n = len(source_text), len(target_text)
    d = [range(n + 1)]
    d += [[i] for i in range(1, m + 1)]

    for i in range(0, m):
        for j in range(0, n):
            cost = 1
            if source_text[i] == target_text[j]: cost = 0
            d[i + 1].append(min(d[i][j + 1] + 1, #deletion
                            d[i + 1][j] + 1, #insertion
                            d[i][j] + cost) #substitution
                            )
    return d[m][n]


@measure
def test_LVD(s):
    print fLevenshteinDistance()(s, s)

@measure
def test_CLVD(s):
    print fClassicalLevenshteinDistance()(s, s)

@measure
def test_FLVD(s):
    print compute_edit_distance(s, s)

@measure
def test_LVD2(s):
    print fLevenshteinDistance2()(s, s)

@measure
def test_DLVD(s):
    print fDiagDistance(100)(s, s)



def test_bitapdistance(s):
    start_time = time.time() 
    print fBitapDistance(fRjInsert)(s, s)
    print "Bitap distance done:", (time.time() - start_time)

    
def test_distances(s):
    test_LVD(s)
    test_CLVD(s)
    test_FLVD(s)
    test_bitapdistance(s)


def small_fLoc_test1():
    s1 = "la bla  Amsterdam test" 
    s2 = "la/O bla/O Amsterdam/LOC test/O"
    f = fEntityLocator()
    print f(s1, s2, [ ["Amsterdam", 11, -1, 1] ])
    
def small_fLoc_test2():
    s1 = "la bla  Amsterdam test" 
    s2 = "la Amsterdam test"
    f = fEntityLocator()
    print f(s1, s2, [ ["Amsterdam", 3, -1, 1] ])
    

def small_fLoc_test3():
    s1 = ", ?Van Daal ," 
    tnt = NER() 
    ee = tnt(s1)   
    print ee
    for e in ee:
        print e[0], e[1], e[2], "  : ", s1[e[1]: e[2] + 1]
        #print "Entity: ", s1[e[1]: e[2] + 1] 

    m = DistanceMatrix(fLevenshteinDistance, s1, tnt._processed_text)
    p = fMinPath()(m)

    print m.toString(p)


def general_test1():
    res = prepare_data(data_dir)
    for file in res:
        print "::: Handle file: ", file
        original_text = read_file(file)
        ner = NER.ner('tnt')()
        entities       = ner(original_text)
        processed_text = ner._processed_text
        
        for e in entities:
            print "Entity: ", e[0], "  ", original_text[e[1]: e[2] + 1] 
    


@measure
def levdiag_test0():
    #s = read_file(data_dir +  "/73632.agg.txt")  # 14kb file
    s = read_file(data_dir +  "/73621.agg.txt")  # 900 bytes file
    for i in fDiagDistance(100).__generator__(s, s): pass
    
    #fDiagDistance()(s, s)

@measure
def levdiag_test1():
    s = read_file(data_dir +  "/73632.agg.txt")  # 14kb file
    #s = read_file(data_dir +  "/73621.agg.txt")  # 900 bytes file
    print len(s)
    DistanceMatrix(fDiagDistance(100), s, s, 1000)
    

@measure
def levdiag_test2():
    s1 = s2 = read_file(data_dir +  "/73632.agg.txt")  # 14kb file
    #s1 = read_file(data_dir +  "/73621.agg.txt")  # 900 bytes file
    #s2 = read_file(data_dir +  "/73691.agg.txt")  # 900 bytes file
    m = SubsetDistanceMatrix(fDiagDistance(100), s1, s2, 1000)
    #for e in fMinPath()(m): 
     #   print m.get(e[0], e[1])


@measure
def levdiag_test3():
    s = read_file(data_dir +  "/73632.agg.txt")  # 14kb file
    #s = read_file(data_dir +  "/73621.agg.txt")  # 900 bytes file
    print len(s)
    ArrayDistanceMatrix(fDiagDistance(100), s, s, 1000)

    
    #for e in fDiagDistance(100).__generator__(s, s): pass
    #print e


@measure
def levdiag_test4():
    s1 = s2 = read_file(data_dir +  "/73632.agg.txt")  # 14kb file
    #s1 = read_file(data_dir +  "/73621.agg.txt")  # 900 bytes file
    #s2 = read_file(data_dir +  "/73691.agg.txt")  # 900 bytes file
    m = ArraySubsetDistanceMatrix(fDiagDistance(100), s1, s2)
    #for e in fMinPath()(m): 
     #   print m.get(e[0], e[1])
    
    
    #for e in fDiagDistance(100).__generator__(s, s): pass
    #print e


@measure
def levdiag_test5():
    s1 = s2 = read_file(data_dir +  "/73632.agg.txt")  # 14kb file
    #s1 = read_file(data_dir +  "/73621.agg.txt")  # 900 bytes file
    #s2 = read_file(data_dir +  "/73691.agg.txt")  # 900 bytes file
    m = HybridSubsetDistanceMatrix(fDiagDistance(100), s1, s2, 100000000)
    
    #for e in fMinPath()(m): 
     #   print m.get(e[0], e[1])



#small_fLoc_test1()
#small_fLoc_test2()
#small_fLoc_test3()

#general_test()

#lev_test()
#levdiag_test0()
#levdiag_test2()
#levdiag_test1()
#levdiag_test3()
#levdiag_test4()
#levdiag_test5()


t1, t2 = "asdsdsa", "ssasasas"
m = DistanceMatrix(fLevenshteinDistance2, t1, t2)
print m.toString(t1, t2)


t1, t2 = "asdsdsa", "ssasasas"
m = DistanceMatrix(fLevenshteinDistance, t1, t2)
print m.toString(t1, t2)

t1, t2 = "asdsdsa", "ssasasas"
m = DistanceMatrix(fClassicalLevenshteinDistance, t1, t2)
print m.toString(t1, t2)

t1, t2 = "asdsdsa", "ssasasas"
m = DistanceMatrix(fDiagDistance(6), t1, t2, 111)
print m.toString(t1, t2)

s = s1 = s2 = read_file(data_dir +  "/73632.agg.txt")
test_LVD2(s)
test_LVD(s)

#test_FLVD(s)

#levdiag_test1()
#levdiag_test4()
#levdiag_test5()

#s1 = s2 = read_file(data_dir +  "/73632.agg.txt")
#test_DLVD(s1)
