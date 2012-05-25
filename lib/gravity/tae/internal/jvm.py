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

import os, cPickle, sys

from gravity import GRAVITY_LIB_HOME
from gravity.common.internal.misc import ExternalTool
from gravity.common.process import JavaClassRunner
from gravity.tae.tokenizer  import Tokenizer


class JavaBasedTokenizer(ExternalTool, Tokenizer):
    class PickleCallback(JavaClassRunner.Callback):
        def __init__(self, text, runner):
            assert text and runner
            self.text, self.runner = text, runner

        def read(self, pipe):
            tokens, runner = cPickle.load(pipe), self.runner
            for t in tokens: t[3], t[0] = runner.map_tag(t[3]), t[0].decode("utf-8")
            return tokens

        def send(self, pipe):
            pipe.write(unicode(self.text).encode("utf-8"))

    def __init__(self, lang = 'nl'):
        Tokenizer.__init__(self, lang)
    
        self.memory, self.tags_map = "-mx512M", {}
        self.class_loader = self.ner_instance = None
        
        # test wheher tokenizer has been started under Jython
        try:
            from java.lang import Class
            self.class_loader = Class.forName("gravity.common.CustomClassLoader")(self.java_classpath())
        except: pass

    def map_tag(self, tag):
        return self.tags_map[tag] if tag in self.tags_map else None

    def _tokenize(self, text):
        if self.class_loader:
            if self.ner_instance == None:  
                self.ner_instance = self.class_loader.loadClass(self.java_class())(self.jython_parameters())
            
            l = self.jython_tagger_listener()
            self.ner_instance.tag(text, l);
            return l.result
        else:
            callback = self.callback(text)
            java_runner = JavaClassRunner(self.java_class())
            java_runner.options   = self.java_options() 
            java_runner.classpath = self.java_classpath()
            return java_runner(callback, self.parameters())

    def jython_tagger_listener(self):
        class JythonListener(self.class_loader.loadClass("gravity.tae.Tagger$TaggerListener")):
            def __init__(self, runner): self.result, self.runner = [], runner
            def recognitionStarted(self): pass
            def recognitionEndded(self): pass
            def newTokenRecognized(self, text, offset, ln, tp): 
                self.result.append([text, offset, ln, self.runner.map_tag(tp)])
            
        return JythonListener(self)

    def callback(self, text):
        return JavaBasedTokenizer.PickleCallback(text, self)

    def java_classpath(self):
        return [ GRAVITY_LIB_HOME  ]

    def java_class(self):
        raise NotImplementedError()

    def java_options(self): 
        return [ self.memory ]

    def jython_parameters(self):
        from java.util import Properties
        params = self.parameters()
        props  = Properties()
        for k in params: props.setProperty(k, params[k])
        return props

    def parameters(self): 
        return { "mode":"python", "lang": self.lang }

    def info(self):
        return "Java external tool"


class JavaBasedTagger(JavaBasedTokenizer):
    def __init__(self, lang='nl', model=None):
        JavaBasedTokenizer.__init__(self, lang)
        self.model = model

    def parameters(self):
        p = super(JavaBasedTagger, self).parameters()
        if self.model: p["model"] = self.model
        return p

