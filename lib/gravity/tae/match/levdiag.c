#include <Python.h>
#include <float.h>

// max value
const int   MAX_INT_VALUE   = 100000000;
const float MAX_FLOAT_VALUE = FLT_MAX;


//
//  Calculate Levenshtein distance for the specified strings 
//  input: 
//     unicode string 1
//     unicode string 2
//  return: Python int   
//    
static PyObject* fLevDistance(PyObject* self, PyObject* args)
{
    const Py_UNICODE *text1;
    const Py_UNICODE *text2;
    int   rows, cols, row, col;   
    
    // convert PyObject to appropriate C typed variables
    if (!PyArg_ParseTuple(args, "u#u#", &text1, &rows, &text2, &cols)) {
      return Py_None;  
    }

    // create array
    int* data = malloc(sizeof(int) * rows);
    if (data == NULL) {
        return PyErr_NoMemory();
    }
    
    int top = 0, diag;
    
    // setup initial values for left column
    for (row=0; row < rows; row++) {    
       data[row] = row;
    }
 
    for (col=0; col < cols; col++) 
    {
        // store character 
        Py_UNICODE pch = text2[col];
        
        // init top and diagonal elements
        diag = col;
        top  = col + 1;
         
        for (row=0; row < rows; row++)
        {
            int dr = data[row];
            
            if (text1[row] == pch) 
            { 
                top       = diag; 
                diag      = dr;           
                data[row] = top; 
            }    
            else
            {   
                // calculate minimum
                if (top < dr)
                {
                  if (diag < top) { 
                    top = diag;
                  }
                }
                else {
                  top = (dr < diag) ? dr : diag; 
                } 
                
                top++; 
                
                diag      = dr;
                data[row] = top;
            }
         }
    }      
        
    free(data);
    return Py_BuildValue("i", top);
}


//
//  Calculates Levenshtein distance matrix for the specified strings
//  Input:
//    string 1 (unicode)
//    string 2 (unicode)
//  Return:   
//    Python list [ col0_row0, ..., col0_rowN, col1_row0, ..., col1_rowN, ...]
//
static PyObject* fLevDistanceMatrix(PyObject* self, PyObject* args)
{
    const Py_UNICODE *text1;
    const Py_UNICODE *text2;
    int   rows, cols, row, col;   

    // convert PyObject to appropriate C typed variables
    if (!PyArg_ParseTuple(args, "u#u#", &text1, &rows, &text2, &cols)) {
      return Py_None;  
    }

    // create list
    PyObject *data = PyList_New(rows * cols);
    if (data == NULL) {
       return PyErr_NoMemory();
    }

    // setup initial values for left column
    for (row=0; row < rows; row++) {
        PyList_SetItem(data, row, Py_BuildValue("i", row + 1));
    }

    int index = 0, pindex = 0, diag = 0, top, si = 0; 
    for (col=0; col < cols; col++) 
    {
        // store character 
        Py_UNICODE pch = text2[col];     
        
        // start handling new column, have to init top and diag elements
        diag = col;
        top  = col + 1;
         
        // store first row index of prev. column
        si = index;
         
        for (row=0; row < rows; row++)
        {
            PyObject* item = PyList_GetItem(data, pindex);
            int left = (int)PyInt_AsLong(item);
            
            if (text1[row] == pch) 
            { 
               PyList_SetItem(data, index, Py_BuildValue("i", diag));
               top  = diag; 
               diag = left;           
            }    
            else
            {   
                // calculate minimum
                if (top < left)
                {
                  if (diag < top) { 
                    top = diag;
                  }
                }
                else {
                  top = (left < diag) ? left : diag; 
                } 
                
                top++; 
                
                diag  = left;
                PyList_SetItem(data, index, Py_BuildValue("i", top));
            }
            
            index ++;
            pindex++;
         }
         pindex = si;
    }      

    return data;
}


