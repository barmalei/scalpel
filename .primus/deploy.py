#       
#       Copyright 2011 Andrei <vish@gravitysoft.org>
#       
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

from __future__ import with_statement 
import sys, os, subprocess, urllib2, shutil


#  Required package
DOWNLOAD_PRIMUS = True
PACKAGE   = 'primus-1.4.1.zip'
REPO_URLS = [ 'http://ilps.science.uva.nl/thirdparty-packages/primus/%s' % (PACKAGE),
              'http://uva.nl/thirdparty-packages/primus/%s' % (PACKAGE) ]


def download_primus(urls, destination):
    if os.path.isdir(destination): 
        raise BaseException("Destination '%s' cannot point to existent directory" % destination)

    if os.path.exists(destination): return True
    dfolder = os.path.dirname(destination) 
    if os.path.exists(dfolder): shutil.rmtree(dfolder)
    if not os.path.exists(dfolder) : os.mkdir(dfolder)

    for url in urls:
        repo = None
        try:
            repo = urllib2.urlopen(url)
            with open(destination, 'w') as file: file.write(repo.read())
            break
        except urllib2.HTTPError: pass
        finally:  
            if repo != None: repo.close()

    if not os.path.exists(destination): 
        print "\nERROR: Primus cannot be downloaded from repositories:\n * %s" % "\n * ".join(urls)
        return False
   
    # Read file to prevent possible unzip error
    # Most likely prev. file close doesn't close file immediately
    with open(destination, 'r') as f: f.read()
    
    done = False
    try:
        p = subprocess.Popen("unzip -o %s -d %s" % (destination, dfolder), stdout = subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if os.waitpid(p.pid, 0)[1] > 0: 
            shutil.rmtree(dfolder)
            raise BaseException("Unzip of '%s' failed.\nUnzip stderr:\n%s\nUnzip stdout:\n%s" % (destination, p.stderr.read(),p.stdout.read()))
        done = True
    finally: 
        if not done: shutil.rmtree(dfolder)

    print ":: Primus has been downloaded from: \n   * %s" % url
    return True


def deploy_project(project = 'project'):
    assert project
    
    __PROJECT = None
    try:
        __PROJECT = __import__(project) 
        __PROJECT.PROJECT
    except (NameError, AttributeError), e: 
        print 'ERROR:'   
        print "  " + str(e)
        return 1         
    
#    try:
    __PROJECT.PROJECT.deploy()    
 #   except (IOError, BaseException), e:
  #      print "\nDEPLOYMENT ERROR:\n  %s\n" % (str(e))
   #     return 1
    print "\nDEPLOYMENT SUCCESS:\n  Project '%s' has been successfully deployed.\n" % (__PROJECT.PROJECT.name)
    return 0

def run():
    if DOWNLOAD_PRIMUS: 
        if not download_primus(REPO_URLS, os.path.normpath(os.path.join(os.path.dirname(__file__), 'primus', PACKAGE))):
            exit(1)

    if len(sys.argv) > 1: 
        r = deploy_project(sys.argv[1])
    else:
        r = deploy_project()
    
    exit(r)
        
if __name__ == '__main__':
    run()
