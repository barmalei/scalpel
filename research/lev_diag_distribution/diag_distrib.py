
import os, codecs, time, re

from gravity.common.xml.grabber import XmlElementsCollector, XmlGrabber, XmlPathFilter 

from gravity.tae.ner.tnt.ner import NER

from gravity.tae.match.lev_distance import fClassicalLevDistance, fLevDistance, fLevPath, fLevDistance2

from gravity.tae.distance import fDistancePath, fMinPath
from gravity.tae.match.distance_matrix import UprightDistanceMatrix, UprightSubsetDistanceMatrix, DistanceMatrix, HybridSubsetDistanceMatrix 
from gravity.tae.match.bitap.distance import fBitapDistance
from gravity.tae.match.bitap.rj_set import fRjExact, fRjSubstitute, fRjInsert, fRjDelete, fRjKError
from gravity.tae.match.bitap.rj import fRj

data_dir = os.path.join(os.path.dirname(__file__), "data")
   
def read_file(path):
    assert os.path.isfile(path)
    with codecs.open(path, 'r', "utf-8") as f:
        return f.read()  

def gen_string_pairs(folder1, folder2):
    folder1 = os.path.join(data_dir, folder1)
    folder2 = os.path.join(data_dir, folder2)
   
    assert os.path.exists(folder1) and os.path.exists(folder2)
 
    collection1 = { }
    for name in os.listdir(folder1):
        path = os.path.join(folder1, name)
        key = name.split('.')[0]
        collection1[key] = path 

    collection2 = { }
    for name in os.listdir(folder2):
        path = os.path.join(folder2, name)
        key = name.split('.')[0]
        collection2[key] = path 

    for key in collection1:
        yield (read_file(collection1[key]), read_file(collection2[key]), collection1[key], collection2[key])


def step1_fetch_text(folder):
    def fetch_text(xml_file):
        assert os.path.exists(xml_file)            
        def listener(path, element, filter):
            listener.text += element.text

        listener.text = ''            
        grabber = XmlGrabber()
        grabber.addXmlElementFilter(XmlPathFilter([ ".*/samenvatting", ".*/beschrijving", ".*/annotatie"]))
        grabber.grab(xml_file, listener)

        return listener.text
        
    assert os.path.isdir(folder)
 
    res = []    
    for name in os.listdir(folder):
        
        path = os.path.join(folder, name)
        if os.path.isfile(path) and name.find(".xml") == len(name) - 4: 
            print "::  Fetch text from '%s'" % name

            text = fetch_text(path)
            output_file_name = os.path.join(data_dir, 'txt', name + ".txt")
             
            if len(text) < 50:
                print "!!  Not enough information found in '%s' (%d bytes) XML file." % (name, len(text))
                continue
             
            with codecs.open(output_file_name, 'w', "utf-8") as f: 
                f.write(text)
           
    
def step2_run_tnt(folder):
    def tnt(txt_file):
        s = ''
        with codecs.open(txt_file, 'r', "utf-8") as f: s = f.read()         
        tnt = NER() 
        res = tnt(s)   
   
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if os.path.isfile(path) and name.find(".txt") == len(name) - 4: 
            print "::  TNT text from '%s'" % name

            text = tnt(path)
            output_file_name = os.path.join(data_dir, 'tnt', name + ".tnt")
            with codecs.open(output_file_name, 'w', "utf-8") as f: 
                f.write(text)


def step3_calc_lev_distance():
    for s in gen_string_pairs("cleaned-tnt", "txt"):
        d = fLevDistance2()(s[0], s[1])
        print "Lev distance [", os.path.basename(s[2]), "(", len(s[0]),"b),",  os.path.basename(s[3]),"(", len(s[1]),")] = ", d 
        
        
def step4_calc_minpath():
    for s in gen_string_pairs("tnt", "txt"):
        m = UprightDistanceMatrix()
        fLevDistance2().fill_matrix(s[0], s[1], m)
        print fMinPath()(m)
        

def step5_calc_minpath_dt(p_txt_folder = 'tnt', o_txt_folder = 'txt', size_limit = -1):
    res1 = []
    res2 = []
    skipped = [] 
    
    print ":: Calculate minimal path deviation ." 
    print "     :: processed text folder:", p_txt_folder 
    print "     :: original  text folder:", o_txt_folder
    print "-"*64
    print "   Deviation   | Text1 size | Text2 size | Text diff  | Distance | "
    print "-"*64
    for s in gen_string_pairs(p_txt_folder, o_txt_folder):
        if size_limit > 0 and (len(s[1]) >  size_limit or len(s[0]) > size_limit): 
            skipped.append(os.path.basename(s[0]))
            continue
        
        m = UprightDistanceMatrix()
        fLevDistance2().fill_matrix(s[0], s[1], m)
        p = fMinPath()(m)
        #p = fLevPath(insPriority = 1)(m)
        
        i = 0 
        mdt1 = mdt2 = 0
        for col in range(m.cols - 1, -1, -1):       
            arow = (col * m.rows) // m.cols
            while i < len(p) and p[i][1] == col:
                dt = arow - p[i][0]
                if dt < 0:
                    if dt < mdt2: mdt2 = dt
                else:
                    if dt > mdt1: mdt1 = dt
                i += 1

        res1.append(mdt1)
        res2.append(mdt2)

        print " [%4d ..%3d] " % (mdt2, mdt1), "|   %6d  " % len(s[0]),  "|  %6d  " % len(s[1]), " |   %3d    " %  (len(s[0]) - len(s[1])), " |   %3d   " % m.get(m.rows-1, m.cols-1), "| %s " % os.path.basename(s[3])  

    res1.sort()
    res2.sort()
    print "=" * 52
    print " Maximal deviation = [", res2[0], " .. ", res1[len(res1) - 1], "]" 
    print "=" * 52
    

def step6_cleantnt_txt():

    rs = re.compile('/[A-Z0]+', re.U)
    output_folder = os.path.join(data_dir, "cleaned-tnt")
    input_folder  = os.path.join(data_dir, "tnt")

    for name in os.listdir(input_folder):
        path = os.path.join(input_folder, name)
        if os.path.isfile(path): 
            with codecs.open(path, 'r', "utf-8") as f: 
                data = ''.join(rs.split(f.read()))

            print ":: cleanup TNT annotations: ", name
           
            output_file_name = os.path.join(output_folder, name + ".cln")
            with codecs.open(output_file_name, 'w', "utf-8") as f: 
                f.write(data)
    


def prepare_data():
    step1_fetch_text(os.path.join(data_dir, "xml"))
    step2_run_tnt(os.path.join(data_dir, "txt"))
    step6_cleantnt_txt()
    


t = time.time()

#prepare_data()


#step1_fetch_text(os.path.join(data_dir, "xml"))
#step2_run_tnt(os.path.join(data_dir, "txt"))
#step3_calc_lev_distance()
#step4_calc_minpath()
#step5_calc_minpath_dt()
#step6_cleantnt_txt()
#step5_calc_minpath_dt("cleaned-tnt", "txt", size_limit=1000)



from gravity.tae.match.lev_distance import  fLevDistanceDiag
#s1 = "Song about   Alice dream"
#s2 = "Song al?ce dream" 

s1 = "  abc d dfg  rer klm"
s2 = "abc dfg  klm" 


m = DistanceMatrix(111)
#fLevDistanceDiag(1).fill_matrix(s2, s1, m)
fLevDistance().fill_matrix(s2, s1, m)
print m.toString(s2, s1, fMinPath()(m))


print "Elapsed time: ", (time.time()  - t)