//
//  Calculates Levenshtein diagonal for the specified string and diagonal 
//  delta (number of elements below and above diagonal to be calculated)
//  Input:
//    -- unicode string
//    -- unicode string
//    -- delta
//    -- default value (the value of matrix elements that are outside of 
//       calculated diagonal)
//  Return:
//    Python list [ fisrt_row_index, col0_fisrtrow_value ... col0_rowN_value, ... ]
//
static PyObject* fLevDistanceDiag(PyObject* self, PyObject* args) 
{
  Py_UNICODE *text;
  Py_UNICODE *pattern;
  int  delta, rows, cols, def_value;

  // convert PyObject to appropriate C typed variables
  if (!PyArg_ParseTuple(args, "u#u#ii", &text, &rows, &pattern, &cols, &delta, &def_value)) {
    return Py_None;  
  }
  
  // normalize delta
  delta = (rows - delta - 1) < 0  ? rows - 1 : delta;  
  int colsize = delta * 2 + 1, i = 0;

  // init two columns for calculation and fill it with max value   
  int a_lcol[colsize + 3];
  int a_rcol[colsize + 3];
  
  int *lcol = a_lcol;
  int *rcol = a_rcol;
   
  for (i=0; i < colsize + 3; i++) {
      lcol[i] = def_value;
      rcol[i] = def_value;
  }

  // setup initial values for left column
  for (i=0; i< delta + 3; i++) {
      lcol[i] = i;
  }
  
  // setup result array
  int data_size = cols * (colsize + 1);
  PyObject *data = PyList_New(data_size);
  if (data == NULL) {
     return PyErr_NoMemory();
  }
  
  for (i=0; i < data_size; i++) {
      PyList_SetItem(data, i, Py_BuildValue("i", def_value));
  }

  // initialize start and end rows indexes
  int l_row1 = 0, l_row2 = delta + 1; 
          
  // slightly speed up access to variable
  int maxrow = rows - 1;
      
  int col = 0, row = 0; 
  for (col=0; col < cols; col++) 
  {
    // calculate anchor row index
    int arow = (int)(((long)col * (long)rows) / (long)cols);
    
    // upper row
    int r_row1 = arow > delta ? arow - delta : 0;
    
    // lower row
    int r_row2 = arow + delta;
    if (r_row2 >= rows) r_row2 = maxrow; 

    lcol[0] = l_row1 == 0 ? col     : lcol[1];   
    rcol[0] = r_row1 == 0 ? col + 1 : def_value;
    
    // to speed up access to array element store it in temporary var
    Py_UNICODE col_ch = pattern[col];
          
    // pre-calculated variables slightly speed up loop below
    int drr = 1 - r_row1;
    int dlr = 1 - l_row1;    
    
    // calculate starting index for the given column 
    int index = col * (colsize + 1);
    
    // store starting row to be calculated as the first element 
    // data[index] = r_row1;
    PyList_SetItem(data, index, Py_BuildValue("i", r_row1));
    index ++;
                
    // calculate diagonal elements for the given column
    for (row = r_row1; row < r_row2 + 1; row++) { 
      // again pre-compute values to speed up calculation
      int i = row + drr; 
      int j = row + dlr;    
                  
      // compare text and pattern characters 
      if (text[row] == col_ch) { 
        rcol[i] = lcol[j - 1];
        PyList_SetItem(data, index, Py_BuildValue("i", rcol[i]));

        //data[index] = rcol[i];
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
        rcol[i] = a; 
        PyList_SetItem(data, index, Py_BuildValue("i",a));
      } 
      index++;    
    }

    // replace left row reference with just calculated right row
    // since for the next column calculation current right row should 
    // be considered as left row.
    int *a = lcol;
    lcol = rcol;
    rcol = a;
    l_row1 = r_row1; 
    l_row2 = r_row2;
  }
  
  return data;
}

 
//
//  Minimal path element
// 
struct CELL {
  int   row;
  int   col;    
  void *prev; 
};
 
 
struct CELL* add_cell(struct CELL* tail, int row, int col)
{
   struct CELL* new_cell = (struct CELL*)malloc(sizeof(struct CELL));   

   if (new_cell == NULL) {
      return NULL;  
   }

   new_cell->row  = row;
   new_cell->col  = col;
   new_cell->prev = tail;
   return new_cell;
} 
 
