
import re
from ilps.tae.tokenizer import TokenSet


DUTCH_STOP_WORDS = [ 'aan', 'af', 'al', 'alles', 'als', 'altijd', 'andere', 'ben', 'bij', 'daar', 'dan', 'dat', 'de', 'der', 
                     'deze', 'die', 'dit', 'doch', 'doen', 'door', 'dus', 'een', 'eens', 'en', 'er', 'ge', 'geen', 'geweest',
                     'haar', 'had', 'heb', 'hebben', 'heeft', 'hem', 'het', 'hier', 'hij', 'hoe', 'hun', 'iemand', 'iets',
                     'ik', 'in', 'is', 'ja', 'je', 'kan', 'kon', 'kunnen', 'maar', 'me', 'meer', 'men', 'met', 'mij', 'mijn',
                     'moet', 'na', 'naar', 'niet', 'niets', 'nog', 'nu', 'of', 'om', 'omdat', 'ons', 'onze', 'ook', 'op',
                     'over', 'reeds', 'te', 'tegen', 'toch', 'toen', 'tot', 'u', 'uit', 'uw', 'van', 'veel', 'voor', 'want',
                     'waren', 'was', 'wat', 'we', 'wel', 'werd', 'wezen', 'wie', 'wij', 'wil', 'worden', 'zal', 'ze',
                     'zei', 'zelf', 'zich', 'zij', 'zijn', 'zo', 'zonder', 'zou' ]
        


ENGLISH_STOP_WORDS = [ 'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and',
                       'any', 'are', 'aren', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below',
                       'between', 'both', 'but', 'by', 'can', 'cannot', 'could', 'couldn','d', 'did', 'didn','do', 
                       'does', 'doesn', 'doing','don', 'down','during','each','few','for','from','further',
                       'had','hadn','has','hasn','have','haven','having','he','her','here','hers','herself',
                       'him','himself','his','how','i','if','in','into','is','isn','it','its','itself',
                       'let','ll','m','me','more','most','mustn','my','myself','no','nor','not','of',
                       'off','on','once','only','or','other','ought','our','ours','ourselves','out','over',
                       'own','re','s','same','shan','she','should','shouldn','so','some','such','t',
                       'than','that','the','their','theirs','them','themselves','then','there','these',
                       'they','this','those','through','to','too','under','until','up','ve','very','was',
                       'wasn','we','were','weren','what','when','where','which','while','who','whom','why',
                       'with','won','would','wouldn','you','your','yours','yourself','yourselves' ]


class SkipStopWords(TokenSet.Match):
    def __init__(self, stop_words = ENGLISH_STOP_WORDS, mask = re.compile(r"^[a-z]$", re.U | re.I)):
        assert stop_words
        self.stop_words, self.mask = stop_words, mask
        
    def match(self, t): 
        r = (t[0].lower() in self.stop_words) or (self.mask and self.mask.match(t[0])) 
        return not r


if __name__ == "__main__":
    from ilps.tae.tokenizer import WordTokenizer
    txt = "Andrei cannot drive a car if he has more than 0.5 pro-mile of alcohol !"
    for t in TokenSet(WordTokenizer()(txt)).tokens(SkipStopWords()):
        print t

