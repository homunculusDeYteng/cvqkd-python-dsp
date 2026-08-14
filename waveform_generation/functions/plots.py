# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 11:34:53 2026

@author: Yulin Teng
"""


import numpy as np
import matplotlib.pyplot as plt


def draw_constellation(symbols: np.ndarray, title: str):
    """Scatter plot of complex symbols on the I-Q plane."""
    plt.figure(figsize=(6, 6))
    plt.scatter(np.real(symbols), np.imag(symbols),
                color='blue', alpha=0.6, marker='.', s=10)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.title(title)
    plt.xlabel('In-Phase (I)')
    plt.ylabel('Quadrature (Q)')
    plt.axis('equal')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_symbol_histogram(symbols: np.ndarray, num_bins: int):
    """3-D bar chart showing the empirical probability distribution over the I-Q plane."""
    real_part = np.real(symbols)
    imag_part = np.imag(symbols)

    counts, x_edges, y_edges = np.histogram2d(real_part, imag_part, bins=num_bins)
    prob = counts / len(symbols)

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    x_pos, y_pos = np.meshgrid(x_edges[:-1], y_edges[:-1], indexing='ij')
    x_flat = x_pos.ravel()
    y_flat = y_pos.ravel()
    z_flat = prob.ravel()

    dx = x_edges[1] - x_edges[0]
    dy = y_edges[1] - y_edges[0]

    norm = plt.Normalize(0, z_flat.max() if z_flat.max() > 0 else 1)
    cmap = plt.get_cmap('viridis')
    colors = cmap(norm(z_flat))

    ax.bar3d(x_flat, y_flat, np.zeros_like(x_flat),
             dx, dy, z_flat, color=colors, shade=True)

    ax.set_xlabel('In-Phase (I)')
    ax.set_ylabel('Quadrature (Q)')
    ax.set_zlabel('Probability')
    plt.title('Symbol probability histogram')

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, pad=0.1)
    plt.tight_layout()
    plt.show()


def plot_noisy_symbols(
    M: int,
    ideal_symbols: np.ndarray,
    received_symbols: np.ndarray,
):
    """
    Scatter plot of received symbols, colour-coded by their ideal constellation point.

    Parameters
    ----------
    M : int
        Constellation size (used to set colour spacing).
    ideal_symbols : array-like of complex
        The noiseless symbol for each transmitted sample.
    received_symbols : array-like of complex
        The noisy received samples (same length as ideal_symbols).
    """
    ideal    = np.asarray(ideal_symbols)
    received = np.asarray(received_symbols)

    unique = np.unique(ideal)
    cmap   = plt.get_cmap('hsv')
    color_step = M // len(unique)

    plt.figure(figsize=(8, 8))
    for i, point in enumerate(unique):
        mask = (ideal == point)
        color = cmap(((i * color_step) % M) / M)
        plt.plot(
            np.real(received[mask]),
            np.imag(received[mask]),
            marker='.', linestyle='', color=color, markersize=5,
        )

    plt.title('Received symbols (colour = ideal constellation point)')
    plt.xlabel('In-Phase (I)')
    plt.ylabel('Quadrature (Q)')
    plt.axis('equal')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()


def plot_spectrum(signal: np.ndarray, sample_rate: float, title: str) :
    """
    Power spectral density plot of a complex signal.

    Parameters
    ----------
    signal : np.ndarray
        Time-domain waveform.
    sample_rate : float
        Sampling rate in Hz (used to scale the frequency axis to GHz).
    title : str
        Plot title.
    """
    plt.figure()
    plt.psd(signal, NFFT=2048, Fs=sample_rate, color='blue')
    plt.title(title)

    ax = plt.gca()
    ax.set_xticklabels([f'{t / 1e9:g}' for t in ax.get_xticks()])
    plt.xlabel('Frequency (GHz)')
    plt.tight_layout()
    plt.show()