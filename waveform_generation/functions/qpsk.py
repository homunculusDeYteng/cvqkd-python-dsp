# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 11:16:22 2026

@author: Yulin Teng
"""



import numpy as np


_QPSK_MAP = np.array([-1 + 1j, -1 - 1j, 1 + 1j, 1 - 1j])


def QPSK(data: np.ndarray):
    """
    Modulate a binary sequence with QPSK.

    Parameters
    ----------
    data : array-like of int
        Flat bit sequence. Length must be even.

    Returns
    -------
    symbols : np.ndarray of complex, shape (len(data) // 2,)
        QPSK symbols.
    """
    data = np.asarray(data, dtype=int)

    if data.size % 2 != 0:
        raise ValueError(f"Input length must be even, got {data.size}.")

    # Group bits into pairs and convert to decimal index (MSB first)
    pairs = data.reshape(-1, 2)
    indices = pairs[:, 0] * 2 + pairs[:, 1]

    return _QPSK_MAP[indices]