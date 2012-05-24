#include <string>
#include <vector>
#include <iostream>
#include <fstream>

using namespace std;

#define MAX_VALUE 10000000

typedef vector< int > INTVECT;

//
// Calculate diag
//
INTVECT calculate_diag(const string& text, const string& pattern, const int& delta) {
  
  int rows    = text.length(), cols = pattern.length();
  int colsize = delta * 2 + 1;

  // init two columns for calculation and fill it with max value   
  INTVECT lcol;
  INTVECT rcol;
  lcol.resize( colsize + 3, MAX_VALUE );
  rcol.resize( colsize + 3, MAX_VALUE );

  // setup initial values for left column
  for (int row=0; row < delta + 3; row++) {
      lcol[row] = row;
  }
  
  INTVECT data;
  data.resize( cols * (colsize + 1), MAX_VALUE );
      
  // initialize start and end rows indexes
  int l_row1 = 0, l_row2 = delta + 1, l_col = -1; 
          
  // slightly speed up access to variable
  int maxrow = rows - 1;
      
  for (int col=0; col < cols; col++) {
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
    char col_ch = pattern[col];
          
    // pre-calculated variables slightly speed up loop below
    int drr = 1 - r_row1;
    int dlr = 1 - l_row1;    
    
    // calculate starting index for the given column 
    int index = col * (colsize + 1);
    
    // store starting row to be calculated as the first element 
    data[index] = r_row1;
    index ++;
                
    // calculate diagonal elements for the given column
    for (int row = r_row1; row < r_row2 + 1; row++) { 
      // again pre-compute values to speed up calculation
      int i = row + drr; 
      int j = row + dlr;    
                  
      // compare text and pattern characters 
      if (text[row] == col_ch) { 
        rcol[i] = lcol[j - 1];
        data[index] = rcol[i];
      }    
      else {  
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
    INTVECT a = lcol;
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
void print_result(const string& s1, const string& s2, const int& delta, const INTVECT& res) {
  int rows = s1.length(), cols = s2.length();
  int colsize = delta * 2 + 1;

  for (int row = 0; row < rows; row++) {
    for (int col=0; col < cols; col++) {
      int index  = (colsize + 1) * col;
      int srow   = res[index];
      index ++;
      int i = index + row - srow;
      
      if (row < srow || row >= srow + colsize || res[i] == MAX_VALUE) { 
        cout << " xx ";
      }    
      else {
        cout << " " << res[i] << " ";
      }        
    }
    cout << endl; 
  }                
  cout << endl;
}

string readFile(const string& filename) {
  string allstr = "";
  string str;
  ifstream infile;
  infile.open( filename.c_str() );
  
  if ( !infile.is_open() ) {
    cout << "file doesn't exist" << endl;
    exit( -1 );
  }
  else {
    infile >> allstr; 
    while( !infile.eof() ) {
      infile >> str; 
      allstr += (" " + str);
    }
    infile.close();
    return allstr;    
  }
}


int main( int argc, char* argv[] ) {
  
//  string s1  = "sdasdasd";
//  string s2 = "sdsadasd"; 
//  int    d  = 2;
  
  clock_t t1, t2;  
  
  string s1 = readFile("test.txt");
  string s2 = readFile("test2.txt"); 
  int     d = 100;

  cout << "s1.length = " << s1.length() << "  s2.length = " << s2.length() << endl;

  t1 = clock();
  
  INTVECT r = calculate_diag(s1, s2, d);
//  print_result(s1, s2, d, r);  

  t2 = clock();
  float diff = ((float)t2 - (float)t1) / 1000000.0F;
  
  cout << "runtime: " << diff << " ms" << endl;

  int li = (d * 2 + 2) * (s2.length() - 1 ) + d;
  cout << "Last element: " << r[li] << endl;
  
}