void print_cells(struct CELL *tail)
{ 
  struct CELL *m = tail;
  while (m) {
    printf (" ; (%d, %d)", m->row, m->col);
    m = m->prev;
  }
  printf("\n\n");
}

void free_cells(struct CELL *tail)
{
   if (tail != NULL) {
      free_cells((struct CELL*)tail->prev);
      free(tail);
   }    
} 

int count_cells(struct CELL *tail)
{
   struct CELL *t = tail;
   int counter = 0;
   
   while (t) {
      counter++;
      t = (struct CELL*)t->prev;
   }
   return counter;   
} 

struct CELL* find_cell_by_col(struct CELL *tail, int col)
{
   struct CELL *t = tail;
   struct CELL *r = NULL;
   while (t && t->col <= col) {
      if (t->col == col) r = t;
      t = (struct CELL*)t->prev;
   }
   return r;   
} 

struct CELL* find_cell_by_row(struct CELL *tail, int row)
{
   struct CELL *t = tail;
   struct CELL *r = NULL;
   while (t && t->row <= row) {
      if (t->row == row) r = t;
      t = (struct CELL*)t->prev;
   }
   return r;   
} 

 
int get_cell(int* data, int row, int col, int colsize)
{
    int index = col * (colsize + 1);
    int start_row = (int)data[index];
    return (row < start_row || row >= start_row + colsize) ? MAX_INT_VALUE : data[index + row - start_row + 1];
}


float get_cell_float(float* data, int row, int col, int colsize)
{
    int index = col * (colsize + 1);
    int start_row = (int)data[index];
    return (row < start_row || row >= start_row + colsize) ? MAX_FLOAT_VALUE : data[index + row - start_row + 1];
}


struct CELL* calculate_min_path(int* data, int rows, int cols, int colsize)
{
    struct CELL* tail;    

    int i = rows - 1, j = cols-1;
    int dr = 0, dc = 0;
 
    tail = malloc(sizeof(struct CELL));
    if (tail == NULL) {
      return NULL;
    }

    tail->row = i;
    tail->col = j;
    tail->prev = NULL;

    while (j != 0 || i != 0) 
    {
        int min   = get_cell(data, i, j, colsize);
        int left  = get_cell(data, i, j-1, colsize);  
        int top   = get_cell(data, i-1, j, colsize);
        
        int diag  = get_cell(data, i-1, j-1, colsize);
        if (left  < min) {
           dr  =  0;
           dc  = -1; 
           min = left;    
        }
        
        if (top < min) {   
           dr  = -1;
           dc  =  0;
           min = top; 
        }
        
        if (diag <= min) { 
            dr = dc = -1;
        }
        
        if (i > 0) { 
           i += dr;
        }
        
        if (j > 0) { 
          j += dc;
        }
        
        tail = add_cell(tail, i, j);
    }
     
    return tail;
}


struct CELL* calculate_min_path_float(float* data, int rows, int cols, int colsize)
{
    struct CELL* tail;    

    int i = rows - 1, j = cols-1;
    int dr = 0, dc = 0;
 
    tail = malloc(sizeof(struct CELL));
    if (tail == NULL) {
      return NULL;
    }

    tail->row = i;
    tail->col = j;
    tail->prev = NULL;

    while (j != 0 || i != 0) 
    {
        float min   = get_cell_float(data, i, j, colsize);
        float left  = get_cell_float(data, i, j-1, colsize);  
        float top   = get_cell_float(data, i-1, j, colsize);
        
        float diag  = get_cell_float(data, i-1, j-1, colsize);
        if (left  < min) {
           dr  =  0;
           dc  = -1; 
           min = left;    
        }
        
        if (top < min) {   
           dr  = -1;
           dc  =  0;
           min = top; 
        }
        
        if (diag <= min) { 
            dr = dc = -1;
        }
        
        if (i > 0) { 
           i += dr;
        }
        
        if (j > 0) { 
          j += dc;
        }
        
        tail = add_cell(tail, i, j);
    }
     
    return tail;
}


