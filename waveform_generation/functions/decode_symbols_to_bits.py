# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 11:32:47 2026

@author: Yulin Teng
"""
import math
import numpy as np


def decodeSymbolsToBits(symbols: np.ndarray, mapping: np.ndarray):
    """
    Decode QAM symbols to a binary sequence (hard decision).

    Parameters
    ----------
    symbols : array-like of complex
        Received symbol sequence.
    mapping : np.ndarray of complex, shape (M,)
        Constellation map produced by generateNQAMMapping.

    Returns
    -------
    bits : np.ndarray of int, shape (len(symbols) * bits_per_symbol,)
    """
    symbols = np.asarray(symbols)
    M = len(mapping)
    bits_per_symbol = int(math.log2(M))

    
    distances = np.abs(symbols[:, np.newaxis] - mapping[np.newaxis, :])
    indices = np.argmin(distances, axis=1)  # shape: (len(symbols),)

    powers = 2 ** np.arange(bits_per_symbol - 1, -1, -1)
    bit_matrix = ((indices[:, np.newaxis] & powers) > 0).astype(int)

    return bit_matrix.ravel()