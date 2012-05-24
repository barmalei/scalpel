# startup code to point to lib.
# in general case it is not necessary to have.
# this is for demo purposes only.
import sys
sys.path.insert(0, "lib")


from ilps.tae.link.wikipedia import Wikipedia

#
#   
#
def wiki_sample1(): 
    w = Wikipedia("Wiki")
    w.languages = ["en", "nl"]
    w.db_parameters = { "db":"nenorm", 
                        "user":"wiki" , 
                        "passwd":"1cd2ddb4" , 
                        "host":"qassir.science.uva.nl" }
    w.en_base_url = "http://en.wikipedia.org/wiki/"
    w.nl_base_url = "http://nl.wikipedia.org/wiki/"
 

    print w.search("Den Haag", "nl")
    print w.search("Amsterdam", "nl")


#
#  demonstrates how to use Wiki code inilized with a config file
#
def wiki_sample2(): 
    w = Wikipedia("test_wikipedia")
    w.init_from_config("conf/local.conf")
    print w.search("Den Haag", "nl")


#
#  run sample
#
wiki_sample1()
wiki_sample2()
