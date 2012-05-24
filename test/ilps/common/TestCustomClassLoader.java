package ilps.common; 

import org.junit.Test;
import org.junit.runner.JUnitCore;
import org.junit.runner.Result;
import org.junit.runner.notification.Failure;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.File;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertFalse;
import static org.junit.Assume.assumeTrue;

import ilps.common.*;

public class TestCustomClassLoader
{
    private File base = null;

    public TestCustomClassLoader() 
    throws Exception 
    {
        ClassLoader cl = getClass().getClassLoader();
        String      p  = cl.getResource("ilps/common/TestCustomClassLoader.class").getPath();
        File        f = (new File(p)).getParentFile();
        this.base  = f.getCanonicalFile();
    }
    
    public String fullpath(String p) {
        return (new File(base, p)).getAbsolutePath();
    }
    
    @Test(expected=FileNotFoundException.class)
    public void test_wrong_path1() 
    throws Exception
    {
        String p = fullpath("test_lib2");
        assumeTrue(!(new File(p)).exists());
        CustomClassLoader l = new CustomClassLoader(p);
    }

    @Test(expected=FileNotFoundException.class)
    public void test_wrong_path2() 
    throws Exception
    {
        String p1 = fullpath("test_lib");
        String p2 = fullpath("test_lib/gg.jar");
        assumeTrue((new File(p1)).exists());
        assumeTrue(!(new File(p2)).exists());
        CustomClassLoader l = new CustomClassLoader(p2);
    }

    @Test
    public void test_jar1() 
    throws Exception
    {
        String p = fullpath("test_lib/g-data.jar");
        assumeTrue((new File(p)).exists());
        CustomClassLoader l = new CustomClassLoader(p);
        Class cl = l.loadClass("gravity.data.TextModel");
        assertTrue(cl != null);

        boolean b = false;
        try { cl = l.loadClass("gravity.Context"); }
        catch(ClassNotFoundException e) { b = true; }
        assertTrue(b);

        b = false;
        try { cl = l.loadClass("gravity.io.DataBus"); }
        catch(ClassNotFoundException e) { b = true; }
        assertTrue(b);
    }
    
    @Test
    public void test_jars() 
    throws Exception
    {
        String p1 = fullpath("test_lib/g-core.jar");
        String p2 = fullpath("test_lib/g-data.jar");
        assumeTrue((new File(p1)).exists());
        assumeTrue((new File(p2)).exists());
        CustomClassLoader l = new CustomClassLoader(new String[] { p1, p2 } );
        Class cl = l.loadClass("gravity.data.TextModel");
        assertTrue(cl != null);
        cl = l.loadClass("gravity.Context");
        assertTrue(cl != null);
        
        boolean b = false;
        try { cl = l.loadClass("gravity.io.DataBus"); }
        catch(ClassNotFoundException e) { b = true; }
        assertTrue(b);
    }

    @Test(expected=RuntimeException.class)
    public void test_duplicated_jars1() 
    throws Exception
    {
        String p1 = fullpath("test_lib/g-core.jar");
        String p2 = fullpath("test_lib/g-core.jar");
        assumeTrue((new File(p1)).exists());
        assumeTrue((new File(p2)).exists());
        CustomClassLoader l = new CustomClassLoader(new String[] { p1, p2 } );
    }

    @Test(expected=RuntimeException.class)
    public void test_duplicated_jars2() 
    throws Exception
    {
        String p1 = fullpath("test_lib");
        String p2 = fullpath("test_lib/g-core.jar");
        assumeTrue((new File(p1)).exists());
        assumeTrue((new File(p2)).exists());
        CustomClassLoader l = new CustomClassLoader(p1);
        l.addJar(p2);
    }

    @Test(expected=RuntimeException.class)
    public void test_duplicated_folders1() 
    throws Exception
    {
        String p1 = fullpath("test_lib");
        String p2 = fullpath("test_lib");
        assumeTrue((new File(p1)).exists());
        assumeTrue((new File(p2)).exists());
        CustomClassLoader l = new CustomClassLoader(new String[] { p1, p2 } );
    }

    @Test(expected=RuntimeException.class)
    public void test_duplicated_folders2() 
    throws Exception
    {
        String p1 = fullpath("test_lib");
        String p2 = fullpath("test_lib");
        assumeTrue((new File(p1)).exists());
        assumeTrue((new File(p2)).exists());
        CustomClassLoader l = new CustomClassLoader(p1);
        l.addFolder(p2, false);
    }

    @Test(expected=IllegalArgumentException.class)
    public void test_illegal_jar() 
    throws Exception
    {
        String p1 = fullpath("test_lib");
        assumeTrue((new File(p1)).exists());
        CustomClassLoader l = new CustomClassLoader(p1);
        l.addJar((File)null);
    }

    @Test
    public void test_folder1() 
    throws Exception
    {
        String p = fullpath("test_lib");
        assumeTrue((new File(p)).exists());
        CustomClassLoader l = new CustomClassLoader();
        l.addFolder(p, false);
        Class cl = l.loadClass("gravity.io.DataBus");
        assertTrue(cl != null);
        
        boolean b = false;
        try { cl = l.loadClass("gravity.data.TextModel"); }
        catch(ClassNotFoundException e) { b = true; }

        b = false;
        try { cl = l.loadClass("gravity.Context"); }
        catch(ClassNotFoundException e) { b = true; }
    }

    @Test
    public void test_folder2() 
    throws Exception
    {
        String p = fullpath("test_lib");
        assumeTrue((new File(p)).exists());
        CustomClassLoader l = new CustomClassLoader(p);
        Class cl = l.loadClass("gravity.data.TextModel");
        assertTrue(cl != null);
        cl = l.loadClass("gravity.Context");
        assertTrue(cl != null);
        cl = l.loadClass("gravity.io.DataBus");
        assertTrue(cl != null);
    }

    @Test
    public void test_resources1() 
    throws Exception
    {
        String p = fullpath("test_lib");
        assumeTrue((new File(p)).exists());
        CustomClassLoader l = new CustomClassLoader(p);
        java.net.URL u = l.getResource("gravity/io/beans.xml");
        assertTrue(u != null);
        u = l.getResource("gravity/io/beans2.xml");
        assertTrue(u == null);
    }

    @Test
    public void test_resources2() 
    throws Exception
    {
        String p = fullpath("test_lib/g-core.jar");
        assumeTrue((new File(p)).exists());
        CustomClassLoader l = new CustomClassLoader(p);
        java.net.URL u = l.getResource("gravity/Context.class");
        assertTrue(u != null);
        u = l.getResource("gravity/io/beans.xml");
        assertTrue(u == null);
    }
    
    public static void main(String[] args)
    throws Exception
    {
		Result result = JUnitCore.runClasses(TestCustomClassLoader.class);
        for (Failure failure : result.getFailures()) {
            System.err.println("Failed: " +  failure.toString());
        }
	}
}


