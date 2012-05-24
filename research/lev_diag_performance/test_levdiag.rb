


$MAX_VALUE = 1000000000
 
# delta is number of row elements to be calculated above and below the central  
# diagonal element  

def calculate_diag(text, pattern, delta)
    # defines size of matrix 
    rows, cols = text.length, pattern.length    
    
    # initialize column data 
    colsize = delta * 2 + 1     # number of row elements to be calculated per column
   
    # init column arrays to keep prev. calculated results and current results
    lcol = Array.new(colsize + 3, $MAX_VALUE)
    rcol = Array.new(colsize + 3, $MAX_VALUE)
    
    # init left column data
    for i in 0..(delta + 2) 
        lcol[i] = i
    end

    # initialize array to keep result data
    # this is the plain array where every calculated row diagonal 
    # elements are placed in fixed sized slot - (colsize + 1). The first (extra)
    # element in the slot is used to keep first row index the data have been
    # calculated. array is pre-filled with MAX_VALUE to make difference between
    # elements that have been calculated and untouchable elements.  
    data = Array.new((cols * (colsize + 1)), $MAX_VALUE)
    
    # initialize start and end rows indexes
    l_row1, l_row2, l_col = 0, delta + 1, -1 
    
    # slightly speed up access to variable
    maxrow = rows - 1

    for col in 0..(cols-1)
        # calculate anchor row index
        arow = (col * rows) / cols
        
        # upper row
        r_row1 = arow > delta  ? arow - delta : 0
        
        # lower row
        r_row2 = arow + delta
        if (r_row2 >= rows) 
            r_row2 = maxrow 
        end
        
        lcol[0] = l_row1 == 0 ? col     : $MAX_VALUE   
        rcol[0] = r_row1 == 0 ? col + 1 : $MAX_VALUE
        
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
        for row in r_row1..r_row2 
            # again pre-compute values to speed up calculation
            i, j = row + drr, row + dlr    
                        
            # compare text and pattern characters 
            if (text[row] == col_ch) 
                rcol[i] = lcol[j - 1]
                data[index] = rcol[i]
            else  
                # the construction below is equivalent of min (a,b,c) 
                # function just to win another thousand milliseconds
                a,b,c = lcol[j], rcol[i - 1], lcol[j - 1]
                
               # puts a, b, j
                
                if (a < b)
                    if (c < a) 
                        a = c
                    end     
                else
                    a = b < c  ? b : c
                end
           
                a += 1              
                rcol[i] = data[index] = a 
            end

            index += 1    
        end
        
        # replace left row reference with just calculated right row
        # since for the next column calculation current right row should 
        # be considered as left row.
        a, lcol = lcol, rcol
        rcol = a
        l_row1, l_row2 = r_row1, r_row2
    end
    
    return data
end


#
# dirty code just to visualize results
#
def print_result(s1, s2, delta, res)
    rows, cols = s1.length, s2.length
    colsize = delta * 2 + 1
 
    buf = ''
    for row in 0..(rows-1)
        puts row
        for col in 0..(cols-1)
            index  = (colsize + 1) * col
            srow   = res[index]
            index  += 1
            i      = index + row - srow
            
            if (row < srow || row >= srow + colsize || res[i] == $MAX_VALUE) 
                buf += " xx "
            else
                buf += " " + res[i].to_s + " "      
            end
         end
     end       
        buf += "\n"
                
    print buf
end

def test1()
    # test input data
    delta = 3
    s1    = "asdffghjjkll"
    s2    = "sxcvbbnhmkjkjkjhjkg"

    r = calc(s1, s2, delta)
    print_result(s1, s2, delta, r)
end

def test2()
    # load input data located in file  
    delta = 100 
    s1 = IO.readlines('test.txt','r:UTF-8').to_s 
    s2 = IO.readlines('test2.txt','r:UTF-8').to_s 
    calc(s1, s2, delta)
end

def calc(s1, s2, delta)
    puts "Input data : s1.len = " + s1.length.to_s + ", s2.len = " + s2.length.to_s + ", delta = " + delta.to_s

    # calculate diagonal
    t = Time.new
    r = calculate_diag(s1, s2, delta)
    puts (Time.new - t)

    # last element index
    i = (delta * 2 + 2) * (s2.length-1) + delta + 1
    puts "Last elements: ", r[i], r[i-1] 
        
    return r
end




test2()

