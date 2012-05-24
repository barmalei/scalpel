// #       This program is free software; you can redistribute it and/or modify
// #       it under the terms of the GNU General Public License as published by
// #       the Free Software Foundation; either version 2 of the License, or
// #       (at your option) any later version.
// #       
// #       This program is distributed in the hope that it will be useful,
// #       but WITHOUT ANY WARRANTY; without even the implied warranty of
// #       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// #       GNU General Public License for more details.
// #       
// #       You should have received a copy of the GNU General Public License
// #       along with this program; if not, write to the Free Software
// #       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
// #       MA 02110-1301, USA.


package ilps.tae;

import java.io.*;
import java.util.*;
import java.net.*;


public abstract class Tagger
{    
    private String     lang = "nl";
    private Properties config;
    private Map<String, String> TYPEMAP;
  
    public  interface TaggerListener {
        void recognitionStarted();
        void newTokenRecognized(String text, int offset, int len, String t); 
        void recognitionEndded();
    }
  
    public static class TaggerListenerStub
    implements TaggerListener
    {
        public void recognitionStarted() {}
        public void newTokenRecognized(String text, int offset, int len, String t) {} 
        public void recognitionEndded() {}
    }

    public static class TaggerListenerDebug
    extends TaggerListenerStub
    {
        public void recognitionStarted() {
            System.err.println("Start recognition:");
        }

        public void newTokenRecognized(String text, int offset, int len, String t) {
            System.err.println(" found entity: ['" + text + "'," + offset + "," + len + "," + t + "]");
        } 

        public void recognitionEndded() {
            System.err.println("End recognition:");
        }
    }
  
    public static class TaggerPickleListener
    extends TaggerListenerStub
    {
        private PyTokenPickleOutputStream pos;
    
        public TaggerPickleListener(OutputStream os) 
        throws IOException
        {
            pos = new PyTokenPickleOutputStream(os);
        }
    
        public void newTokenRecognized(String text, int offset, int len, String t) 
        {
            try {
                pos.write(text, offset, len, t);
            }
            catch(IOException e) {
                e.printStackTrace();
                cleanup();
            }
        } 
        
        public void recognitionEndded() {
            cleanup();
        }
        
        private void cleanup() {
            if (pos != null) {
                try { pos.close(); pos = null; } catch(IOException e) {}
            }
        }
    }
  
    public Tagger(Properties p) 
    throws Exception
    {
        String lang = p.getProperty("lang");
        if (lang != null) { 
          this.lang = lang.toLowerCase();
        }
  
        config = new Properties();
        InputStream pis = getClass().getResourceAsStream("jtagger.properties");
        if (pis != null) {
            config.load(pis);  
        }
        
        TYPEMAP = new HashMap<String, String>();
        fillTypeMap(TYPEMAP);
    } 

    protected File resolvePath(String path) 
    throws Exception
    {
        if (path == null || path.length() == 0) {
            throw new IllegalArgumentException();
        }
        
        URL url = getClass().getResource(path);
        if (url != null) {
            return new File(url.toURI());
        }    
        throw new FileNotFoundException("'" + path + "' cannot be resolved");  
    }

    protected File getModelFile(String model) 
    throws Exception
    {
        String path = config.getProperty(lang + "." + model.toLowerCase()).trim();
        if (path != null) {   
            return resolvePath(path);
        }
        throw new FileNotFoundException(path);
    }
    
    public void tag(String text, final TaggerListener listener)
    throws Exception
    {
        if (listener == null) {
            throw new IllegalArgumentException();
        }
    
        listener.recognitionStarted();
        try {
           doTagging(text, new TaggerListenerStub() {
              public void newTokenRecognized(String word, int offset, int ln, String tp) {
                tp = mapType(tp);
                if (tp != null) listener.newTokenRecognized(word, offset, ln, tp);
              }
           }); 
        }
        finally {
            listener.recognitionEndded();
        }
    }
    
    protected abstract void doTagging(String s, TaggerListener listener) 
    throws Exception; 

    protected void fillTypeMap(Map<String, String> TYPEMAP) {}
    
    protected String mapType(String type) {
      return TYPEMAP.get(type);
    }

    public String lang() {
      return this.lang;
    }

    public static void main(Class taggerclass, String[] args) 
    throws Exception
    {
        if (taggerclass == null) {
           throw new IllegalArgumentException("Tagger class name has to be specified.");
        }

        // Collect properties passed in command line
        Properties p = new Properties();
        for (int i=0; i<args.length; i++) {
            int j = args[i].indexOf('=');
            if (j > 0) {
               p.put(args[i].substring(0, j), args[i].substring(j+1));
            }
        }
 
        // read mode that defines the way how textual data will be passed
        // mode = "text" means the input text will be passed as commanfd line parameter "text"
        String mode = p.getProperty("mode");
        
        
        String text = null;
        // Read text from PIPE
        if (!p.containsKey("text")) 
        {
            StringBuffer  buf = new StringBuffer(); 
            try {
                BufferedReader bufReader = new BufferedReader(new InputStreamReader(System.in, "UTF-8"));
                char[]         cbuf      = new char[5000]; 
                int            count     = 0;
                while ( (count = bufReader.read(cbuf, 0, 5000)) >= 0) {
                   buf.append(cbuf, 0, count);
                }
            }
            catch (EOFException e) {}
            text = buf.toString();
        }
        else {
            text = p.getProperty("text");
        }
        
        // Create recognizer
        Tagger tagger = (Tagger)taggerclass.getConstructor(new Class[] { Properties.class }).newInstance(new Object[] { p });
    
        // Post result
        if (mode == null)
        {
           tagger.tag(text, new TaggerListenerStub() {
              public void newTokenRecognized(String text, int offset, int len, String t) {
                 System.out.println("\"" +  text + "\"" + "," + offset + "," + len + "," + t);
              }
           }); 
        }
        else
        {
           if (mode.equalsIgnoreCase("python")) {
               tagger.tag(text, new TaggerPickleListener(System.out)); 
           }
           else {
              throw new RuntimeException("Unknown mode :" + mode);
           }
        }
   }
}
