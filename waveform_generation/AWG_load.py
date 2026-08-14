# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 16:38:54 2026

@author: Yulin Teng
"""

from waveform_generation.waveform_gen1 import generate_waveforms, generate_quantum_only_waveform

import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib

from instruments.dac_HAL_v1 import KeysightAWG 

GHz = 1e9
MHz = 1e6

#matplotlib.use('Agg')


print("Initializing AWG")
awg = KeysightAWG(
    location='localhost', 
    channels=[1, 2, 3, 4]
)

print("Setting emission parameters")
awg.set_emission_parameters(
    channels=[1, 2, 3, 4], 
    dac_rate=64e9, 
    amplitude=0.5,
    dacMode='four'
)

awg.set_data_internal_memory_mode()

print("Generating test waveforms")


tx_shift_c, tx_shift_q, metadata = generate_waveforms(
    show_plots=False,

    # AWG clock
    AWG_RATE=64 * GHz,

    # Classical channel (QPSK)
    BAUD_C=4 * GHz,
    FREQ_SHIFT_C=4 * GHz,
    ROLL_OFF_C=0.1,
    LFSR_LENGTH=15,

    # Quantum channel (N-QAM)
    M=64,
    NU=0.0749,
    BAUD_Q=250 * MHz,
    FREQ_SHIFT_Q=2 * GHz,
    ROLL_OFF_Q=0.2,
    APPLY_RRC_Q=True,

    # Pilot frame (symbol-domain pilots)
    N_PILOT=100,
    N_DATA=400,
    A_PILOT=4.0,
    A_DATA=1.0,

    # Frequency pilot tone(s)
    FREQ_PILOT=[900e6],
    amplitudes=[4],

    seed=46,
)
#tx_shift_c, tx_shift_q, metadata = generate_waveforms(show_plots=False)
tx_shift_q_only, _ = generate_quantum_only_waveform(metadata)

#%%
data_ch1 = np.real(tx_shift_c)        # CH1 = Ic (Classical Real)
data_ch2 = np.imag(tx_shift_q)        # CH2 = Qq (Quantum Imaginary)
data_ch3 = np.real(tx_shift_q)        # CH3 = Iq (Quantum Real)
data_ch4 = np.imag(tx_shift_c)        # CH4 = Qc (Classical Imaginary)
#%%
data_ch1 = np.real(tx_shift_c)
data_ch2 = np.imag(tx_shift_q_only)         
data_ch3 = np.real(tx_shift_q_only)         
data_ch4 = np.imag(tx_shift_c)   
'''
t = np.linspace(0, 2 * np.pi, 1024, endpoint=False)
data_ch1 = np.sin(t)
data_ch2 = np.cos(t)
data_ch3 = np.sin(t + np.pi/4)
data_ch4 = np.cos(t + np.pi/4)
'''

# norm_data_ch1 = data_ch1 / np.amax(data_ch1)
# norm_data_ch2 = data_ch2 / np.amax(data_ch2)
# norm_data_ch3 = data_ch3 / np.amax(data_ch3)
# norm_data_ch4 = data_ch4 / np.amax(data_ch4)

#%%
print("Loading data")
# awg.set_data_extended_memory_mode()
awg.load_data([data_ch1, data_ch2, data_ch3, data_ch4])

print("Starting emission")
awg.start_emission()



'''
time.sleep(10)



print("Stopping emission")
awg.stop_emission()
print("Test complete.")
'''
plt.close('all')




basepath = 'D:/cvqkd/1_data/waveform_metadata/'
filename = basepath + metadata['waveform_name'] + '.npz'
np.savez(filename, tx_shift_c=tx_shift_c, tx_shift_q=tx_shift_q, metadata=metadata)



