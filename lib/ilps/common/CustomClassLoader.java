package ilps.common;


import java.io.ByteArrayOutputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.File;
import java.io.FileFilter;
import java.io.InputStream;
import java.io.FileInputStream;
import java.net.URL;
import java.net.MalformedURLException;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;
import java.util.HashMap;
import java.util.jar.JarFile;
import java.util.jar.JarEntry;
import java.util.concurrent.Executors;
import java.util.concurrent.Executor;
import java.util.concurrent.ThreadFactory;

public class CustomClassLoader 
extends ClassLoader 
{
    private Map  classes = new HashMap();
    private Map<String, JarFile> jars = new HashMap();
    private List<File>  dirs = new ArrayList();

    public CustomClassLoader() {}

    public CustomClassLoader(String path) 
    throws IOException
    {
        this(new File(path));
    }

    public CustomClassLoader(File path) 
    throws IOException
    {
        super(CustomClassLoader.class.getClassLoader()); 
        setupPath(path);
    }

    public CustomClassLoader(String[] paths) 
    throws IOException
    {
        super(CustomClassLoader.class.getClassLoader()); 
        for(String path : paths) {
            setupPath(new File(path));
        }
    }

    protected void setupPath(File path)
    throws IOException
    {
        if (path == null) {
            throw new IllegalArgumentException();
        }    
        
        if (path.isDirectory()) { 
            addFolder(path, true);
        }
        else {
            addJar(path);
        }
    }

    public void addFolder(String path, boolean addJars) 
    throws IOException
    {
        if (path == null) { 
            throw new IllegalArgumentException(); 
        }
        addFolder(new File(path), addJars);
    }

    public void addFolder(File file, boolean addJars) 
    throws IOException
    {
        if (file == null) {
            throw new IllegalArgumentException();
        }    
        
        if (!file.exists()) {
            throw new FileNotFoundException(file.getPath());
        }
        
        if (!file.isDirectory()) {
            throw new RuntimeException("Folder '"  + file.getAbsolutePath() + "' is not a directory");
        }
        
        if (this.dirs.indexOf(file) >= 0) {
            throw new RuntimeException("Duplicated folder: " + file.getAbsolutePath());
        }

        this.dirs.add(file);

        if (addJars) {
            File[] jars = file.listFiles(new FileFilter() {
                 public boolean accept(File f) {
                     String n = f.getName();
                     return (f.isFile() && n.toLowerCase().indexOf(".jar") == (n.length() - 4));
                 }
            });
        
            for(int i=0; i < jars.length; i++) {
                addJar(jars[i]);
            }
        }
    }

    public void addJar(String path) 
    throws IOException
    {
        if (path == null) { 
            throw new IllegalArgumentException(); 
        }
        addJar(new File(path));
    }

    public void addJar(File jar) 
    throws IOException
    {
        if (jar == null) {
            throw new IllegalArgumentException();
        }
        
        if (!jar.exists()) {
            throw new FileNotFoundException(jar.getPath());
        }

        if (jar.isDirectory()) {
            throw new IOException("JAR path '" + jar.getPath() + "' is directory");
        }
        
        if (this.jars.get(jar.getName()) != null) { 
            throw new RuntimeException("Duplicated JAR: " + jar.getPath());
        }
        
        this.jars.put(jar.getName(), new JarFile(jar));
    }

    public Class loadClass(String className) 
    throws ClassNotFoundException 
    {
        return findClass(className);
    }

    protected synchronized URL findResource(String name) 
    {
        URL r = getParent().getResource(name);
        if (r != null) return r;
 
        for(File dir:this.dirs) {
            File path = new File(dir, name);
            if (path.exists()) {
                try {
                    return path.toURI().toURL();
                }
                catch(MalformedURLException e) {
                    throw new RuntimeException(e.toString());
                }
            }
        }

        for(JarFile jar:this.jars.values()) {
            JarEntry entry = jar.getJarEntry(name);
            if (entry != null) {
                try {
                    return new URL("jar:" + (new File(jar.getName())).toURI().toURL() + "!/" + name);
                }
                catch(MalformedURLException e) {
                    throw new RuntimeException(e.toString());
                }
            }
        }
        return null;
    }

    protected synchronized Class findClass(String className) 
    throws ClassNotFoundException 
    {
        Class clazz = (Class)classes.get(className); 
        if (clazz != null) return clazz;
        try {
            String cn = className.replace('.', '/').concat(".class");
            for(JarFile jar : this.jars.values()) {
                JarEntry entry = jar.getJarEntry(cn);
                if (entry != null) {
                    clazz = loadFromStream(className, jar.getInputStream(entry));
                    classes.put(className, clazz);
                    return clazz;
                }
            }
            
            String p = className.replace('.', '/').concat(".class");
            for(File dir: this.dirs) {
                File f = new File(dir, p); 
                if (f.exists()) {
                    FileInputStream fi = null;
                    try {
                        fi = new FileInputStream(f);
                        clazz = loadFromStream(className, fi);
                        classes.put(className, clazz);
                        return clazz;
                    }
                    finally {
                        fi.close();
                    }
                }
            }
        }
        catch(IOException e) {
            e.printStackTrace();
            throw new ClassNotFoundException("Class " + className + " not found");
        }

        return findSystemClass(className);
    }
    
    private Class loadFromStream(String className, InputStream is)  
    throws IOException
    {
        byte[] buf = new byte[10000];
        ByteArrayOutputStream bo = new ByteArrayOutputStream();
        int c = 0;
        while ((c = is.read(buf)) >= 0) bo.write(buf, 0, c);
        return defineClass(className, bo.toByteArray(), 0, bo.size(), null);
    }

    // static class NERService {
    //     public void NERService(NER ner) {
    //         ner.setClassLoader();
    //     }
    // }
    
    public static void main(String[] args) 
    throws Exception
    {
        Executor e = Executors.newSingleThreadExecutor(new ThreadFactory() {
            public Thread newThread(Runnable r) {
                try {
                    Thread t = new Thread(r);
               //     t.setDaemon(true);
                    System.out.println("newThread ");
                    CustomClassLoader cl = new CustomClassLoader("lib/test"); 
                    Class c = cl.loadClass("gravity.data.Text");
                    c.newInstance();
                    
                    System.out.println("newThread " + cl);
                    

                    t.setContextClassLoader(cl);
                    return t;
                }
                catch(Exception e) {
                    e.printStackTrace();
                }
                return null;
            }
        });
        
        // e.execute(new Runnable() {
        //     public void run() {
        //         try {
        //             System.out.println(Class.forName("gravity.data.TextModel"));
        //         }
        //         catch(Exception e) {
        //             e.printStackTrace();
        //         }
        //         
        //     }
        // });


        CustomClassLoader cl = new CustomClassLoader("lib/test"); 
        cl.loadClass("gravity.data.TextModel");
        
        System.out.println(Class.forName("org.apache.lucene.util.ArrayUtil"));
    }
}

