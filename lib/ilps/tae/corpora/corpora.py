from __future__ import with_statement

from ilps import ILPS_LIB_HOME
import os

class Corpora(object):
    @classmethod 
    def corpora_home(cls):
        return os.path.join(ILPS_LIB_HOME, "corpora")
        
