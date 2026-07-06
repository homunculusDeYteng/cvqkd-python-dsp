# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 13:08:03 2026

@author: Yulin Teng
"""

import os
import math
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from datetime import datetime 
import pyvisa
import pyarbtools



from functions.LFSR import LFSR
from functions.QPSK import QPSK
from functions.drawConstellation import drawConstellation
from functions.spectrum import spectrum
from functions.RRC_filter import RRC_filter
from functions.plotSymbolHistogram import plotSymbolHistogram
from functions.plot_noisy_symbols import plot_noisy_symbols
from functions.decodeSymbolsToBits import decodeSymbolsToBits
from functions.encodeBitsToSymbols import encodeBitsToSymbols



from functions.generateNQAMMapping import generateNQAMMapping
from functions.sampleSymbols import sampleSymbols

#=============================================
#File Paths and Dates
#=============================================
basePath = r"D:\cvqkd"
#Get today's date in dd_mm_yyyy form
dateStr = datetime.today().strftime('%d_%m_%Y')

#=============================================
#constants 
#=============================================
c = 2.99792458e8
h = 6.626068e-34
GHz = 1e9
MHz = 1e6
KHz = 1e3
km = 1e3
nm = 1e-9

#=============================================
#Equipment parameters
#=============================================
AWGFsc = 64 * GHz
AWGFsq = AWGFsc

#=============================================
#Modulation parameters
#=============================================
possible_states_c = 4
mod_c = math.log2(possible_states_c)

possible_states_q = 64
mod_q = math.log2(possible_states_q)
M = possible_states_q
nu = 0.0749

#=============================================
#DSP / waveform parameters
#=============================================
fs_x = 4 * GHz
fs_y = 125 * MHz

roll_off_c = 0.1
roll_off_q = 0.3
RRC_bool = 0 #1 = no RRC, 0 = apply RRC

fs_c = 4 * GHz
fs_q = 1 * GHz

shiftRegLength = 15

nbBitsc = math.ceil(512000 * mod_c / (2 * AWGFsc / fs_x)) + mod_c
nbBitsq = math.ceil(512000 * mod_q / (2 * AWGFsq / fs_y)) + mod_q

print(f'Classical QPSK signal shifted by {fs_c/GHz:g} GHz, at a baud rate of {fs_x/GHz:g} Gbaud.')
print('Quantum {M}-QAM signal shifted by {fs_q/GHz:g} GHz, at a baud rate of {fs_y/MHz} Mbaud.')

#=============================================
#Classical Signal Generation
#=============================================

bitSeq_raw, _ = LFSR(nbBitsc, shiftRegLength)
bitSeq = np.array(bitSeq_raw)
bitSeq[0:2] = bitSeq[-2:]

tx_sig = QPSK(bitSeq)
drawConstellation(tx_sig, 'tx constellation classical')
tx = np.kron(tx_sig, np.ones(math.floor(AWGFsc / fs_x)))
tx = tx[:-math.ceil(AWGFsc / fs_x)]
bitSeq = bitSeq[:-2]

spectrum(tx, AWGFsc, 'classical before RRC');
tx = RRC_filter(tx, fs_x, roll_off_c, AWGFsc)
spectrum(tx, AWGFsc, 'classical after RRC');
txc = tx.copy()

time_c = np.arange(len(tx)) / AWGFsc
tx_shift_c = tx * np.exp(1j * 2 * np.pi * fs_c * time_c)
spectrum(tx_shift_c, AWGFsc, 'classical after shift')

#============================================
#Quantum Signal Generation
#============================================

# %% Quantum signal generation
np.random.seed(46)

mapping = generateNQAMMapping(M)
symbols = sampleSymbols(math.floor(nbBitsq / math.log2(M)) - 1, mapping, nu)
bitSeq_q = decodeSymbolsToBits(symbols, mapping)
symbols_test = encodeBitsToSymbols(bitSeq_q, generateNQAMMapping(M))

plotSymbolHistogram(symbols, math.floor(math.sqrt(M)))
plot_noisy_symbols(M, symbols, symbols)

tx_sig = symbols
drawConstellation(tx_sig, 'tx constellation quantum')

tx = np.kron(tx_sig, np.ones(math.floor(AWGFsq / fs_y)))
spectrum(tx, AWGFsq, 'quantum before RRC')

if RRC_bool == 0:
    tx = RRC_filter(tx, fs_y, roll_off_q, AWGFsq)

spectrum(tx, AWGFsq, 'quantum after RRC')

txq = tx.copy()

time_q = np.arange(len(tx)) / AWGFsq
tx_shift_q = tx * np.exp(1j * 2 * np.pi * fs_q * time_q)
spectrum(tx_shift_q, AWGFsq, 'quantum after shift')

# ==========================================
# Match Waveform Lengths
# ==========================================
# Find the length of the shortest array
shortest = min(len(tx_shift_c), len(tx_shift_q))

# Truncate all arrays to the shortest length
tx_shift_c = tx_shift_c[:shortest]
tx_shift_q = tx_shift_q[:shortest]
txc = txc[:shortest]
txq = txq[:shortest]

# ==========================================
# Final Waveform Visualizations
# ==========================================


# 1. Baseband waveforms
plt.figure()
plt.plot(np.real(txc), label='Classical')
plt.plot(np.real(txq), label='Quantum')
plt.title('Baseband waveforms')
plt.legend()
plt.show()

# 2. Repeated shifted quantum waveform
plt.figure()
repeated_tx_shift_q = np.tile(tx_shift_q, 3)
plt.plot(np.real(repeated_tx_shift_q))

# Calculate positions for the vertical lines (replacing floor(length/3))
third_len = len(repeated_tx_shift_q) // 3
plt.axvline(third_len, color='black', linestyle='--')
plt.axvline(2 * third_len, color='black', linestyle='--')

plt.title('Repeated shifted quantum waveform')
plt.show()

# 3. Classical and scaled quantum comparison
plt.figure()
plt.plot(np.real(txc), label='Classical')

# Calculate the scaled quantum array
scaled_txq = np.sqrt(2) * np.real(txq) / np.max(np.real(txq))
plt.plot(scaled_txq, label='Quantum scaled')

# Set the exact Y-axis limits from your script
plt.ylim(-1.92, 1.86)
plt.title('Classical and scaled quantum comparison')
plt.legend()
plt.show()

# 4. Final Multiplexed Spectrum
# Calling the custom spectrum() function we translated earlier
spectrum(1000 * tx_shift_c + tx_shift_q, AWGFsc, 'PolX + PolY')


# %% Build waveform name
fs_x_MHz = fs_x / MHz
fs_y_MHz = fs_y / MHz

if RRC_bool == 1:
    # In Python, wrapping strings in parentheses allows you to break 
    # them across multiple lines without using MATLAB's "..."
    waveform_name = (
        f"{dateStr}_M_{M}QAM_"
        f"noRRC_noCAZAC_classicalshift{fs_c/MHz:g}MHz_"
        f"quantumshift{fs_q/MHz:g}MHz_fc"
        f"{fs_x_MHz:g}MHz_fq{fs_y_MHz:g}MHz"
    )
else:
    waveform_name = (
        f"{dateStr}_M_{M}QAM_"
        f"_noCAZAC_classicalshift{fs_c/MHz:g}MHz_"
        f"quantumshift{fs_q/MHz:g}MHz_fc"
        f"{fs_x_MHz:g}MHz_fq{fs_y_MHz:g}"
        f"MHzRRC_roll_off_{round(roll_off_q * 10)}"
    )



# %% Save MAT file
# Create a dictionary to hold all metadata (equivalent to MATLAB's struct)
metadata = {
    'bitSeq': bitSeq,
    'bitSeq_q': bitSeq_q,
    'f_c': fs_x,
    'f_q': fs_y,
    'data_generation_date': dateStr,
    'roll_off_c': roll_off_c,
    'roll_off_q': roll_off_q,
    'RRC_bool': RRC_bool,
    'freq_shift_c': fs_c,
    'freq_shift_q': fs_q,
    'M': possible_states_q, # Make sure 'possible_states_q' is defined, or change to 'M'
    'freq_sampling_AWG': AWGFsc,
    'nu': nu,
    'waveform_name': waveform_name,
    'AWG_channel_map': 'CH1=Ic, CH2=Qq, CH3=Iq, CH4=-CH1'
}

# Use os.path.join to handle folder slashes automatically (works on Windows & Linux)
folder_path = os.path.join(basePath, "1_data", "sent_data")

# Generate the file name using f-strings
if RRC_bool == 1:
    file_name = (
        f"{dateStr}_M_{M}QAM_fc_{fs_x/GHz:g}GHZ_"
        f"fq_{fs_y/MHz:g}MHZ_noRRC.mat"
    )
else:
    file_name = (
        f"{dateStr}_M_{M}QAM_fc_{fs_x/GHz:g}GHZ_"
        f"fq_{fs_y/MHz:g}MHZ_RRC_{round(roll_off_q*10)}rolloff_.mat"
    )

file_gen_name = os.path.join(folder_path, file_name)

# Add the final path to the metadata dictionary
metadata['file_gen_name'] = file_gen_name

# Extract the directory path and create it if it doesn't exist
# exist_ok=True perfectly replicates MATLAB's "if ~exist(..., 'dir') mkdir" logic
saveFolder = os.path.dirname(file_gen_name)
os.makedirs(saveFolder, exist_ok=True)

# Package all variables into a single dictionary to save
save_dict = {
    'metadata': metadata,
    'tx_shift_c': tx_shift_c,
    'tx_shift_q': tx_shift_q
}

# Save the MAT file
sio.savemat(file_gen_name, save_dict)