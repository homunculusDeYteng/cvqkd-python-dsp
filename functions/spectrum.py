# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 11:47:52 2026

@author: Yulin Teng
"""

import numpy as np
import matplotlib.pyplot as plt

def spectrum(signal, fs, title_str):
    """
    Plots the power spectral density (frequency spectrum) of a complex signal.
    """
    plt.figure()
    
    # plt.psd automatically calculates the FFT, converts it to Decibels (dB), 
    # and generates the correct frequency x-axis based on your sampling rate (fs).
    plt.psd(signal, NFFT=2048, Fs=fs, color='blue')
    
    plt.title(title_str)
    
    # Convert x-axis labels to GHz for easier reading
    ax = plt.gca()
    ticks = ax.get_xticks()
    ax.set_xticklabels([f'{tick/1e9:g}' for tick in ticks])
    plt.xlabel('Frequency (GHz)')
    
    plt.show()