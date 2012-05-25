from __future__ import with_statement

from gravity import GRAVITY_LIB_HOME
import os

class Corpora(object):
    @classmethod 
    def corpora_home(cls):
        return os.path.join(GRAVITY_LIB_HOME, "corpora")
        
