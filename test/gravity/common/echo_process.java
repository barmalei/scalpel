package gravity.common;

import java.io.*;

public class echo_process
{
    public static void main(String[] args)
    throws Exception
    {
        StringBuffer buf = new StringBuffer();
        int r = 0;
        while ((r = System.in.read()) > 0) {
            buf.append((char)r);
        }
        System.out.print(buf.toString());
    }
}