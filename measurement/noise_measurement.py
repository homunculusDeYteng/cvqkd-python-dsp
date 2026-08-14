# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 16:00:31 2026
@author: Yulin Teng
"""
import time
import numpy as np
from instruments.HPvoa import HPVOA
from instruments.MSO44_measurement_V1 import TektronixMSO


def noise_measurement(calib: float, N: int, samplerate: float = 500e6) -> np.ndarray:
    """
    Perform shot noise measurement with independent, safe instrument handling.
    """
    with HPVOA('GPIB0::20::INSTR') as voa, \
         TektronixMSO('TCPIP0::192.168.0.5::inst0::INSTR') as mso44:

        # Cut off the optical output
        voa.block_light()
        time.sleep(0.5)

        #Configure the oscilloscope
        mso44.set_acquisition_parameters(
            channels=[3, 4],
            points=int(N),
            sample_rate=samplerate
        )

        #Set vertical scale (mV/div to V/div)
        scale_V = calib / 1000.0
        mso44.set_vertical_scale(scale_V)

        #Arm and fetch data
        #mso44.set_trigger_mode('AUTO')
        mso44.arm_acquisition()
        mso44.force_trigger()
        time.sleep(0.5)
        data = mso44.get_data()

    ch3 = data[0]
    ch4 = data[1]
    sn_raw = ch3 + 1j * ch4

    return sn_raw




