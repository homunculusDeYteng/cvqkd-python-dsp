# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 13:44:25 2026

@author: Yulin Teng
"""

import numpy as np
import math

def generateNQAMMapping(N):
    # N: Number of unique symbols in the mapping (N-QAM)
    
    # Calculate the number of bits per symbol
    numBits = math.log2(N)
    
    # Generate the mapping for N-QAM
    mapping = np.zeros(int(N), dtype=complex)
    
    # IMPORTANT: Python uses 0-based indexing, so we must start at 0 instead of 1
    symbolIndex = 0 
    
    # Calculate the maximum and minimum values for the in-phase and quadrature components
    maxComponentValue = math.sqrt(N) - 1
    minComponentValue = -maxComponentValue
    
    # Generate all possible combinations of the in-phase and quadrature components
    # np.arange(start, stop, step) - We add 0.1 to the stop value to ensure it includes the max value
    axis_values = np.arange(minComponentValue, maxComponentValue + 0.1, 2)
    
    for x in axis_values:
        for y in axis_values:
            mapping[symbolIndex] = complex(x, y)
            symbolIndex = symbolIndex + 1
            
    return mapping