# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 11:28:53 2026

@author: Yulin Teng
"""

import math
import numpy as np


def encodeBitsToSymbols(bits: np.ndarray, mapping: np.ndarray):
    """
    Encode a binary sequence into QAM symbols.

    Parameters
    ----------
    bits : array-like of int
        Flat bit sequence.  Length must be a multiple of log2(len(mapping)).
    mapping : np.ndarray of complex, shape (M,)
        Constellation map produced by generateNQAMMapping.

    Returns
    -------
    symbols : np.ndarray of complex, shape (len(bits) // bits_per_symbol,)
    """
    bits = np.asarray(bits, dtype=int)
    M = len(mapping)
    bits_per_symbol = int(math.log2(M))

    if len(bits) % bits_per_symbol != 0:
        raise ValueError(
            f"Bit sequence length ({len(bits)}) is not a multiple of "
            f"bits_per_symbol ({bits_per_symbol}) for a {M}-QAM mapping."
        )

    
    bit_groups = bits.reshape(-1, bits_per_symbol)
    powers = 2 ** np.arange(bits_per_symbol - 1, -1, -1)
    indices = bit_groups @ powers   # shape: (num_symbols,)

    return mapping[indices]