//
//  Calculates Levensthein minimal path for the given diagonal data
//  Input: 
//     -- Python list that represents calculated diagonal (special structure) 
//     -- number of rows
//     -- number of cols
//     -- diagonal delta
//  Return:
//    Python list of Python tuple:   [ (row, col), ... ]
//
static PyObject* fLevPath(PyObject *self, PyObject* args)
{
      PyObject * list;
      int        rows, cols, delta;
  
      // convert PyObject to appropriate C typed variables
      if (!PyArg_ParseTuple(args, "Oiii", &list, &rows, &cols, &delta)) {
        return Py_None;  
      }
    
      // normalize delta
      delta = (rows - delta - 1) < 0  ? rows - 1 : delta;
      int colsize = delta * 2 + 1;  
    
      // allocate C list to copy calculated values  
      int lsize = PyList_Size(list);
      int i = 0;

      int* data  = malloc(sizeof(int) * lsize);
      if (data == NULL) {
        return PyErr_NoMemory();
      }
            
      // convert Python list to 
      for (i=0; i < lsize; i++) 
      {
         PyObject *item = PyList_GetItem(list, i);
         data[i] = (int)PyInt_AsLong(item);
      }

      // calculate minimal path
      struct CELL *tail = calculate_min_path(data, rows, cols, colsize);
      if (tail == NULL) {
         free(data);
         return PyExc_ValueError;
      }
       
      // convert C array to Python list  [(row, col), ...]
      int       ps     = count_cells(tail); 
      PyObject* result = PyList_New(ps);

      if (result == NULL) {
         free(data);
         free_cells(tail); 
         return PyErr_NoMemory();
      }
    
      i = ps - 1;
      while (tail)
      {
         PyObject* tuple = PyTuple_New(2);
         PyTuple_SetItem(tuple, 0, Py_BuildValue("i", tail->row));      
         PyTuple_SetItem(tuple, 1, Py_BuildValue("i", tail->col));      
         PyList_SetItem(result, i, tuple); 
         tail = (struct CELL*)tail->prev;    
         i--;
      }  
      free(data);
      free_cells(tail);
      return result;
}


