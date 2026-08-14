# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 11:11:06 2026

@author: Yulin Teng
"""


import math
from datetime import datetime

import numpy as np
# import matplotlib.pyplot as plt
from waveform_generation.functions.pilot_frame import build_quantum_frame
from waveform_generation.functions.lfsr import LFSR
from waveform_generation.functions.qpsk import QPSK
from waveform_generation.functions.generate_nqam_mapping import generateNQAMMapping
#from waveform_generation.functions.sample_symbols import sampleSymbols
from waveform_generation.functions.decode_symbols_to_bits import decodeSymbolsToBits
from waveform_generation.functions.rrcfilter import RRC_filter
from waveform_generation.functions.pilot_frame import add_frequency_pilot
#from waveform_generation.functions.encode_bits_to_symbols import encodeBitsToSymbols




def _upsample(symbols: np.ndarray, upsample_factor: int) -> np.ndarray:
    """Repeat each symbol upsample_factor times (zero-order hold)."""
    return np.kron(symbols, np.ones(upsample_factor))


def _frequency_shift(signal: np.ndarray, freq: float, sample_rate: float) -> np.ndarray:
    """Translate a baseband signal to centre frequency `freq` Hz."""
    t = np.arange(len(signal)) / sample_rate
    return signal * np.exp(1j * 2 * np.pi * freq * t)




def generate_waveforms(show_plots: bool = False):
    """
    Generate the classical and quantum TX waveforms.

    Parameters
    ----------
    show_plots : bool
        If True, display diagnostic plots at each DSP stage.

    Returns
    -------
    tx_shift_c : np.ndarray of complex
        Frequency-shifted classical waveform (64 GSa/s).
    tx_shift_q : np.ndarray of complex
        Frequency-shifted quantum waveform (64 GSa/s).
    metadata : dict
        All signal parameters and bit sequences needed for receiver-side
        processing and file naming.
    """

    
    GHz = 1e9
    MHz = 1e6

    AWG_RATE    = 64 * GHz          # AWG clock — same for both channels

    # Classical channel
    BAUD_C      = 4  * GHz          # Symbol rate
    FREQ_SHIFT_C = 4 * GHz          # Carrier offset
    ROLL_OFF_C  = 0.1
    LFSR_LENGTH = 15                 # Shift register length for PRBS

    # Quantum channel
    M           = 4                # Constellation size (64-QAM)
    NU          = 0.0749             # Gaussian shaping parameter
    BAUD_Q      = 125 * MHz          # Symbol rate
    FREQ_SHIFT_Q = 1 * GHz           # Carrier offset
    ROLL_OFF_Q  = 0.3
    APPLY_RRC_Q = True               # Set False to bypass quantum RRC

    n_bits_c = math.ceil(512_000 * math.log2(4)  / (2 * AWG_RATE / BAUD_C))  + 2
    #n_bits_q = math.ceil(512_000 * math.log2(M)  / (2 * AWG_RATE / BAUD_Q))  + int(math.log2(M))


    # Classical signal: PRBS → QPSK → upsample → RRC → shift

    print(f"Classical: QPSK at {BAUD_C/GHz:g} Gbaud, shifted to {FREQ_SHIFT_C/GHz:g} GHz")

    bits_c_raw, _ = LFSR(n_bits_c, LFSR_LENGTH)
    bits_c = np.array(bits_c_raw)

    
    bits_c[:2] = bits_c[-2:]

    symbols_c = QPSK(bits_c)
    

    upsample_c = int(AWG_RATE / BAUD_C)
    tx_c = _upsample(symbols_c, upsample_c)[:-upsample_c]   # trim one symbol period

    

    tx_c = RRC_filter(tx_c, BAUD_C, ROLL_OFF_C, AWG_RATE)

    

    tx_c_baseband = tx_c.copy()
    tx_shift_c = _frequency_shift(tx_c, FREQ_SHIFT_C, AWG_RATE)

    

    
    bits_c = bits_c[:-2]

    # Quantum signal: Gaussian-shaped 64-QAM → upsample → RRC → shift
    print(f"Quantum: {M}-QAM at {BAUD_Q/MHz:g} Mbaud, shifted to {FREQ_SHIFT_Q/GHz:g} GHz")

    np.random.seed(46)   # Reproducible symbol draw for matched receiver

    # mapping = generateNQAMMapping(M)
    # n_symbols_q = math.floor(n_bits_q / math.log2(M)) - 1
    # symbols_q = sampleSymbols(n_symbols_q, mapping, NU)
    # bits_q = decodeSymbolsToBits(symbols_q, mapping)
    # Pilot frame parameters
    N_PILOT = 100    # number of pilot symbols 
    N_DATA  = 400    # number of data symbols
    A_PILOT = 4.0    # pilot amplitude
    A_DATA  = 1.0    # data amplitude

    mapping = generateNQAMMapping(M)

    symbols_q, pilot_symbols, data_symbols, pilot_bits, bits_q = build_quantum_frame(
    n_pilots        = N_PILOT,
    n_data          = N_DATA,
    mapping         = mapping,
    nu              = NU,
    pilot_amplitude = A_PILOT,
    data_amplitude  = A_DATA,
)

    # bits_q = decodeSymbolsToBits(data_symbols, mapping)
    

    upsample_q = int(AWG_RATE / BAUD_Q)
    tx_q = _upsample(symbols_q, upsample_q)

    

    if APPLY_RRC_Q:
        tx_q = RRC_filter(tx_q, BAUD_Q, ROLL_OFF_Q, AWG_RATE)

    

    tx_q_baseband = tx_q.copy()
    tx_shift_q = _frequency_shift(tx_q, FREQ_SHIFT_Q, AWG_RATE)
    
    FREQ_PILOT = [900e6]
    
    
    # generate frequency pilot
    tx_shift_q = add_frequency_pilot(
    signal      = tx_shift_q,
    frequencies = FREQ_PILOT,
    amplitudes  = [4],
    sample_rate = AWG_RATE,
)

    # -----------------------------------------------------------------------
    # Align waveform lengths
    # -----------------------------------------------------------------------
    length = min(len(tx_shift_c), len(tx_shift_q))
    tx_shift_c    = tx_shift_c[:length]
    tx_shift_q    = tx_shift_q[:length]
    tx_c_baseband = tx_c_baseband[:length]
    tx_q_baseband = tx_q_baseband[:length]


    #Normalization
    
    # Quantum
    scale_q = max(np.amax(np.abs(np.real(tx_shift_q))), np.amax(np.abs(np.imag(tx_shift_q))))
    if scale_q > 1:
        tx_shift_q = tx_shift_q / scale_q

    # Classical
    scale_c = max(np.amax(np.abs(np.real(tx_shift_c))), np.amax(np.abs(np.imag(tx_shift_c))))
    if scale_c > 1:
        tx_shift_c = tx_shift_c / scale_c
    
    #variance after normalization
    
    norm_quantum_variance  = [np.var(np.real(tx_shift_q)), np.var(np.imag(tx_shift_q))]
    norm_classical_variance = [np.var(np.real(tx_shift_c)), np.var(np.imag(tx_shift_c))]

    # -----------------------------------------------------------------------
    # Waveform filename
    # -----------------------------------------------------------------------
    date_str = datetime.today().strftime('%d_%m_%Y')
    rrc_tag  = 'noRRC' if not APPLY_RRC_Q else f'RRC_roll_off_{round(ROLL_OFF_Q * 10)}'

    waveform_name = (
        f"{date_str}_M_{M}QAM_noCAZAC"
        f"_classicalshift{FREQ_SHIFT_C/MHz:g}MHz"
        f"_quantumshift{FREQ_SHIFT_Q/MHz:g}MHz"
        f"_fc{BAUD_C/MHz:g}MHz"
        f"_fq{BAUD_Q/MHz:g}MHz"
        f"_{rrc_tag}"
    )

    # -----------------------------------------------------------------------
    # Metadata bundle
    # -----------------------------------------------------------------------
    metadata = {
        'waveform_name':      waveform_name,
        'data_generation_date': date_str,
        # Bit sequences
        'bitSeq':   bits_c,
        'bitSeq_q': bits_q,
        'bitSeq_pilot': pilot_bits,
        # Signal parameters
        'pilot_symbols':   pilot_symbols,
        'n_pilots':        N_PILOT,
        'n_data':          N_DATA,
        'pilot_amplitude': A_PILOT,
        'pilot_frequency':FREQ_PILOT,
        'data_amplitude':  A_DATA,
        'M':              M,
        'nu':             NU,
        'f_c':            BAUD_C,
        'f_q':            BAUD_Q,
        'freq_shift_c':   FREQ_SHIFT_C,
        'freq_shift_q':   FREQ_SHIFT_Q,
        'freq_sampling_AWG': AWG_RATE,
        'norm_quantum_variance':   norm_quantum_variance,
        'norm_classical_variance': norm_classical_variance,
        'roll_off_c':     ROLL_OFF_C,
        'roll_off_q':     ROLL_OFF_Q,
        'RRC_bool':       int(not APPLY_RRC_Q),
        # AWG channel assignment
        'AWG_channel_map': 'CH1=Ic, CH2=Qq, CH3=Iq, CH4=Qc',
    }

    # ensure that the two sequences are normalized (or not exceeding 1 as np.amax(np.real(q))), np.amax(np.imag(q))
    # - normalize together quantum sequence (real and imaginary)
    # - the same for the classical
    return tx_shift_c, tx_shift_q, metadata



def generate_quantum_only_waveform(metadata: dict) -> tuple:
    """
    Generate a quantum-only waveform (no pilots, no frequency pilot tone)
    with variance matched to the original emission.
    """

    M            = metadata['M']
    NU           = metadata['nu']
    N_DATA       = metadata['n_data']
    A_DATA       = metadata['data_amplitude']
    BAUD_Q       = metadata['f_q']
    FREQ_SHIFT_Q = metadata['freq_shift_q']
    AWG_RATE     = metadata['freq_sampling_AWG']
    ROLL_OFF_Q   = metadata['roll_off_q']
    norm_var     = metadata['norm_quantum_variance']

    mapping = generateNQAMMapping(M)
    _, _, data_symbols, _, _ = build_quantum_frame(
        n_pilots        = 0,
        n_data          = N_DATA,
        mapping         = mapping,
        nu              = NU,
        pilot_amplitude = 0.0,
        data_amplitude  = A_DATA,
    )

    # --- DSP: upsample → RRC → frequency shift ---
    upsample_q = int(AWG_RATE / BAUD_Q)
    tx_q = _upsample(data_symbols, upsample_q)

    if metadata['RRC_bool'] == 0:
        tx_q = RRC_filter(tx_q, BAUD_Q, ROLL_OFF_Q, AWG_RATE)

    tx_shift_q_new = _frequency_shift(tx_q, FREQ_SHIFT_Q, AWG_RATE)

    target_var  = float(np.mean(norm_var))
    current_var = float( np.mean([np.var(tx_shift_q_new.real),np.var(tx_shift_q_new.imag)]) )
    scale = np.sqrt(target_var / current_var)
    tx_shift_q_new = tx_shift_q_new * scale

    return tx_shift_q_new, data_symbols

