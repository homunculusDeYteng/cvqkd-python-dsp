# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 11:33:45 2026

@author: Yulin Teng
"""

import numpy as np


def RRC_filter(
    signal: np.ndarray,
    baud_rate: float,
    roll_off: float,
    sample_rate: float,
):
    """
    Apply an RRC filter to a signal in the frequency domain.

    Parameters
    ----------
    signal : np.ndarray
        Time-domain input waveform (may be complex).
    baud_rate : float
        Symbol rate in Hz.
    roll_off : float
        Roll-off factor β ∈ [0, 1].
    sample_rate : float
        Sampling rate of the signal in Hz.

    Returns
    -------
    filtered : np.ndarray
        Filtered time-domain signal (same length and dtype as input).

    Raises
    ------
    ValueError
        If the signal contains NaN values.
    """
    if np.isnan(signal).any():
        raise ValueError("Input signal contains NaN values — cannot filter.")

    N = len(signal)

    # Frequency axis centred at zero, spanning [-fs/2, fs/2)
    f = np.fft.fftfreq(N, d=1.0 / sample_rate)
    f = np.fft.fftshift(f)

    f_abs = np.abs(f)
    f_low  = (1 - roll_off) * baud_rate / 2
    f_high = (1 + roll_off) * baud_rate / 2

    # Raised Cosine response (piecewise)
    H_RC = np.where(
        f_abs <= f_low,
        1.0,
        np.where(
            f_abs < f_high,
            0.5 * (1 + np.cos(np.pi / (roll_off * baud_rate) * (f_abs - f_low))),
            0.0,
        ),
    )

    H_RRC = np.sqrt(H_RC)

    # Multiply in the frequency domain (fftshift aligns the filter with FFT output)
    filtered = np.fft.ifft(np.fft.fft(signal) * np.fft.fftshift(H_RRC))

    return filtered