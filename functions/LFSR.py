# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 14:45:46 2026

@author: Yulin Teng
"""

import math
import numpy as np
import matplotlib.pyplot as plt


def LFSR(output_length,shift_reg_length = None):
    
    # LFSR : Linear Feedback Shift Register
    #
    # Description :
    #   This function uses the Fibonacci implementation of LFSR
    #   which consists of a simple shift register in which a modulo-2 sum of
    #   the binary-weighted taps is fed back to the input.
    #   (The modulo-2 sum of two 1-bit binary numbers yields 0 if the two
    #numbers are identical, and 1 if the differ: 0+0=0, 0+1=1, 1+1=0.)
    #   
    # Parameters :
    #   outputLength   = length of the data to be generated
    #   shift_reg_length = bit length of the shift register
    
    
    
    # Note that the register only has length 2^n-1 before it starts repeating
    
    if shift_reg_length is None:
        #Determine the shift register length according to the data length
        shift_reg_length = math.ceil(math.log2(output_length +1))
    
    '''
    else:
        #Check output length to prevent LFSR from looping
        output_length_max = (2**shift_reg_length)-1
        
        if output_length > output_length_max:
            raise ValueError(f'Output data length cannot exeed 2**shift_reg_length - 1')
    '''
    
    #-------------------Start value of the shiftReg---------------------------#
    ##First option : random
    ##np.random.randint generates random integers from the first number (inclusive)
    ##.tolist() converts the numpy array back into a standard python list
    # shift_reg = np.random.randint(0, 2, shift_reg_length).tolist()
    
    # Second option : fixed
    #The first shift_reg_length bits are zeros, so after the modulation, some
    #successive subcarriers of the first symbol are the same, which can cause
    #a big PAPR for the first symbol.
    shift_reg = [1] + [0] * (shift_reg_length - 1)
    
    #----------------------Primitive polynomials------------------------------#
    #Taps for maximum-length LFSR
    taps_dict = {
        3:[3, 2],
        4:[4, 3],
        5:[5, 3],
        6:[6, 5],
        7:[7, 6],
        8:[8, 6, 5, 4],
        9:[9, 5],
        10:[10, 7],
        11:[11, 9],
        12:[12, 6, 4, 1],
        13:[13, 4, 3, 1],
        14:[14, 5, 3, 1],
        15:[15, 14],
        16:[16, 15, 13, 4],
        17:[17, 14],
        18:[18, 11],
        19:[19, 6, 2, 1],
        20:[20, 17],
        21:[21, 19],
        22:[22, 21],
        23:[23, 18],
        24:[24, 23, 22, 17],
        25:[25, 22]
        }
    if shift_reg_length not in taps_dict:
        raise ValueError(f'This shift register (length : {shift_reg_length}) is not recorded in the tap table.')
        
    taps = taps_dict[shift_reg_length]
    
    #-------------------------Generate output---------------------------------#
    total_len = int(output_length + shift_reg_length - 1)
    output = np.zeros(total_len, dtype=int)
    
    for k in range(total_len):
        # Pull the output of the register (the last bit)
        output[k] = shift_reg[-1]
        
        #calculate the feedback using bitwise XOR (modulo -2 sum)
        feed_back = shift_reg[taps[0] - 1]
        for i in range(1,len(taps)):
            feed_back = feed_back ^ shift_reg[taps[i] - 1]  #^ is the XOR operator
            
        #Insert that value in the beginning and shift the rest to the right
        shift_reg = [feed_back] + shift_reg[:-1]
    
    #Remove the first shiftRegLength-1 bits, because they cause a big PAPR
    output = output[shift_reg_length - 1:]
    
    

    #--------------------------Autocorrelation--------------------------------#
    ##To see how uncorrelated the output is
    plt.figure()
    autocorr = np.correlate(output, output, mode='full')
    plt.plot(autocorr)
    plt.title('Autocorrelation of the output of LFSR')
    plt.show()
    
    #----------------------Primitive polynomial check-------------------------#
    ##To see if the data repeat
    plt.figure()
    first_part_length = 100
    first_part = output[:first_part_length]
    
    corr = np.full(len(output),np.nan)
    
    for k in range(len(output)- first_part_length + 1):
        window = output[k: k + first_part_length]
        
        corr[k] = np.sum(window == first_part)
        
    plt.plot(corr)
    plt.xlabel('Data')
    plt.ylabel('Correlation with the first 100 points')
    plt.title('Primitive polynomial check for LFSR')
    plt.show()
    
    return output, shift_reg_length
    
    

if __name__ == '__main__':
    
    test_len = 50000
    reg_len = 15
    
    print(f"Generating {test_len} bits...")
    bit_sequence, final_reg_len = LFSR(test_len, reg_len)
    
    print("Done!")
    print(f'Total bits generated: {len(bit_sequence)}')
    print(f'First 20 bits: {bit_sequence[:20]}')
        
        
                                     