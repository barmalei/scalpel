package test;

import java.io.*;
import java.util.*;

public class test_levdiag
{
    public static final int MAX_VALUE = 1000000000;

    public static int[] calculate_diag(String text, String pattern, int delta)
    {
        int rows    = text.length(), cols = pattern.length();
        int colsize = delta * 2 + 1;
    
        // init two columns for calculation and fill it with max value   
        int[] lcol = new int[colsize + 3];
        int[] rcol = new int[colsize + 3];
        Arrays.fill(lcol, 0, lcol.length, MAX_VALUE);
        Arrays.fill(rcol, 0, rcol.length, MAX_VALUE);

        // setup initial values for left column
        for (int row=0; row < delta + 3; row++) {
            lcol[row] = row;
        }

        int[] data = new int[(cols * (colsize + 1))];
        Arrays.fill(data, 0, data.length, MAX_VALUE);
        
        // initialize start and end rows indexes
        int l_row1 = 0, l_row2 = delta + 1, l_col = -1; 
    
        
        // slightly speed up access to variable
        int maxrow = rows - 1;
        
        for (int col=0; col < cols; col++) 
        {
            // calculate anchor row index
            int arow = (col * rows) / cols;
            
            // upper row
            int r_row1 = arow > delta ? arow - delta : 0;
            
            // lower row
            int r_row2 = arow + delta;
            if (r_row2 >= rows) r_row2 = maxrow; 

            lcol[0] = l_row1 == 0 ? col     : MAX_VALUE;   
            rcol[0] = r_row1 == 0 ? col + 1 : MAX_VALUE;
            
            // to speed up access to array element store it in temporary var
            char col_ch = pattern.charAt(col);
            
            // pre-calculated variables slightly speed up loop below
            int drr = 1 - r_row1;
            int dlr = 1 - l_row1;    
            
            // calculate starting index for the given column 
            int index = col * (colsize + 1);
            
            // store starting row to be calculated as the first element 
            data[index] = r_row1;
            index ++;
                    
            // calculate diagonal elements for the given column
            for (int row = r_row1; row < r_row2 + 1; row++) 
            { 
                // again pre-compute values to speed up calculation
                int i = row + drr; 
                int j = row + dlr;    
                            
                // compare text and pattern characters 
                if (text.charAt(row) == col_ch) { 
                    rcol[i] = lcol[j - 1];
                    data[index] = rcol[i];
                }    
                else 
                {  
                    // the construction below is equivalent of min (a,b,c) 
                    // function just to win another thousand milliseconds
                    int a = lcol[j], b = rcol[i - 1], c = lcol[j - 1];
                    if (a < b) {
                        if (c < a) a = c; 
                    }
                    else {
                        a = b < c ? b : c;
                    }

                    a++;              
                    rcol[i] = data[index] = a; 
                }
                     
                index ++;    
             }
     
            // replace left row reference with just calculated right row
            // since for the next column calculation current right row should 
            // be considered as left row.
            int[] a = lcol;
            lcol = rcol;
            rcol = a;
            l_row1 = r_row1; 
            l_row2 = r_row2;
        }
        return data;
    }
    
    //
    // dirty code just to visualize results
    //
    public static void print_result(String s1, String s2, int delta, int[] res)
    {
        int rows = s1.length(), cols = s2.length();
        int colsize = delta * 2 + 1;
 
        String buf = new String("");
        for (int row = 0; row < rows; row++)
        {
            for (int col=0; col < cols; col++)
            {
                int index  = (colsize + 1) * col;
                int srow   = res[index];
                index ++;
                int i = index + row - srow;
                
                if (row < srow || row >= srow + colsize || res[i] == MAX_VALUE) { 
                    buf += " xx ";
                }    
                else {
                    buf += " " + res[i] + " ";
                }        
            }
            buf += "\n";
         }           
         
        System.out.println(buf);
    }
    
    
    public static String readFile(String fname)
    throws Exception
    {
       // read file 
       FileInputStream       fi  = new FileInputStream(fname);
       ByteArrayOutputStream bo  = new ByteArrayOutputStream();
       byte[]                buf = new byte[1024];
       int                   c   = 0;
       while ((c = fi.read(buf)) >= 0) {
         bo.write(buf, 0, c);
       }
       fi.close();
        
       return bo.toString();        
    } 
    
    public static void test1() 
    {
       // prepare input data
       String s1  = "sdasdasd";
       int    d  = 2;
       String s2 = "sdsadasd"; 
       int[] r = runTest(s1, s2, d);
       print_result(s1, s2, d, r);  
    }

    public static void test2() 
    throws Exception
    {
        // prepare input data 
       String          s1  = readFile("test.txt");
       int             d  = 100;
       String          s2 = readFile("test2.txt"); 
       runTest(s1, s2, d);
    }

    private static int[] runTest(String s1, String s2, int d)
    {
       System.out.println("Input data: s1.len = " + s1.length() + ", s2.len = " + s2.length() + ", delta = " + d); 
            
       // run test
       long  t = System.currentTimeMillis();          
       int[] r = calculate_diag(s1, s2, d);
       System.out.println("Time: " + (System.currentTimeMillis() - t) + " milliseconds");    
       int i = (d * 2 + 2) * (s2.length() - 1) + d + 1;
       System.out.println("Last elements:" + r[i] + ","  + r[i-1]); 
       
       return r;
    } 
    
    public static void main(String[] args)
    throws Exception
    {       
       test2();
    }
} 
