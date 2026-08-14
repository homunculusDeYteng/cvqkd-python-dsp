# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 16:00:31 2026
@author: Yulin Teng
"""
import time
import numpy as np
from instruments.HPvoa import HPVOA
from instruments.MSO44_measurement_V1 import TektronixMSO
from instruments.DSOZ540A_measurement_V1 import KeysightDSOZ540A


def noise_measurement(
    calib: float,
    N: int,
    samplerate: float = 500e6,
    dpofs: float = 500e6,
    dpo_voltage_scale: float = 70e-3,
    dpo_trigger_level: float = 0.5,
    dpo_trigger_slope: str = 'POSitive',
    dpo_trigger_source: str = 'AUX',
    mso_bandwidth: float = 500e6,
    mso_trigger_level: float = 0.45,
    mso_trigger_slope: str = 'RISE',
    voa_address: str = 'GPIB0::20::INSTR',
    dpo_address: str = 'TCPIP0::192.168.0.10::hislip0::INSTR',
    mso_address: str = 'TCPIP0::192.168.0.5::inst0::INSTR',
) -> tuple:
    
    record_length_pts_mso = int(N)
    acq_time = record_length_pts_mso / samplerate
    record_length_pts_dpo = int(round(acq_time * dpofs))

    with HPVOA(voa_address) as voa, \
         KeysightDSOZ540A(dpo_address) as dpo, \
         TektronixMSO(mso_address) as mso44:

        # Cut off the optical output
        voa.block_light()
        time.sleep(0.5)

        # Configure the Keysight DSOZ540A (classical channels)
        dpo.set_acquisition_parameters(
            channels=[1, 2],
            points=record_length_pts_dpo,
            sample_rate=dpofs,
            voltage_scale=dpo_voltage_scale
        )
        dpo.set_trigger_parameters(
            trigger_level=dpo_trigger_level,
            slope=dpo_trigger_slope,
            source=dpo_trigger_source
        )

        # Configure the Tektronix MSO44 (quantum channels)
        mso44.set_acquisition_parameters(
            channels=[3, 4],
            points=record_length_pts_mso,
            sample_rate=samplerate
        )
        scale_V = calib / 1000.0
        mso44.set_vertical_scale(scale_V)
        mso44.set_bandwidth(mso_bandwidth)
        mso44.set_trigger_parameters(level=mso_trigger_level, slope=mso_trigger_slope)
        mso44.set_trigger_mode('NORMal')
        mso44.set_aux_sync()

        # Arm both scopes and fetch data
        mso44.arm_acquisition()
        time.sleep(0.2)
        dpo.arm_acquisition()
        time.sleep(0.8)
        mso44.force_trigger()
        time.sleep(0.2)

        dpo_data = dpo.get_data()
        mso_data = mso44.get_data()

        dpo.stop_acquisition()
        mso44.stop_acquisition()

        dpo.run()
        mso44.run()

    ch1, ch2 = dpo_data[0], dpo_data[1]
    ch3, ch4 = mso_data[0], mso_data[1]

    sn_raw_c = ch1 + 1j * ch2
    sn_raw_q = ch3 + 1j * ch4

    return sn_raw_q, sn_raw_c