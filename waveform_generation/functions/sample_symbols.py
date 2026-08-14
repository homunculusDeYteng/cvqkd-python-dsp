# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 11:27:22 2026

@author: Yulin Teng
"""


import math
import numpy as np


def sampleSymbols(N: int, mapping: np.ndarray, nu: float):
    """
    Sample N symbols from a QAM constellation with Gaussian shaping.

    Parameters
    ----------
    N : int
        Number of symbols to draw.
    mapping : np.ndarray of complex, shape (M,)
        Flat array of constellation points (from generateNQAMMapping).
    nu : float
        Gaussian shaping parameter. Larger ν concentrates probability mass
        near the origin (tighter Gaussian).

    Returns
    -------
    symbols : np.ndarray of complex, shape (N,)
        Sampled symbol sequence.
    """
    M = len(mapping)

    # --- Build the discrete Gaussian probability vector ---
    energy = np.real(mapping) ** 2 + np.imag(mapping) ** 2
    weights = np.exp(-nu * energy)
    probabilities = weights / weights.sum()

    # --- Draw N symbols according to the shaped distribution ---
    indices = np.random.choice(M, size=N, replace=True, p=probabilities)
    symbols = mapping[indices].copy()

    # --- Guarantee every constellation point appears at least once ---
    
    used_positions = set()
    for k in range(M):
        pos = np.random.randint(0, N)
        retries = 0
        while pos in used_positions and retries < 10_000:
            pos = np.random.randint(0, N)
            retries += 1
        used_positions.add(pos)
        symbols[pos] = mapping[k]

    return symbols