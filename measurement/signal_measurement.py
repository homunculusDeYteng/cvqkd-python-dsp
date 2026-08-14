# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 16:21:08 2026

@author: Yulin Teng
"""

import time
import numpy as np
from instruments.HPvoa import HPVOA


from measurement.simultaneous_mso_dpo import simultaneous_mso_dpo

def signal_measurement(adc_range: float, ATT_c: float, DPOFs: float, Qsamples: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Perform signal measurement for both classical and quantum channels.
    
    Args:
        adc_range: The ADC range / calibration value (mV/div) for the MSO44.
        ATT_c: The attenuation value for the VOA (dB).
        DPOFs: The DPO sampling rate/frequency in Hz.
        Qsamples: Record length for the MSO44 in MPts.
        
    Returns:
        tuple[np.ndarray, np.ndarray]: 
            - classical_signal_raw (complex NumPy array)
            - quantum_signal_raw (complex NumPy array)
    """
    # connect to VOA to configure for signal measurement
    voa = HPVOA('GPIB0::20::INSTR')
    voa.set_value(ATT_c) # Set to your desired attenuation
    voa.open_light()     # Turn the output back ON
    time.sleep(0.5)      # Give it a half-second to mechanically open
    # Perform the simultaneous signal measurement
    ch1, ch2, ch3, ch4 = simultaneous_mso_dpo(adc_range, Qsamples, DPOFs)
    
    # Correct the electronic signal split
    ch2_new = ch2 * 2.0
    
    #Combine raw signals into complex signals
    classical_signal_raw = ch1 - 1j * ch2_new
    quantum_signal_raw = ch3 + 1j * ch4
    
    return classical_signal_raw, quantum_signal_raw