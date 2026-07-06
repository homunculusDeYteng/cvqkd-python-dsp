# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 13:40:36 2026

@author: Yulin Teng
"""

import numpy as np
import matplotlib.pyplot as plt

def drawConstellation(signal, title_str):
    """
    Plots the constellation diagram of complex symbols on the I-Q plane.
    """
    plt.figure(figsize=(6, 6))
    
    # Scatter plot: Real parts on X, Imaginary parts on Y
    plt.scatter(np.real(signal), np.imag(signal), color='blue', alpha=0.6, marker='.')
    
    plt.title(title_str)
    plt.xlabel('In-Phase (I)')
    plt.ylabel('Quadrature (Q)')
    
    plt.grid(True)
    plt.axis('equal')
    
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    
    plt.show()