

import array

MAX_VALUE = 1000000000
 
# delta is number of row elements to be calculated above and below the central  
# diagonal element  
def calculate_diag(text, pattern, delta):
    # defines size of matrix 
    rows, cols = len(text), len(pattern)    
    

    # initialize column data 
    colsize = delta * 2 + 1     # number of row elements to be calculated per column
   
    # init column arrays to keep prev. calculated results and current results
    lcol, rcol = [ MAX_VALUE ]*(colsize + 3), [ MAX_VALUE ]*(colsize + 3)  
    
    # init left column data
    for i in range(delta + 3): lcol[i] = i
    

    # initialize array to keep result data
    # this is the plain array where every calculated row diagonal 
    # elements are placed in fixed sized slot - (colsize + 1). The first (extra)
    # element in the slot is used to keep first row index the data have been
    # calculated. array is pre-filled with MAX_VALUE to make difference between
    # elements that have been calculated and untouchable elements.  
    #data = [MAX_VALUE] * (cols * (colsize + 1))
    data = array.array("i", [MAX_VALUE] * (cols * (colsize + 1)))
    
    
    # initialize start and end rows indexes
    l_row1, l_row2, l_col = 0, delta + 1, -1 
    
    # slightly speed up access to variable
    maxrow = rows - 1

    for col in range(cols):
        # calculate anchor row index
        arow = ((col * rows) // cols)
        
        # upper row
        r_row1 = arow - delta if arow > delta else 0
        
        # lower row
        r_row2 = arow + delta
        if r_row2 >= rows: r_row2 = maxrow 

        lcol[0] = col     if l_row1 == 0 else MAX_VALUE   
        rcol[0] = col + 1 if r_row1 == 0 else MAX_VALUE
        
        # to speed up access to array element store it in temporary var
        col_ch = pattern[col]
        
        # pre-calculated variables slightly speed up loop below
        drr, dlr = 1 - r_row1, 1 - l_row1    
        
        # calculate starting index for the given column 
        index = col * (colsize + 1)
        
        # store starting row to be calculated as the first element 
        data[index] = r_row1
        index += 1
        
        # calculate diagonal elements for the given column
        for row in range(r_row1, r_row2 + 1, 1): 
            # again pre-compute values to speed up calculation
            i, j = row + drr, row + dlr    
                        
            # compare text and pattern characters 
            if text[row] == col_ch: 
                rcol[i] = lcol[j - 1]
                data[index] = rcol[i]
            else:  
                # the construction below is equivalent of min (a,b,c) 
                # function just to win another thousand milliseconds
                a,b,c = lcol[j], rcol[i - 1], lcol[j - 1]
                if a < b:
                    if c < a: a = c 
                else:
                    a = b if b < c else c

                a += 1              
                rcol[i] = data[index] = a 
              
            index += 1    
        
        # replace left row reference with just calculated right row
        # since for the next column calculation current right row should 
        # be considered as left row.
        a, lcol = lcol, rcol
        rcol = a
        l_row1, l_row2 = r_row1, r_row2

    return data



#
# dirty code just to visualize results
#
def print_result(s1, s2, delta, res):
    rows, cols = len(s1), len(s2)
    colsize = delta * 2 + 1
 
    buf = ''
    for row in range(rows):
        for col in range(cols):
            index  = (colsize + 1) * col
            srow   = res[index]
            index  += 1
            i      = index + row - srow
            
            if row < srow or row >= srow + colsize or res[i] == MAX_VALUE: 
                buf += " xx "
            else:
                buf += " %2d " % res[i]    
        
        buf += "\n"
                
    print (buf)


def test1():
    # test input data
    delta = 3
    s1    = "asdffghjjkll"
    s2    = "sxcvbbnhmkjkjkjhjkg"

    r = calc(s1, s2, delta)
    print_result(s1, s2, delta, r)
        

def test2():
    # load input data located in file  
    delta = 100 
    import os, codecs 
    f = codecs.open(os.path.join(os.path.dirname(__file__), "test.txt"), 'r', "utf-8") 
    s1 = f.read()         
    f.close()
    f = codecs.open(os.path.join(os.path.dirname(__file__), "test2.txt"), 'r', "utf-8") 
    s2 = f.read()         
    f.close()
    calc(s1, s2, delta)


def calc(s1, s2, delta):
    print ("Input data : s1.len = ", len(s1), ", s2.len = ", len(s2), ", delta = ", delta)


    # calculate diagonal
    import time
    t = time.time()
    r = calculate_diag(s1, s2, delta)
    print (time.time() - t)

    # last element index
    i = (delta * 2 + 2) * (len(s2)-1) + delta + 1
    print ("Last elements: ", r[i], r[i-1]) 
        
    return r


test2()


