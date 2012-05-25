
import sys, os, subprocess

tae_home = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]), os.pardir, os.pardir))
py_path = os.path.join(tae_home, 'lib')
sys.path.insert(0, py_path)

from gravity.common.file.filewalker import FileWalker

python_path = "python"
if python_path: python_path = sys.executable

class TestRunner(FileWalker):
    def handle_file(self, file):
        extension = os.path.splitext(file)[1]
        if extension == '.py' and os.path.basename(file).find('test_') == 0: 
            self.run_test(file)
            return 1
        return 0

    def run_test(self, file):
        print ":: Run '%s' test case" % file
        process = subprocess.Popen("%s %s" % (python_path, file), shell=True, env = { 'PYTHONPATH':py_path })
        if process.wait() != 0:
            raise BaseException("Test '%s' failed" % file)

TestRunner(os.path.dirname(__file__)).walk()
