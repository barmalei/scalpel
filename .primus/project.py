from primus.artifactcore  import DoGroup, Project
from primus.repartifact   import DownloadArchivedFiles, DownloadFile
from primus.fileartifact  import RunMakefile
from primus.pyartifact    import SetupPythonPackage, CheckPythonEnvironment, ValidatePythonCode, RunPythonCode
from primus.javaartifact  import CompileJavaCode, RunJUnit


#  Repo URL
REPO_URL = 'http://ilps.science.uva.nl/thirdparty-packages'

#  Deployment configuration
PROJECT = Project("TAE",
      [ 
        DoGroup("Test environment:", 
        [
            CheckPythonEnvironment(required_version=(2,5)),
            ValidatePythonCode('lib/ilps')         
        ]),
    
        DoGroup("Download third party software:",  
        [
          DownloadArchivedFiles('lib/quartz/ner', "%s/quartz/quartz-ner-1.0.0.zip" % REPO_URL),
          DownloadArchivedFiles('lib/quartz/pos', "%s/quartz/quartz-pos-1.0.0.zip" % REPO_URL),
          DownloadArchivedFiles('lib/lingpipe', "%s/lingpipe/lingpipe-4.0.0.zip" % REPO_URL),
          DownloadArchivedFiles('lib/stanford/pos', "%s/stanford/stanford-pos-3.0.1.zip" % REPO_URL),
          DownloadArchivedFiles('lib/ilps/tae/ner/lingpipe', "%s/lingpipe/nl.conll.2002-4.0.0.hmm.zip" % REPO_URL, do_if_absent = 'nl.conll.2002-4.0.0.hmm'),
          DownloadArchivedFiles('lib/ilps/tae/ner/lingpipe', "%s/lingpipe/nl.conll.2002-4.0.0.lm.zip"  % REPO_URL, do_if_absent = 'nl.conll.2002-4.0.0.lm'),
          DownloadArchivedFiles('lib/ilps/tae/ner/lingpipe', "%s/lingpipe/en.conll.2002-4.0.0.hmm.zip" % REPO_URL, do_if_absent = 'en.conll.2002-4.0.0.hmm'),
          DownloadArchivedFiles('lib/ilps/tae/ner/lingpipe', "%s/lingpipe/en.conll.2002-4.0.0.lm.zip"  % REPO_URL, do_if_absent = 'en.conll.2002-4.0.0.lm'),
          DownloadArchivedFiles('lib/ilps/tae/ner/lingpipe', "%s/lingpipe/es.conll.2002-4.0.0.hmm.zip" % REPO_URL, do_if_absent = 'es.conll.2002-4.0.0.hmm'),
          DownloadArchivedFiles('lib/ilps/tae/ner/lingpipe', "%s/lingpipe/es.conll.2002-4.0.0.lm.zip"  % REPO_URL, do_if_absent = 'es.conll.2002-4.0.0.lm'),
          #DownloadArchivedFiles('lib/corpora/sonar', "%s/corpora/sonar/sonar.zip" % REPO_URL),
          DownloadArchivedFiles('lib/stanford/ner', "%s/stanford/stanford-ner-1.2.3.zip" % REPO_URL),
          DownloadFile('lib/ilps/tae/ner/stanford', "%s/stanford/conll.2002.nl.ser-1.2.3.gz" % REPO_URL),
          DownloadArchivedFiles('lib/stanford_old/ner', "%s/stanford/stanford-ner-1.1.1.zip" % REPO_URL),
          DownloadFile('lib/ilps/tae/ner/stanford_old', "%s/stanford/conll.2002.nl.ser-1.1.1.gz" % REPO_URL),
          DownloadArchivedFiles('lib/lbj', "%s/lbj/lbj-1.2.0.zip" % REPO_URL),
          DownloadArchivedFiles('lib/corpora/CoNLL/2000', "%s/corpora/conll/conll-2000.zip" % REPO_URL),
          DownloadArchivedFiles('lib/corpora/CoNLL/2002', "%s/corpora/conll/conll-2002.zip" % REPO_URL),
          DownloadArchivedFiles('lib/corpora/CoNLL/2003', "%s/corpora/conll/conll-2003.zip" % REPO_URL),
          DownloadArchivedFiles('lib/corpora/ILPS', "%s/corpora/ilps.zip" % REPO_URL),
          DownloadArchivedFiles('lib/snowball', "%s/snowball/stemmer-1.1.0.zip" % REPO_URL),
          DownloadFile('lib/junit', "%s/junit/junit-4.8.2.jar" % REPO_URL),
          DownloadArchivedFiles('lib/jython', "%s/jython/jython-2.5.2.zip" % REPO_URL)
        ]),
        
        DoGroup("Build binary modules:",
        [
            SetupPythonPackage('lib/ilps/tae/match'),
            SetupPythonPackage('lib/snowball', lib = 'lib/ilps/tae/stemmer/snowball/so')
        ]),
        
        DoGroup("Compile Java code:",
        [ 
            CompileJavaCode('lib/ilps/common/*.java'),
            CompileJavaCode('test/ilps/common/TestCustomClassLoader.java', destination='test', classpath = ['lib', 'lib/junit/junit-4.8.2.jar']),
            CompileJavaCode('lib/ilps/tae/ner/*.java'),
            CompileJavaCode('lib/ilps/tae/pos/*.java'),
            CompileJavaCode('lib/ilps/tae/pos/stanford/*.java', classpath = [ 'lib', 'lib/stanford/pos/stanford-postagger.jar']),
            CompileJavaCode('lib/ilps/tae/ner/stanford/*.java', classpath = [ 'lib', 'lib/stanford/ner/stanford-ner.jar']),
            CompileJavaCode('lib/ilps/tae/ner/stanford_old/*.java', classpath = [ 'lib', 'lib/stanford_old/ner/stanford-ner.jar']),
            CompileJavaCode('lib/ilps/tae/ner/lingpipe/*.java', classpath = [ 'lib', 'lib/lingpipe/lib']),
            CompileJavaCode('lib/ilps/tae/ner/lbj/*.java', classpath = [ 'lib', 'lib/lbj/LBJ2Library.jar', 'lib/lbj/LBJ2', 'lib/lbj/bin'])
        ]),
        
        DoGroup("Configure TNT NER/POS:",
        [
            RunMakefile('lib/quartz/ner/ner'),
            RunMakefile('lib/quartz/pos')
        ]),
        
        RunPythonCode("test/tests.py"),
        RunJUnit("test/ilps/common/TestCustomClassLoader.class", classpath = ['test', 'lib', 'lib/junit/junit-4.8.2.jar'])
]) 
