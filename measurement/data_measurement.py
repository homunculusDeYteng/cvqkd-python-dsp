# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 16:25:05 2026

@author: Yulin Teng
"""





import time
import datetime
import numpy as np
import os
from instruments.powermeter_HAL_v1 import AndoPowerMeter



from measurement.noise_measurement_both import noise_measurement






from measurement.signal_measurement import signal_measurement
from instruments.local_oscillator import local_oscillator

from instruments.dac_HAL_v1 import KeysightAWG
from waveform_generation.waveform_gen1 import generate_waveforms, generate_quantum_only_waveform


GHz = 1e9
MHz = 1e6
FLAG_DIR = 'D:/cvqkd/1_data/flags/'
PAUSE_FLAG_ALICE = os.path.join(FLAG_DIR, 'pause_alice.flag')
PAUSE_FLAG_BOB = os.path.join(FLAG_DIR, 'pause_bob.flag')
laser = local_oscillator()

def pause_feedback_loops():
    """Pause both polarisation feedback loops before acquiring."""
    os.makedirs(FLAG_DIR, exist_ok=True)
    open(PAUSE_FLAG_ALICE, 'w').close()
    open(PAUSE_FLAG_BOB, 'w').close()
    print("Feedback loops paused.")


def resume_feedback_loops():
    """Resume both polarisation feedback loops after acquiring."""
    for flag in (PAUSE_FLAG_ALICE, PAUSE_FLAG_BOB):
        if os.path.exists(flag):
            os.remove(flag)
    print("Feedback loops resumed.")
    

def db_to_lin(db: float) -> float:
    """Convert dB to linear scale."""
    return 10 ** (db / 10.0)


# ---------------------------------------------------------
# Load the generated data file
# ---------------------------------------------------------
'''
data_path = 'D:/cvqkd/1_data/waveform_metadata/29_07_2026_M_64QAM__noCAZAC_classicalshift4000MHz_quantumshift1000MHz_fc4000MHz_fq125MHzRRC_roll_off_3.npz'
print(f"Loading base data from {data_path}...")

# Load the .npz file 
loaded_data = np.load(data_path, allow_pickle=True)

if 'metadata' in loaded_data:
    metadata = loaded_data['metadata'].item()
else:
    metadata = {} 
'''
print("Generating waveforms...")
#tx_shift_c, tx_shift_q, metadata = generate_waveforms(show_plots=False)
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
'''
basepath = 'D:/cvqkd/1_data/waveform_metadata/'
filename = basepath + metadata['waveform_name'] + '.npz'
np.savez(filename, tx_shift_c=tx_shift_c, tx_shift_q=tx_shift_q, metadata=metadata)
print(f"Waveform metadata saved to {filename}")
'''

# ---------------------------------------------------------
# Add stable parameters to metadata
metadata['DPOFs'] = 20e9  # Hz
metadata['MSOFs'] = 625e6 # Hz

metadata['p_lo_mW'] = 30    # mW
metadata['p_sig_mW'] = 10.5 # mW

metadata['V_dac_C'] = 500 # mV
metadata['V_dac_Q'] = 500 # mV

metadata['T_optique'] = db_to_lin(-5.6)
metadata['global_attenuation_dB'] = 0

# 0 = No, 1 = Yes
metadata['polar_stab_bool'] = 1 

# mV/div : Intense = ~20mV, quantum regime = ~8mV
metadata['V_adc_Q'] = 20 

metadata['propre'] = 0 
metadata['comment'] = "clock locked"

# ---------------------------------------------------
        
current_time = datetime.datetime.now()
date_str = current_time.strftime('%d_%m_%Y__%H_%M_%S')
metadata['signal_measurement_date'] = str(current_time)





if metadata.get('polar_stab_bool'):
    print("Stopping polarization stabilization...")
    pause_feedback_loops()
    time.sleep(2)







# --- A. Shot Noise Measurement ---
print("Acquiring shot noise...")
time.sleep(4)
# N = 1 (1 Mpoint), scale by 1e6 inside the function or pass directly





'''
metadata['rcv_raw'] = noise_measurement(calib=metadata['V_adc_Q'], 
                                        N=1e6, 
                                        samplerate=metadata['MSOFs'])

'''
SHOT_NOISE_POINTS = 1e6
metadata['rcv_raw'], metadata['rcv_raw_c'] = noise_measurement(
    calib=metadata['V_adc_Q'],
    N=SHOT_NOISE_POINTS,
    samplerate=metadata['MSOFs'],
    dpofs=metadata['DPOFs']
)

# generate sequence with quantum + pilot + synchronization
# emit sequence
print("\n--- Starting Acquisition ---")
print("Initializing AWG...")
awg = KeysightAWG(location='localhost', channels=[1, 2, 3, 4])
awg.set_emission_parameters(channels=[1, 2, 3, 4], dac_rate=64e9, amplitude=0.5)

print("Loading waveforms into AWG...")
awg.load_data([
    np.real(tx_shift_c),   # CH1 = Ic (Classical Real)
    np.imag(tx_shift_q),   # CH2 = Qq (Quantum Imaginary)
    np.real(tx_shift_q),   # CH3 = Iq (Quantum Real)
    np.imag(tx_shift_c),   # CH4 = Qc (Classical Imaginary)
])
awg.start_emission()
print("AWG emitting quantum + pilot + classical.")

time.sleep(4)

# --- C. Signal Acquisition ---
print("Acquiring signals...")
start_time = time.time()

q_samples_mpts = 0.312500 

classical_raw, quantum_raw = signal_measurement(
    adc_range=metadata['V_adc_Q'], 
    ATT_c=metadata['global_attenuation_dB'], 
    DPOFs=metadata['DPOFs'], 
    Qsamples=q_samples_mpts
)

metadata['classical_signal_raw'] = classical_raw
metadata['quantum_signal_raw'] = quantum_raw

elapsed_time = time.time() - start_time
print(f"Signal acquisition completed in {elapsed_time:.2f} seconds.")

# stop the signal
# generate a sequence with only quantum symbols (and same variance of before, for the quantum part)
# emit the sequence
awg = KeysightAWG(location='localhost', channels=[1, 2, 3, 4])
awg.set_emission_parameters(channels=[1, 2, 3, 4], dac_rate=64e9, amplitude=0.5)

print("Switching to quantum-only emission...")
awg.stop_emission()


time.sleep(4)

tx_shift_q_new, _ = generate_quantum_only_waveform(metadata)
awg.load_data([
    np.real(tx_shift_c),
    np.imag(tx_shift_q_new),       
    np.real(tx_shift_q_new),   
    np.imag(tx_shift_c),
])
awg.start_emission()
print("AWG emitting quantum-only (variance matched).")

time.sleep(4)

# --- B. Read Optical Power ---
# Initialize and read the Ando power meter
print("Reading Ando power meter...")
try:
    pwmt = AndoPowerMeter("GPIB0::2::INSTR")
    metadata['power_ando'] = pwmt.read()
    pwmt.close()
except Exception as e:
    print(f"Warning: Power meter read failed: {e}")
    metadata['power_ando'] = np.nan

metadata['power_ratio'] = 0.0408


awg.stop_emission()
print('Emission stopped for measuring power at zero')

time.sleep(10)

# --- B. Read Optical Power without modulation ---
# Initialize and read the Ando power meter
print("Reading Ando power meter...")
try:
    pwmt = AndoPowerMeter("GPIB0::2::INSTR")
    metadata['power_ando_zero'] = pwmt.read()
    pwmt.close()
except Exception as e:
    print(f"Warning: Power meter read failed: {e}")
    metadata['power_ando_zero'] = np.nan

print(f"Power at zero is {metadata['power_ando_zero']}")



# ---------------------------------------------------------
# --- LOAD AND ATTACH ELECTRONIC NOISE ---
# ---------------------------------------------------------
ELN_FILENAME = "D:/cvqkd/1_data/noise_calibration/elec_noise/30_07_2026__16_46_54_elec_noise_1Mpoints_625MHz.npz"

print("Loading electronic noise...")
try:
    eln_data = np.load(ELN_FILENAME, allow_pickle=True)
    metadata['eln_raw'] = eln_data['metadata'].item()['eln_raw']
    print("Successfully added electronic noise to metadata.")
except Exception as e:
    print(f"Warning: Could not load electronic noise data: {e}")
    metadata['eln_raw'] = None
# ---------------------------------------------------------

# --- D. Save the Data ---
save_path = f"D:/cvqkd/1_data/received_data/{date_str}.npz"
print(f"Saving data to {save_path}...")
np.savez(save_path, metadata=metadata)

# --- E. Resume Polarization Stabilization ---
if metadata.get('polar_stab_bool'):
        print("Resuming polarization stabilization thread...")
        resume_feedback_loops()   
        
awg.start_emission()

    
print("\nAll acquisitions complete.")