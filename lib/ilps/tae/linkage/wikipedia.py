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
#       MA 02110-1301, USA

from __future__ import with_statement

from ilps.common.db import Database
from ConfigParser import ConfigParser
from link import Link

class Wikipedia(Link):
    def __init__(self, name):
        assert name
        self._name  = name
        self.langs = set(["en"])
        self.db_parameters = {  }
        self.db = None

    @property
    def name(self): 
        return self._name

    def init_from_config(self, config):
        if isinstance(config, basestring):
            fname  = config
            config = ConfigParser()
            config.read(fname)
        
        # read all WIKI properties and represent it as class properties
        for o in config.options(self.name): 
            setattr(self, o, config.get(self.name, o).strip())
                    
        self.db_parameters.clear()
        if self.db[0] == '{' : 
            self.db_parameters = eval(self.db) 
        else:
            for p in config.items(self.db): self.db_parameters[p[0]] = p[1] 
        
        self.db = self._init_db()

        self.languages = [language.strip() for language in config.get(self.name, "languages").split(',')]

    def search(self, text, language):
        assert text and language
       
        language = str(language)
        if language not in self.languages:
            raise BaseException("Unsupported '%s' language." % language)
        
        if self.db is None:
            self.db = self._init_db()
        
        # init array to collect all found references
        urls = []
        
        # read Wiki data base parameters from configuration
        page_table_name = self._get("_".join([language, "page_table"]), "_".join([language, "page_title"])) 
        inlinks_table_name  =  self._get("_".join([language, "inlinks_table"]), "_".join([language, "inlinks"])) 
        redirect_table_name =  self._get("_".join([language, "redirect_table"]), "_".join([language, "_redirect"])) 
        url = self._get("_".join([language, "base_url"]), "")
        if url and url[-1] != '/': url += '/'
     
        with self.db.getConnection() as con: 
            pid = self._get_page_id(text,
                                    con,
                                    page_table_name,
                                    inlinks_table_name,
                                    redirect_table_name)
        
            if pid != -1: 
                # Get page title from wikipedia dump
                sql = "SELECT page_title FROM %s WHERE page_id = %%s" % (page_table_name, )
                cur = con.cursor()
                cur.execute(sql, str(pid[0]))
                article = cur.fetchall()
                cur.close()

                if (article[0][0] != ""):
                    page_title = article[0][0]
                    urls.append(url + page_title)
        return urls


    def _get_page_id(self, text, con, page_table_name, inlinks_table_name, redirect_table_name):
        """Get page id from database

           -text: Text content of current named entity
           -page_table_name: The name of page title table in named entity normalization database
           -inlinks_table_name: The name of inlinks table in named entity normalization database
           -con: Wikixml dump database connection

        """
        assert page_table_name and inlinks_table_name
        
        # Get page id from wikipedia dump
        sqlstr_case_sensitive = """SELECT page_id, page_is_redirect
                                FROM %s
                                WHERE page_title = BINARY %%s""" % (page_table_name)

        cur = con.cursor()
        cur.execute(sqlstr_case_sensitive, text)
        article = cur.fetchall()
        cur.close()
        
        if article is None or len(article) == 0:
            sqlstr = """SELECT page_id, page_is_redirect
                     FROM %s
                     WHERE page_title = %%s""" % (page_table_name)

            # There maybe a difference between MAC and Mac ...
            cur = con.cursor()
            cur.execute(sqlstr, (text))
            article = cur.fetchall()
            cur.close()
                
        if article and len(article) > 0:  
            if(article[0][1] == 1):
                return self._get_redirect_page( article[0][0],
                                                con,
                                                page_table_name,
                                                inlinks_table_name,
                                                redirect_table_name)
            else: 
                return article[0]
                  
        return -1

    def _get_redirect_page(self, page_id, con, page_table_name, inlinks_table_name, redirect_table_name):
        """Get redirect page id from wikipedia database

           -page_id: The page id of wikixml dump database
           -page_table_name: The name of page title table in named entity normalization database
           -inlinks_table_name: The name of inlinks table in named entity normalization database
           -con: Wikixml dump database connection
        """
            
        sql = """select t1.page_id FROM %s t1, %s t2, %s t3
                 where t2.page_id = %%s
                 and t1.page_id = t2.target_id and
                 t3.page_id = t1.page_id
                 ORDER BY t3.inlinks DESC LIMIT 1""" \
            % (page_table_name,
               redirect_table_name,
               inlinks_table_name)
                 
        cur = con.cursor()
        cur.execute(sql, str(page_id))
        article = cur.fetchall()
        cur.close()
        
        if article is not None and len(article) > 0: return article[0]
        return -1

    def _get(self, attrname, def_value=None):
        if hasattr(self, attrname): 
            v = getattr(self, attrname).strip()
            if isinstance(v, basestring) : v = v.strip()
            return v
        
        if def_value != None: return def_value
        
        raise BaseException("Attribute '%s' is not defined." % attrname)

    def _init_db(self):
        if len(self.db_parameters) == 0:
            raise BaseException("No data base parameters have been defined")  
        return Database(self.name, self.db_parameters)

    def _set_languages(self, langs):
        assert langs
        self._languages = set(langs)
                
    def _get_languages(self):
        return self._languages

    languages = property(_get_languages, _set_languages)





