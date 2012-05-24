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

import os, cPickle
from ilps.tae.ner.ne import JavaBasedNER


class NER(JavaBasedNER):
    def __init__(self, lang='nl', model=None):
        JavaBasedNER.__init__(self, lang, model)
 
    def callback(self, text):
        class Callback(NER.PickleCallback):
            def read(self, pipe):
                glue, tokens, pp = NER.NamedEntityGlue(), [], cPickle.load(pipe)
                for t in pp: 
                    name, tp = t[0].decode("utf-8"), self.runner.map_tag(t[3])
                    rt = glue(name, t[1], tp)
                    if rt: tokens.append(rt)
                        
                rt = glue.flush()
                if rt: tokens.append(rt)
                return tokens

        return Callback(text, self)

    def jython_tagger_listener(self):
        class JythonListener(self.class_loader.loadClass("ilps.tae.Tagger$TaggerListener")):
            def __init__(self, runner): self.result, self.runner, self.glue = [], runner, None
            def recognitionStarted(self): self.glue = NER.NamedEntityGlue()

            def recognitionEndded(self): 
                t = self.glue.flush()
                if t: self.result.append(t)
                
            def newTokenRecognized(self, text, offset, ln,tp): 
                t = self.glue(text, offset, self.runner.map_tag(tp))
                if t: self.result.append(t)

        return JythonListener(self)
    
    def home(self):
        return os.path.join(super(NER, self).home(), 'ner')

    def java_class(self):
        return "ilps.tae.ner.stanford.NER"
            
    def java_classpath(self):
        libs = super(NER, self).java_classpath()
        libs.append(os.path.join(self.home(), 'classifiers'))
        libs.append(os.path.join(self.home(), 'stanford-ner.jar'))
        return libs
      
if __name__ == '__main__':
    from ilps.tae import DEBUG_NER_TEXT
    print NER()(DEBUG_NER_TEXT)
