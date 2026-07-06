# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 15:07:00 2026

@author: Yulin Teng
"""

import numpy as np
import matplotlib.pyplot as plt
# from scipy.stats import norm # Uncomment if you need the distribution fitting later

def plot_noisy_symbols(M, symbols, noisy_symbols):
    """
    Plots received noisy symbols, color-coded based on their original ideal symbol.
    """
    # MUS = []
    # SIGZ = []
    
    # Generate a color map with M distinct colors (using 'hsv' to match MATLAB)
    cmap = plt.get_cmap('hsv')
    
    # Create a figure
    plt.figure(figsize=(8, 8))
    
    # Determine the unique original symbols
    unique_symbols = np.unique(symbols)
    num_symbols = len(unique_symbols)
    
    # Calculate the color index spacing
    # Using integer division (//) to match MATLAB's fix()
    color_spacing = M // num_symbols
    
    # noisy_symbols = phaseCorrection(symbols, noisy_symbols)
    
    # Iterate over each unique original symbol
    for i, symbol in enumerate(unique_symbols):
        
        # Find the noisy symbols corresponding to the current original symbol
        # We use boolean masking instead of MATLAB's find() for speed
        mask = (symbols == symbol)
        current_noisy = np.array(noisy_symbols)[mask]
        
        # Calculate the color index based on the symbol index (Python is 0-based)
        color_index = (i * color_spacing) % M
        
        # Get the color from the colormap (matplotlib colormaps take values from 0.0 to 1.0)
        color = cmap(color_index / M)
        
        # Plot the noisy symbols with the corresponding color
        plt.plot(np.real(current_noisy), np.imag(current_noisy), marker='.', linestyle='', color=color, markersize=5)
        
        # =========================================================
        # Commented out distribution fitting (translated to Python)
        # =========================================================
        # mu_real, sigma_real = norm.fit(np.real(current_noisy))
        # mu_imag, sigma_imag = norm.fit(np.imag(current_noisy))
        # 
        # MUS.append(mu_real + mu_imag * 1j)
        # SIGZ.append(sigma_real + sigma_imag * 1j)
        
    # Set the title and labels for the plot
    plt.title('Noisy Symbols')
    plt.xlabel('Real Part')
    plt.ylabel('Imaginary Part')
    
    # Ensure axes are scaled equally so the constellation isn't stretched
    plt.axis('equal')
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Create a legend for the different original symbols
    # plt.legend([str(sym) for sym in unique_symbols], loc='best')
    
    plt.show()
    
    # plt.figure()
    # plt.plot(np.real(MUS), np.imag(MUS), "o")
    # plt.show()