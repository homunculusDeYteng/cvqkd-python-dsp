# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 14:51:36 2026

@author: Yulin Teng
"""

import numpy as np

from waveform_generation.functions.lfsr import LFSR
from waveform_generation.functions.encode_bits_to_symbols import encodeBitsToSymbols
from waveform_generation.functions.decode_symbols_to_bits import decodeSymbolsToBits
from waveform_generation.functions.sample_symbols import sampleSymbols


def generate_pilot_symbols(n_pilots: int,mapping: np.ndarray,lfsr_reg_length: int,amplitude: float,):
    """
    n_pilots : int
        Number of pilot symbols to generate.
    mapping : np.ndarray of complex, shape (M,)
        QAM constellation map from generateNQAMMapping.
    lfsr_reg_length : int
        Shift register length for the LFSR (controls sequence period).
    amplitude : float
        Amplitude scaling applied to all pilot symbols.

    """
    bits_per_symbol = int(np.log2(len(mapping)))
    n_bits = n_pilots * bits_per_symbol

    bits, _ = LFSR(n_bits, lfsr_reg_length)
    pilots = encodeBitsToSymbols(bits, mapping)

    return amplitude * pilots, bits


def generate_data_symbols(n_data: int,mapping: np.ndarray,nu: float,amplitude: float,):
    """
    Generate Gaussian-shaped QAM data symbols.

    Parameters
    n_data : int
        Number of data symbols to generate.
    mapping : np.ndarray of complex, shape (M,)
        QAM constellation map from generateNQAMMapping.
    nu : float
        Gaussian shaping parameter.
    amplitude : float
        Amplitude scaling applied to all data symbols.

    Returns
    data : np.ndarray of complex, shape (n_data,)
        Scaled data symbols.
    """
    data = sampleSymbols(n_data, mapping, nu)
    data_bits = decodeSymbolsToBits(data, mapping)
    return amplitude * data, data_bits


def build_quantum_frame(n_pilots: int,n_data: int,mapping: np.ndarray,nu: float,pilot_amplitude: float,data_amplitude: float,lfsr_reg_length: int = 15,):
    """
    

    Parameters
    n_pilots : int
        Number of pilot symbols (placed at the start of the frame).
    n_data : int
        Number of data symbols (placed after the pilots).
    mapping : np.ndarray of complex, shape (M,)
        QAM constellation map from generateNQAMMapping.
    nu : float
        Gaussian shaping parameter for data symbols.
    pilot_amplitude : float
        Amplitude of pilot symbols.
    data_amplitude : float
        Amplitude of data symbols.
    lfsr_reg_length : int, optional
        LFSR shift register length. Default 15.

    
    """
    pilot_symbols, pilot_bits = generate_pilot_symbols(n_pilots, mapping, lfsr_reg_length, pilot_amplitude)
    if n_data > 0:
        data_symbols, data_bits = generate_data_symbols(n_data, mapping, nu, data_amplitude)
    else:
        data_symbols, data_bits = np.array([]), np.array([])
    frame = np.concatenate([pilot_symbols, data_symbols])

    return frame, pilot_symbols, data_symbols, pilot_bits, data_bits

def add_frequency_pilot(signal: np.ndarray,frequencies: np.ndarray,amplitudes: np.ndarray,sample_rate: float,):
    """
    
    Parameters
    signal : np.ndarray
        Time-domain waveform.
    frequencies : array-like of float
        Pilot tone frequencies in Hz.
    amplitudes : array-like of float
        Pilot tone amplitudes, one per frequency.
    sample_rate : float
        Sampling rate in Hz.

    """
    pilot_sequence = np.zeros(len(signal), dtype=complex)

    for i, freq in enumerate(frequencies):
        print(f"Adding frequency pilot: {freq * 1e-6:.1f} MHz, amplitude: {amplitudes[i]}")
        pilot_sequence += amplitudes[i] * np.exp(
            1j * 2 * np.pi * np.arange(len(signal)) * freq / sample_rate
        )

    return signal + pilot_sequence