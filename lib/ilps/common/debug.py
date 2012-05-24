"""Misc functions for debugging"""

import re

def print_r(obj, visited_ids=None, prefix=''):
    """Recursively print out any python value. 

    'obj' - value to print; it's the only parameter users should supply.
    """

    if visited_ids is None:
        visited_ids = set()

    try:
        classname = re.sub('.*\.|\'>', '', str(obj.__class__))
    except AttributeError:
        classname = ""
            
    sub_prefix = prefix + '    '
    
    if obj is None:
        print 'None'
        return
    elif isinstance(obj, int):
        print str(obj)
        return
    elif isinstance(obj, basestring):
        # strings are printed without end-of-lines
        print obj.replace('\n', ' ').encode("utf-8")
        return

    if id(obj) in visited_ids:
        print "%s @ %s {...}" % (classname, hex(id(obj)))
        return

    visited_ids.add(id(obj))    
        
    if isinstance(obj, list):
        print '['
        for elem in obj:
            print sub_prefix,
            print_r(elem, visited_ids, sub_prefix)
        print prefix, ']'
    elif isinstance(obj, tuple):
        print '('
        for elem in obj:
            print sub_prefix,
            print_r(elem, visited_ids, sub_prefix)
        print prefix, ')'
    elif isinstance(obj, set):
        print 'set('
        for elem in obj:
            print sub_prefix,
            print_r(elem, visited_ids, sub_prefix)
        print prefix, ')'
    elif isinstance(obj, dict):
        print '{'
        for name, val in obj.iteritems():
            print sub_prefix, name, ':',
            print_r(val, visited_ids, sub_prefix)
        print prefix, '}'
    elif hasattr(obj, '__dict__'):        
        print "%s @ %s {" % (classname, hex(id(obj)))
        for attr in obj.__dict__:
            val = obj.__dict__[attr]
            print  sub_prefix, attr, '=', 
            print_r(val, visited_ids, sub_prefix)
        print prefix, '}'
    else:
        print str(obj)    

