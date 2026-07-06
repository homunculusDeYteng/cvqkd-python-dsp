# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 10:30:17 2026

@author: Yulin Teng
"""

import numpy as np


def QPSK(data):
    '''
    Description :
    This function modulates the data with QPSK modulation.
   
    Parameters :
    data = data te be modulated

    Example :
    00  ==> 3/4*pi  ==> -1+1*1i
    01  ==> 5/4*pi  ==> -1-1*1i 
    10  ==> 1/4*pi  ==> 1+1*1i
    11  ==> 7/4*pi  ==> 1-1*1i
    '''
    #Ensure the input is a numpy array
    data = np.array(data)
    
    # Reshape into pairs
    # reshape(-1, 2) tells numpy to figure out the number of rows (-1) 
    # but strictly enforce 2 columns. 
    data_pairs = data.reshape(-1, 2)
    
    # Convert bit pairs to decimal (0, 1, 2, or 3)
    # This multiplies the first column by 2 and adds the second column.
    position = data_pairs[:, 0] * 2 + data_pairs[:, 1]
    
    # Pre-allocate the output array
    # dtype=complex ensures numpy knows this array will hold imaginary numbers
    dataMod = np.zeros(len(position), dtype=complex)
    
    # Map the symbols using boolean indexing
    dataMod[position == 0] = -1 + 1j
    dataMod[position == 1] = -1 - 1j
    dataMod[position == 2] =  1 + 1j
    dataMod[position == 3] =  1 - 1j
    
    return dataMod