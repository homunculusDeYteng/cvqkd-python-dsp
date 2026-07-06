# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 14:40:45 2026

@author: Yulin Teng
"""


from functions.generateNQAMMapping import generateNQAMMapping
from functions.sampleSymbols import sampleSymbols

import numpy as np
import matplotlib.pyplot as plt

def plotSymbolHistogram(symbols, numBins):
    """
    Creates a 3D histogram of complex symbols showing the probability distribution
    over the I-Q (Real-Imaginary) plane.
    """
    # Extract the real and imaginary parts of the symbols
    realPart = np.real(symbols)
    imagPart = np.imag(symbols)

    hist, xedges, yedges = np.histogram2d(realPart, imagPart, bins=numBins)

    # Dividing the counts in each bin by the total number of symbols ensures the volume sums to 1
    prob = hist / len(symbols)

    # Set up the 3D figure
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    xpos, ypos = np.meshgrid(xedges[:-1], yedges[:-1], indexing="ij")
    xpos = xpos.ravel()
    ypos = ypos.ravel()
    zpos = np.zeros_like(xpos) # All bars start at Z = 0

    # Construct arrays for the dimensions (width, depth, height) of the bars
    dx = xedges[1] - xedges[0]
    dy = yedges[1] - yedges[0]
    dx_arr = np.ones_like(xpos) * dx
    dy_arr = np.ones_like(ypos) * dy
    dz = prob.ravel() # The height of the bars is the probability

    cmap = plt.get_cmap('viridis')
    # Normalize colors based on the maximum probability so the tallest bars are the brightest
    norm = plt.Normalize(0, np.max(dz)) if np.max(dz) > 0 else plt.Normalize(0, 1)
    colors = cmap(norm(dz))

    # Draw the 3D bar chart
    ax.bar3d(xpos, ypos, zpos, dx_arr, dy_arr, dz, color=colors, shade=True)

    # Format the axes and labels
    ax.set_xlabel('Real Part')
    ax.set_ylabel('Imaginary Part')
    ax.set_zlabel('Probability')
    plt.title('Symbol Histogram')

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, pad=0.1)

    plt.show()
    
    
# ==========================================
# 3D Histogram Test Block
# ==========================================
if __name__ == "__main__":
    print("Generating test constellation...")
    
    # 1. Define the parameters from your main script
    M = 64          # 64-QAM
    nu = 0.0749     # Gaussian spread parameter
    N = 15000       # Generate 15,000 symbols to get a smooth, dense histogram
    
    # 2. Generate the QAM mapping grid
    mapping = generateNQAMMapping(M)
    
    # 3. Sample the symbols with the Gaussian probabilistic shaping applied
    test_symbols = sampleSymbols(N, mapping, nu)
    
    # 4. Plot the results!
    print("Plotting histogram...")
    
    # We use numBins=15 because sqrt(64) = 8. 
    # Using 15-20 bins ensures each of the 8 grid coordinates gets its own distinct column.
    plotSymbolHistogram(test_symbols, numBins=15)