PyObject* fLocations(struct CELL* min_path, int rows, int cols, int colsize, PyObject* offsets)      
{      
    struct CELL* t = min_path;
    int          i = 0;
    int          lsize  = PyObject_Size(offsets);
    PyObject*    it     = PyObject_GetIter(offsets);
    PyObject*    result = PyList_New(lsize); 
    PyObject*    item; 
     
    if (result == NULL) {
       return PyErr_NoMemory();
    }
     
    while ((item = PyIter_Next(it)) != NULL) 
    {
       int  offset = (int)PyInt_AsLong(item);
       struct CELL * rt = find_cell_by_row(t, offset);  
       if (rt) 
       {
          PyList_SetItem(result, i, Py_BuildValue("i", rt->col));         
          t = rt->prev;
       }
       else {
          PyList_SetItem(result, i, Py_BuildValue("i", -1));
       }
       
       i++;
       Py_DECREF(item);
    } 
    
    
    Py_DECREF(it);
    return result;
}
 
 
//  Identify locations  
//  input:
//    -- unicode text1
//    -- unicode text2
//    -- delta   (int)
//    -- offsets (Python list)
//  Return:
//    Python list [loc1, loc2, ...]
//
static PyObject* fLevTextAlignment(PyObject* self, PyObject* args) 
{
      Py_UNICODE *text1;
      Py_UNICODE *text2;
      PyObject   *offsets;  
      int    delta, rows, cols;
      float def_value = MAX_FLOAT_VALUE;

      // convert PyObject to appropriate C typed variables
      if (!PyArg_ParseTuple(args, "u#u#iO", &text1, &rows, &text2, &cols, &delta, &offsets)) {
        return Py_None;  
      }

      // normalize delta
      delta = (rows - delta - 1) < 0  ? rows - 1 : delta;
      int colsize = delta * 2 + 1, i = 0;

      // init two columns for calculation and fill it with max value   
      float a_lcol[colsize + 3];
      float a_rcol[colsize + 3];
      
      float *lcol = a_lcol;
      float *rcol = a_rcol;      
      for (i=0; i < colsize + 3; i++) {
          lcol[i] = def_value;
          rcol[i] = def_value;
      }

      // setup initial values for left column
      for (i=0; i< delta + 3; i++) {
          lcol[i] = i;
      }
      
      // setup result array
      int data_size = cols * (colsize + 1);
      float* data = malloc(sizeof(float) * data_size);
      if (data == NULL) {
         return PyErr_NoMemory();
      }
      
      for (i=0; i < data_size; i++) {
          data[i] = def_value;
      }

      // initialize start and end rows indexes
      int l_row1 = 0, l_row2 = delta + 1; 
              
      // slightly speed up access to variable
      int maxrow = rows - 1;
                
      int col = 0, row = 0; 
      for (col=0; col < cols; col++) 
      {
        // calculate anchor row index
        int arow = (int)(((long)col * (long)rows) / (long)cols);
        
        // upper row
        int r_row1 = arow > delta ? arow - delta : 0;
        
        // lower row
        int r_row2 = arow + delta;
        if (r_row2 >= rows) r_row2 = maxrow; 

        lcol[0] = l_row1 == 0 ? col     : lcol[1];   
        rcol[0] = r_row1 == 0 ? col + 1 : def_value;
        
        // to speed up access to array element store it in temporary var
        Py_UNICODE col_ch = text2[col];
              
        // pre-calculated variables slightly speed up loop below
        int drr = 1 - r_row1;
        int dlr = 1 - l_row1;    
        
        // calculate starting index for the given column 
        int index = col * (colsize + 1);
        
        // store starting row to be calculated as the first element 
        data[index] = r_row1;
        index ++;
                    
        // calculate diagonal elements for the given column
        for (row = r_row1; row < r_row2 + 1; row++) 
        { 
          // again pre-compute values to speed up calculation
          int i = row + drr; 
          int j = row + dlr;    
                      
          // compare text and pattern characters 
          if (text1[row] == col_ch) 
          { 
            rcol[i] = lcol[j - 1];
            data[index] = rcol[i];
          }
          else 
          {  
            // the construction below is equivalent of min (a,b,c) 
            // function just to win another thousand milliseconds
            float a = lcol[j], b = rcol[i - 1], c = lcol[j - 1];
            if (a < b) {
                if (c < a) a = c; 
            }
            else {
                a = b < c ? b : c;
            }

            // add weights 
            Py_UNICODE row_ch = text1[row];
            if (Py_UNICODE_TOUPPER(row_ch) == Py_UNICODE_TOUPPER(col_ch)) { 
              a += 0.25;
            }
            else {
              if (Py_UNICODE_ISSPACE(row_ch) && Py_UNICODE_ISSPACE(col_ch)) {
                a += 0.125;
              } 
              else
              { 
                if (Py_UNICODE_ISALNUM(row_ch) && Py_UNICODE_ISALNUM(col_ch)) {
                  a += 1.0;
                }
                else {
                  a += 1.25;
                }
              }
            }

            rcol[i] = a; 
            data[index] = a;
          } 

          index ++;    
        }

        // replace left row reference with just calculated right row
        // since for the next column calculation current right row should 
        // be considered as left row.
        float *a = lcol;
        lcol = rcol;
        rcol = a;
        l_row1 = r_row1; 
        l_row2 = r_row2;
      }
     
      //
      //  Calculate intersection between minimal path and locations
      // 
      struct CELL *tail = calculate_min_path_float(data, rows, cols, colsize);
      free(data);
      if (tail == NULL) {
         return PyExc_ValueError;
      }
      
      PyObject* result = fLocations(tail, rows, cols, colsize, offsets);
      free_cells(tail);
      return result;
}

  
// List of exported (API) methods    
PyMethodDef methods[] = {
    {"fLevDistance",       fLevDistance,       METH_VARARGS, ""},
    {"fLevDistanceMatrix", fLevDistanceMatrix, METH_VARARGS, ""},
    {"fLevDistanceDiag",   fLevDistanceDiag,   METH_VARARGS, ""},
    {"fLevTextAlignment",  fLevTextAlignment,  METH_VARARGS, ""},
    {"fLevPath",           fLevPath,           METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC initclev() {
  (void) Py_InitModule("gravity.tae.match.clev", methods);   
}


