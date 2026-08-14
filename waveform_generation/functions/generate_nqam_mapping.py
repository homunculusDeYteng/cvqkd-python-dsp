# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 11:24:54 2026

@author: Yulin Teng
"""

import math
import numpy as np


def generateNQAMMapping(N: int):
    """
    Generate the symbol mapping for N-QAM.

    N must be a perfect square (e.g. 4, 16, 64, 256).
    Symbols are enumerated row by row, varying the imaginary component
    in the inner loop.

    Parameters
    ----------
    N : int
        Constellation size (number of unique symbols).

    Returns
    -------
    mapping : np.ndarray of complex, shape (N,)
        Flat array of constellation points.
    """
    side = int(math.sqrt(N))
    if side * side != N:
        raise ValueError(f"N must be a perfect square, got {N}.")

    # Axis values: -side+1, -side+3, ..., side-1  (step = 2)
    axis = np.arange(-(side - 1), side, 2, dtype=float)

    # Build grid via meshgrid and flatten row-major (matches the nested loop order)
    real_grid, imag_grid = np.meshgrid(axis, axis, indexing='ij')
    mapping = (real_grid + 1j * imag_grid).ravel()

    return mapping