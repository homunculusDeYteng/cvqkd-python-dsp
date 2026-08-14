# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 11:12:39 2026

@author: Yulin Teng
"""


import math
import numpy as np
# import matplotlib.pyplot as plt

_TAPS = {
     3: [3, 2],
     4: [4, 3],
     5: [5, 3],
     6: [6, 5],
     7: [7, 6],
     8: [8, 6, 5, 4],
     9: [9, 5],
    10: [10, 7],
    11: [11, 9],
    12: [12, 6, 4, 1],
    13: [13, 4, 3, 1],
    14: [14, 5, 3, 1],
    15: [15, 14],
    16: [16, 15, 13, 4],
    17: [17, 14],
    18: [18, 11],
    19: [19, 6, 2, 1],
    20: [20, 17],
    21: [21, 19],
    22: [22, 21],
    23: [23, 18],
    24: [24, 23, 22, 17],
    25: [25, 22],
}


def LFSR(output_length: int, shift_reg_length: int = None):
    """
    Generate a pseudo-random binary sequence using a Fibonacci LFSR.

    The register is initialised to [1, 0, 0, ..., 0] (fixed seed).
    The first (shift_reg_length - 1) output bits are discarded to avoid
    the high-PAPR transient caused by the all-zero initial state.

    Parameters
    ----------
    output_length : int
        Number of bits to return.
    shift_reg_length : int, optional
        Length of the shift register. If omitted, the minimum length
        required to cover output_length without repeating is used.

    Returns
    -------
    output : np.ndarray of int, shape (output_length,)
        The generated bit sequence.
    shift_reg_length : int
        The register length that was used.
    """
    if shift_reg_length is None:
        shift_reg_length = math.ceil(math.log2(output_length + 1))

    if shift_reg_length not in _TAPS:
        raise ValueError(
            f"No tap table entry for shift register length {shift_reg_length}. "
            f"Supported lengths: {sorted(_TAPS)}."
        )

    taps = _TAPS[shift_reg_length]

    shift_reg = [1] + [0] * (shift_reg_length - 1)

    # Generate (output_length + shift_reg_length - 1) bits, then trim the head
    total_len = output_length + shift_reg_length - 1
    raw = np.zeros(total_len, dtype=int)

    for k in range(total_len):
        raw[k] = shift_reg[-1]

        feedback = shift_reg[taps[0] - 1]
        for tap in taps[1:]:
            feedback ^= shift_reg[tap - 1]

        shift_reg = [feedback] + shift_reg[:-1]

    output = raw[shift_reg_length - 1:]
    return output, shift_reg_length


