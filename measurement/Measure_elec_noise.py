# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 16:46:37 2026

@author: Yulin Teng
"""

import os
import datetime
import numpy as np

from instruments.HPvoa import HPVOA
from measurement.noise_measurement import noise_measurement

# --- Paths ---
LOCATION = 'D:/cvqkd/1_data/'
FOLDER = 'noise_calibration/elec_noise/'
LOG_FILE = 'D:/cvqkd/log/elec_noise_measurement_log.txt'

# --- Parameters ---
N_POINTS_MPTS = 2          # Megapoints
F_SAMPLING = 625e6         # Hz
V_ADC_Q = 8                # mV/div
NUM_ACQUISITIONS = 1


def elec_noise_calibration(n_points_mpts=N_POINTS_MPTS,
                           f_sampling=F_SAMPLING,
                           v_adc_q=V_ADC_Q,
                           num_acquisitions=NUM_ACQUISITIONS):

    output_dir = os.path.join(LOCATION, FOLDER)
    os.makedirs(output_dir, exist_ok=True)

    acquisition_time = (n_points_mpts * 1e6) / f_sampling
    print(f"Acquisition time: {acquisition_time * 1e3:.3f} ms")

    # Block the VOA and leave it blocked for the whole calibration.
    # The LO laser should be turned off manually before running this script.
    with HPVOA() as voa:
        voa.block_light()

    print("TURN OFF LO LASER")

    for index in range(1, num_acquisitions + 1):
        print(f"Acquisition: {index}")

        now = datetime.datetime.now()
        date_str = now.strftime('%d_%m_%Y__%H_%M_%S')
        name = f"{date_str}_elec_noise_{n_points_mpts}Mpoints_{int(f_sampling / 1e6)}MHz"

        # Build metadata
        metadata = {
            'MSOFs': f_sampling,
            'signal_measurement_date': str(now),
            'p_lo_mW': 0,
            'V_adc_Q': v_adc_q,
            'comment': 'No comment',
            'N_points': n_points_mpts,
            'index': index,
        }

        # Acquire
        eln_raw = noise_measurement(
            calib=v_adc_q,
            N=n_points_mpts * 1e6,
            samplerate=f_sampling
        )
        metadata['eln_raw'] = eln_raw

        # Save
        save_path = os.path.join(output_dir, name + '.npz')
        np.savez(save_path, metadata=metadata)
        print(f"Saved to {save_path}")

    # Log
    log_entry = (
        f"[{date_str}] Electronic Noise Measurement\n"
        f"  Npoints: {n_points_mpts} Mpts\n"
        f"  Sampling Rate: {f_sampling / 1e6:.2f} MHz\n"
        f"\n"
    )
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)

    print("Electronic noise calibration complete.")


if __name__ == '__main__':
    elec_noise_calibration()