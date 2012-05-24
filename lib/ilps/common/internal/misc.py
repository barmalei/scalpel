#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import os, sys
from ilps import ILPS_LIB_HOME

def list_module_implementations(cls):
    home = os.path.dirname(os.path.join(ILPS_LIB_HOME, *cls.__module__.split('.'))) 
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


class ExternalTool(object):
    def home(self): 
        if  self.__module__ == '__main__':
            return os.path.join(ILPS_LIB_HOME, os.path.basename(os.path.dirname(sys.argv[0])))
        else:
            return os.path.join(ILPS_LIB_HOME, self.__module__.split('.')[-2])

    def info(self):
        return "External tool"

