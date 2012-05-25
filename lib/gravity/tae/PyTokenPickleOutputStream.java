package gravity.tae;

import java.io.*;

public class PyTokenPickleOutputStream
extends BufferedOutputStream 
{
    private int tokens = 0, pointer = 2;
    
    public PyTokenPickleOutputStream(OutputStream os)
    throws IOException
    {
       super(os);
       write("(lp1\n".getBytes());
    }
 
    public void write(PyToken t) 
    throws IOException
    {
       write(t.getText(), t.getOffset(), t.getLen(), t.getType());
    }
   
    public void write(String text, int offset, int length, int type)
    throws IOException
    {
       StringBuffer buf = new StringBuffer();
       write3fields(text, offset, length, buf);
  
       writePyInt(type, buf);
       buf.append("aa");           
       flushBuffer(buf);
       tokens++;
    }
   
    public void write(String text, int offset, int length, String type)
    throws IOException
    {
       StringBuffer buf = new StringBuffer();
       write3fields(text, offset, length, buf);
  
       writePyStr(type, buf);
       buf.append("aa");           
       flushBuffer(buf);
       tokens++;
    }

    public void close()
    throws IOException
    {
       write('.');
       super.close();
    }

    protected void flushBuffer(StringBuffer buf)
    throws IOException
    {
       write(buf.toString().getBytes("UTF-8"));
    }

    protected void writePyStr(String text, StringBuffer buf) 
    {
       buf.append('S').append('\'').append(text).append('\'');
       buf.append('\n');        
       buf.append('p').append(pointer++).append('\n');
    }

    protected void writePyInt(int i, StringBuffer buf) {
       buf.append("aI").append(i).append('\n');
    }

    private void write3fields(String text, int offset, int length, StringBuffer buf)
    {
       buf.append("(lp").append(pointer++).append('\n');
       
       text = text.replace('\n', ' ');
       text = text.replace('\\', ' ');
       text = text.replace('/', ' ');
       
       writePyStr(text, buf);
       writePyInt(offset, buf);
       writePyInt(length, buf);
       buf.append('a');
    }
}
