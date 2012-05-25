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

from gravity.common.internal.misc import list_module_implementations, instantiate_module_implementation
import gravity.tae.stemmer.stemmer 

class Stemmer(object):
    def __init__(self, lang = "en"):
        assert lang
        self.lang = lang

    def info(self): raise NotImplementedError()

    @classmethod
    def list(cls):
        return list_module_implementations(cls)

    @classmethod
    def stemmer(cls, name, *args):
        return instantiate_module_implementation(cls, name, *args)

    