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

import ConfigParser

class Configuration(ConfigParser.ConfigParser, object):
    INHERIT_KEY = "__inherit__"
    
    def has_inheritance(self, section):
        return super(Configuration, self).has_option(section, Configuration.INHERIT_KEY)
        
    def inherit_from(self, section):
        return super(Configuration, self).get(section, Configuration.INHERIT_KEY).strip()
        
    def has_option(self, section, option):
        if super(Configuration, self).has_option(section, option):
            return True
        
        if self.has_inheritance(section):
            return self.has_option(self.inherit_from(section), option)
        return False    

    def options(self, section):
        o = super(Configuration, self).options(section)
        
        if self.has_inheritance(section):
            o.remove(Configuration.INHERIT_KEY)
            o.extend([e for e in self.options(self.inherit_from(section)) if e not in o])
        return o

    def items(self, section):
        i = super(Configuration, self).items(section)
        
        if self.has_inheritance(section):
            i  = [e for e in i if e[0] != Configuration.INHERIT_KEY]
            ii = self.items(self.inherit_from(section))
            def f(e): 
                for ee in i: 
                    if ee[0] == e[0]: return False
                return True
            i.extend(filter(f, ii))     
        return i

    def get(self, section, option):
        if self.has_inheritance(section) and not super(Configuration, self).has_option(section, option):
            val = self.get(self.inherit_from(section), option)
        else:
            val = super(Configuration, self).get(section, option)
          
        if val:
            sval = val.strip()
            if len(sval) > 3 and sval[0] == '%' and sval[1] == '[':
                i = sval.find(']') 
                if i < 0: raise BaseException()
                j = sval.find(":", 2)
                if j > 0 and j < i:
                    r_section = sval[2:j]
                    r_option  = sval[j+1:i]
                    r_val = super(Configuration, self).get(r_section, r_option)
                    val = "".join([r_val, val[i+1:]]) 
                    self.set(section, option, val)     
                
        return val       
            
    def set(self, section, option, value):
        return super(Configuration, self).set(section, option, value)
       
    def remove_section(self, section):
        raise NotImplementedError()

