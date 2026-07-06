# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 11:20:01 2026

@author: Yulin Teng
"""

import numpy as np

def RRC_filter(Ax, Bbaud, beta, Bo):
    """
    Applies a Root-Raised-Cosine filter in the frequency domain.
    Matches the original MATLAB implementation.
    """
    
    '''
    Ax: input signal, time-domain waveform
    Bbaud: baud rate 
    beta: roll-off factor
    Bo: sampling rate
    '''
    total_samples = len(Ax)
    
    # Create the frequency axis
    f = np.arange(-total_samples // 2 + 1, total_samples // 2 + 1) / total_samples
    f = f * Bo
    
    # Find the index boundaries for the piecewise filter shape
    f_low_negative = np.argmax(f >= -(1 - beta) * Bbaud / 2)
    f_high_negative = np.argmax(f >= -(1 + beta) * Bbaud / 2)
    f_low_positive = np.argmax(f >= (1 - beta) * Bbaud / 2)
    f_high_positive = np.argmax(f >= (1 + beta) * Bbaud / 2)
    
    # Calculate the Raised Cosine (RC) frequency response
    H_RC = 0.5 * (1 + np.cos(np.pi / (beta * Bbaud) * (np.abs(f) - (1 - beta) * Bbaud / 2)))
    
    # Apply the piecewise boundaries
    H_RC[:f_high_negative] = 0.0                      # Stopband (negative freq)
    H_RC[f_high_positive:] = 0.0                      # Stopband (positive freq)
    H_RC[f_low_negative:f_low_positive] = 1.0         # Passband (flat top)
    
    # Convert Raised Cosine to Root Raised Cosine
    H_RRC = np.sqrt(H_RC)
    
    # Safety check for bad data
    if np.isnan(Ax).any():
        raise ValueError('Signal contains NaN, cannot filter')
        
    # Apply the filter in the frequency domain
    # fftshift aligns the zero-frequency component of the filter with the FFT output
    filtered_signal = np.fft.ifft(np.fft.fft(Ax) * np.fft.fftshift(H_RRC))
    
    return filtered_signal