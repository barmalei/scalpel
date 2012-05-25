
from gravity import GRAVITY_LIB_HOME

import os

def list_module_implementations(mod_cls):
    assert mod_cls
    home = os.path.dirname(os.path.join(GRAVITY_LIB_HOME, *cls.__module__.split('.'))) 
    r = []
    for f in os.listdir(home):
        p = f if os.path.isabs(f) else os.path.join(home, f)
        if os.path.isdir(p) and os.path.basename(p)[0] != '.': r.append(os.path.basename(p)) 
    return r

def instantiate_module_implementation(cls, name, *args):
    m = cls.__module__.split('.')
    m = '.'.join(m[0:len(m)-1])
    m = __import__(m + "." + name + "." + cls.__name__.lower(), globals(), locals(), [cls.__name__], -1)
    return getattr(m, cls.__name__)(*args)

