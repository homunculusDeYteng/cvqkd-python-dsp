# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 14:24:07 2026

@author: Yulin Teng
"""
import numpy as np
import math

def encodeBitsToSymbols(bits, mapping):
    """
    bits: Input bit sequence (binary vector)
    mapping: Symbol mapping table (complex vector)
    """
    # Ensure bits is a numpy array for mathematical operations
    bits = np.array(bits)
    
    # Calculate how many bits represent one symbol
    bits_per_symbol = int(math.log2(len(mapping)))
    
    # Check if the number of bits is compatible with the mapping
    if len(bits) % bits_per_symbol != 0:
        print(len(bits))
        print(bits_per_symbol)
        raise ValueError('The number of bits is not compatible with the mapping.')
        
    # Reshape the bit sequence into groups of log2(length(mapping)) bits
    # -1 tells numpy to automatically calculate the required number of rows
    numSymbols = len(bits) // bits_per_symbol
    bitGroups = bits.reshape(-1, bits_per_symbol)
    
    # Initialize the symbol sequence
    # dtype=complex ensures the array can hold the I-Q plane coordinates
    symbols = np.zeros(numSymbols, dtype=complex)
    
    # Convert each bit group to the corresponding symbol using the mapping
    for i in range(numSymbols):
        bitGroup = bitGroups[i, :]
        
        # Binary to Decimal conversion ('left-msb')
        # We join the array of bits into a string (e.g., "101100") 
        # and use int(..., 2) to convert that base-2 string into a standard decimal integer.
        bit_string = "".join(str(int(b)) for b in bitGroup)
        symbolIndex = int(bit_string, 2)
        
        # Map to the complex symbol
        symbols[i] = mapping[symbolIndex]
        
    return symbols
