
import os
from subprocess import Popen, PIPE


class PipedProcess(object):
    class Callback(object):
        def send(self, pipe): raise NotImplementedError()
        def read(self, pipe): raise NotImplementedError()

    def __init__(self, process):
        assert process
        self.process  = process
        
    def __call__(self, call_back, params = None):
        assert call_back

        cmd = self.command_line()
        if params and len(params) > 0:
            if isinstance(params, dict):
                a = [ k + "=" + v for k, v in params.iteritems() ]
                cmd += " " +  " ".join(a)
            else: 
                cmd += ' ' + ' '.join(params)
        
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, close_fds=True)

        result = None
        try:
            if hasattr(call_back, 'send'): call_back.send(p.stdin)
            p.stdin.close()
        
            if  hasattr(call_back, 'read'): result = call_back.read(p.stdout)
            p.stdout.close()
        finally:
            try:
                p.stdin.close()
                p.stdout.close()
            except: pass

        ret_code = int(p.wait())
        if ret_code != 0: 
            raise BaseException("Unexpected error %s" % str(ret_code))

        return result

    def command_line(self): return self.process
    

class JavaClassRunner(PipedProcess):    
    def __init__(self, class_name):
        assert class_name
        PipedProcess.__init__(self, 'java')
        self.options, self.classpath, self.class_name = [], [], class_name
    
    def command_line(self):
        # form command line
        cmd = "".join([super(JavaClassRunner, self).command_line(), " ", " ".join(self.options)])
        if len(self.classpath) > 0:
            cmd = "".join([cmd,  " -cp ",  self._class_path()])

        return cmd + " " + self.class_name
    
    def _class_path(self):
        if len(self.classpath) > 0:
            classpath = []
            for path in self.classpath:
                if not os.path.exists(path):
                    raise BaseException("Invalid classpath item '%s'" % path)
                
                if os.path.isdir(path):
                    for jar in self._collect_jars(path): classpath.append(jar)
                else: 
                    classpath.append(path)
                    
            return ":".join(classpath)

    def _collect_jars(self, path):
        jars = [ path ]
        for p in os.listdir(path):
            name = p
            p = os.path.join(path, p)
            if os.path.isfile(p) and len(name) > 4 and name.find('.jar') == len(name)- 4: jars.append(p)
        return jars
        
