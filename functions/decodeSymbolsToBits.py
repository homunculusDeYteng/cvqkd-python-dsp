# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 14:24:08 2026

@author: admin
"""

import numpy as np
import math

def decodeSymbolsToBits(symbols, mapping):
    #symbols: Input symbol sequence (complex vector)
    #mapping: Symbol mapping table (complex vector)
    
    # Calculate bits per symbol (e.g., log2(64) = 6)
    bits_per_symbol = int(math.log2(len(mapping)))
    
    # Initialize the bit sequence
    numBits = len(symbols) * bits_per_symbol
    bits = np.zeros(numBits, dtype=int)
    
    # Convert each symbol to the corresponding bit group using the mapping
    for i in range(len(symbols)):
        symbol = symbols[i]
        
        symbolIndex = np.argmin(np.abs(symbol - mapping))
        
        # Decimal to Binary conversion ('left-msb')
        # We format the integer as a binary string with leading zeros.
        # Example: if bits_per_symbol is 6, the number 3 becomes '000011'
        bit_string = format(symbolIndex, f'0{bits_per_symbol}b')
        
        # Convert the string of characters into a list of integers [0, 0, 0, 0, 1, 1]
        bitGroup = [int(b) for b in bit_string]
        
        # Calculate the start and end positions for this chunk of bits
        start_idx = i * bits_per_symbol
        end_idx = (i + 1) * bits_per_symbol
        
        # Assign to the main bits array
        bits[start_idx:end_idx] = bitGroup
        
    return bits