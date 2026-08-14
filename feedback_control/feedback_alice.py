# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 15:06:52 2026

@author: admin
"""

import math

import time
import os



import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation



import dwfpy as dwf



from instruments.powermeter_HAL_v1 import AndoPowerMeter

from feedback_control.optimizer_min import optimize_step_fd_adaptive

import numpy as np

PAUSE_FLAG = 'D:/cvqkd/1_data/flags/pause_alice.flag'

# --------------------------------------------------------------------------

# Configuration

# --------------------------------------------------------------------------

RESOURCE_ADDRESS = "GPIB0::2::INSTR"

SERIAL_A = "210321A19B75"

SERIAL_B = "210321A19FB0"



V = [2.5, 2.5, 2.5, 2.5]     # initial guess
# V = [0.5, 0.5, 0.5, 0.5]     # initial guess
# V  = [0.857,  1.011,  0.889,  1.875]
# V = [ 0.775,  0.667,  1.366,  1.262]

STEP = 0.05     # voltage perturbation

ALPHA = 1e5

SETTLE_TIME = 0.02



OPTIMIZER = optimize_step_fd_adaptive

PLOT_EVERY = 1                  



# --------------------------------------------------------------------------

# Hardware setup

# --------------------------------------------------------------------------

meter = AndoPowerMeter(RESOURCE_ADDRESS)



managerA = dwf.Device(serial_number=SERIAL_A, configuration=0)

managerB = dwf.Device(serial_number=SERIAL_B, configuration=0)

A = managerA.__enter__()

B = managerB.__enter__()



# Channel index 0..3 -> analog-out channel object.

CHANNELS = [

    A.analog_output[0],

    A.analog_output[1],

    B.analog_output[0],

    B.analog_output[1],

]



_closed = False
_paused = False
_manual_paused = False




def set_voltage(k, value):

   

    CHANNELS[k].setup("dc", offset=value, start=True)

   





def apply_all(v_array):

    for k in range(4):

        set_voltage(k, v_array[k])





def measure_power():

    return meter.read()





def close_devices():

    global _closed

    if _closed:

        return

    _closed = True

    try:

        A.__exit__(None, None, None)

    finally:

        B.__exit__(None, None, None)

    print("\nHardware stopped.")







apply_all(V)

time.sleep(SETTLE_TIME)





fig, ax = plt.subplots()

line, = ax.plot([], [], 'b-', label='Optical Power')

ax.set_title("Live plot of Ando AQ2140 PowerMeter")

ax.set_xlabel("time (sec)")

ax.set_ylabel("Power")

ax.grid(True, linestyle='--', alpha=0.7)

ax.legend()



x_data = []

y_data = []

alpha_data = []

start_time = time.time()

LAST_POWER = float('nan')     

_frame = 0





def on_key(event):
    global _paused,_manual_paused
    if event.key == 'q':

        close_devices()

        print("Key 'q' pressed - closing plot.")

        plt.close(fig)
        
    elif event.key == '1':
        _manual_paused = not _manual_paused
        state = "Paused" if _paused else "Resumed"
        print(f"\n>>> Key '1' pressed - {state} voltage updates <<<\n")
        
        
    else:

        print(f'Detected {event.key}')





def update(frame):
    global V, LAST_POWER, _frame,ALPHA,_paused

    _paused = _manual_paused or os.path.exists(PAUSE_FLAG)    
    if _closed:
        return line,
    
    
    
    # ----------------------

    if _paused:
        # Measure power without updating voltages
        LAST_POWER = measure_power()
        time.sleep(0.1)  # 100ms delay to prevent polling the meter too aggressively
        
        current_time = time.time() - start_time
        print(f"[PAUSED] Time: {current_time:>6.2f}s | "
              f"Voltages: [{V[0]:>6.3f}V, {V[1]:>6.3f}V, "
              f"{V[2]:>6.3f}V, {V[3]:>6.3f}V] | "
              f"Power: {LAST_POWER:.4e} | "
              f"Alpha: {ALPHA: 4e}")
    else:
        # Run the adaptive optimization loop
        V, ALPHA, LAST_POWER = OPTIMIZER(
            V, STEP, ALPHA, SETTLE_TIME, set_voltage, measure_power, LAST_POWER
        )
        
        current_time = time.time() - start_time
        print(f"Time: {current_time:>6.2f}s | "
              f"Voltages: [{V[0]:>6.3f}V, {V[1]:>6.3f}V, "
              f"{V[2]:>6.3f}V, {V[3]:>6.3f}V] | "
              f"Power: {LAST_POWER:.4e} | "
              f"Alpha: {ALPHA: 4e}")
        
    if not math.isnan(LAST_POWER):
        x_data.append(current_time)
        y_data.append(LAST_POWER)
        alpha_data.append(ALPHA)
        line.set_data(x_data, y_data)

    _frame += 1
    if _frame % PLOT_EVERY == 0:
        ax.relim()
        ax.autoscale_view()

    return line,





print("\n>>> Click the plot window, then press 'q' to stop <<<\n")



ani = FuncAnimation(

    fig,

    update,

    interval=1,          # run as fast as the hardware allows

    blit=False,

    cache_frame_data=False,

)



fig.canvas.mpl_connect('key_press_event', on_key)



plt.show(block = True)               # blocks until the window closes

close_devices()          # idempotent safety net

print('The end of the script, save data')
from datetime import datetime
format_date = "%Y%m%d_%H_%M_%S"

time_now = datetime.now()
timestamp = time_now.strftime(format_date)

dirname = 'D:/cvqkd/1_data/polarization_stabilization_alice/'
fname = f'pol_stabilization_alice_{timestamp}.npz'

np.savez(dirname+fname, x_data=np.array(x_data), y_data=np.array(y_data), alpha_data=np.array(alpha_data))
