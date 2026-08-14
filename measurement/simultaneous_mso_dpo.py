# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 16:17:49 2026
@author: Yulin Teng
"""
from instruments.MSO44_measurement_V1 import TektronixMSO
from instruments.DSOZ540A_measurement_V1 import KeysightDSOZ540A
import time

def simultaneous_mso_dpo(scale_mv: float, record_length_mpts: float, dpofs: float):
    """
    Simultaneously record data from Keysight DSOZ540A and Tektronix MSO44.

    Args:
        scale_mv: MSO44 vertical scale in mV/div.
        record_length_mpts: MSO44 record length in megapoints. The Keysight
            record length is derived from it so both scopes span the same time.
        dpofs: Keysight sample rate in Sa/s.

    Returns:
        (ch1, ch2, ch3, ch4) voltage arrays. ch1/ch2 are the classical
        quadratures, ch3/ch4 the quantum ones.

    Raises:
        TimeoutError: if either scope does not receive its trigger.
    """
    # Parameter Calculation ---
    samplerate_mso = 625e6  # 625 MSa/s
    bandwidth_mso = 500e6   # 500 MHz

    scale_v_mso = scale_mv * 1e-3
    record_length_pts_mso = int(record_length_mpts * 1e6)

    # Calculate acquisition time and Keysight points
    acq_time = record_length_pts_mso / samplerate_mso
    record_length_pts_dpo = int(round(acq_time * dpofs))

    print('Connecting to Keysight DSOZ540A and Tektronix MSO44...')

    dpo = KeysightDSOZ540A('TCPIP0::192.168.0.10::hislip0::INSTR')
    mso = TektronixMSO('TCPIP0::192.168.0.5::inst0::INSTR')
    

    # ---Configure Keysight DSOZ540A ---
    dpo.set_acquisition_parameters(
        channels=[1, 2],
        points=record_length_pts_dpo,
        sample_rate=dpofs,
        voltage_scale=70e-3  # Assuming 70 from MATLAB was 70 mV/div
    )
    #dpo.set_trigger_parameters(trigger_level=0.05, slope='POSitive', source='CHANnel1')
    dpo.set_trigger_parameters(trigger_level=0.5, slope='POSitive',source='AUX')
    # --- Configure Tektronix MSO44 ---
    mso.set_acquisition_parameters(
        channels=[3, 4],
        points=record_length_pts_mso,
        sample_rate=samplerate_mso
    )
    mso.set_vertical_scale(scale_v_mso)
    mso.set_bandwidth(bandwidth_mso)
    mso.set_trigger_parameters(level=0.45, slope='RISE')

    mso.set_trigger_mode('NORMal')
    
    mso.set_aux_sync()
    
    # ---  Arm Both Scopes ---
    print("Arming oscilloscopes...")
    #dpo.arm_acquisition()
    #mso.arm_acquisition()
    mso.arm_acquisition()
    time.sleep(0.2)
    dpo.arm_acquisition()
    time.sleep(0.8)
    mso.force_trigger()
    time.sleep(0.2)
    # ---  Wait for the trigger and fetch the data ---
    print("Waiting for trigger and fetching data...")
    dpo_data = dpo.get_data()
    mso_data = mso.get_data()

    dpo.stop_acquisition()
    mso.stop_acquisition()
    
    print("Returning scopes to continuous run mode...")
    dpo.run()
    mso.run()
    # ---  Unpack (both sessions are closed by now) ---
    ch1, ch2 = dpo_data[0], dpo_data[1]
    ch3, ch4 = mso_data[0], mso_data[1]

    return ch1, ch2, ch3, ch4