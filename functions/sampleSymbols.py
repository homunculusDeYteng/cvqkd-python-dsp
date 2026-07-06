# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 14:00:52 2026

@author: Yulin Teng
"""

import numpy as np
import math

def sampleSymbols(N, mapping, nu):
    """
    SAMPLESYMBOLS - Sample symbols from the QAM mapping using a discrete Gaussian distribution.
    N: Number of symbols to sample.
    mapping: Constellation points from the QAM mapping.
    nu: Parameter controlling the Gaussian spread.
    """
    # Calculate size of mapping grid
    M = len(mapping)
    m = int(math.sqrt(M))

    # Generate Gaussian-based probabilities for each constellation point
    probabilities = np.zeros((m, m))
    
    index = 0 
    for x in range(m):
        for y in range(m):
            # Extract in-phase and quadrature components
            realPart = np.real(mapping[index])
            imagPart = np.imag(mapping[index])

            # Apply Gaussian distribution: p ∝ exp(-nu * (x^2 + y^2))
            probabilities[x, y] = np.exp(-nu * (realPart**2 + imagPart**2))
            index += 1

    # Normalize probabilities so they sum to 1
    probabilities = probabilities / np.sum(probabilities)

    # Sample symbols using the generated probabilities
    # np.random.choice requires a 1D array of probabilities, so we flatten it
    indices = np.random.choice(M, size=int(N), replace=True, p=probabilities.flatten())
    
    # Use .copy() to ensure we don't accidentally modify the original mapping array
    symbols = mapping[indices].copy() 

    # Ensure every symbol appears at least once
    # We use a Python 'set' for replaced_indexes because lookups are significantly faster than lists
    replaced_indexes = set() 
    
    for k in range(M):
        # np generates an integer from low (inclusive) to high (exclusive)
        index_to_replace = np.random.randint(0, len(symbols))
        kk = 0
        
        while (index_to_replace in replaced_indexes) and (kk < 10000):
            index_to_replace = np.random.randint(0, len(symbols))
            kk += 1
            
        replaced_indexes.add(index_to_replace)
        symbols[index_to_replace] = mapping[k]

    return symbols