# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 14:51:02 2026

@author: Yulin Teng
"""
import numpy as np
import dwfpy as dwf
import time 
import math
import pyvisa
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from powermeter_HAL_v1 import AndoPowerMeter
from test_optimizer2 import optimize_step

RESOURCE_ADDRESS = "GPIB0::2::INSTR"
meter = AndoPowerMeter(RESOURCE_ADDRESS)


managerA = dwf.Device(serial_number="210321A19B75", configuration=0)
managerB = dwf.Device(serial_number='210321A19FB0', configuration=0)
A = managerA.__enter__()
B = managerB.__enter__()


fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-', label='Optical Power')

ax.set_title("Live plot of Ando AQ2140 PowerMeter")
ax.set_xlabel("time(sec)")
ax.set_ylabel("Power")
ax.grid(True, linestyle='--', alpha=0.7)
ax.legend()


x_data=[]
y_data=[]
start_time = time.time()


V = [1.5, 1.5, 1.5, 1.5]  # Initial guess
STEP = 0.1
ALPHA = 1e5
SETTLE_TIME = 0.02

def apply_voltages(v_array):
    A.analog_output[0].setup("dc", offset=v_array[0], start=True)
    A.analog_output[1].setup("dc", offset=v_array[1], start=True)
    B.analog_output[0].setup("dc", offset=v_array[2], start=True)
    B.analog_output[1].setup("dc", offset=v_array[3], start=True)

def measure_power():
    return meter.read()

# Apply initial voltages
apply_voltages(V)




def close_devices():
    A.__exit__(None,None,None)
    B.__exit__(None,None,None)
            
def on_key(event):
    
    # print('Event')
    
    # If the user presses 'q' while the plot window is active
    if event.key in ['q']:
        A.__exit__(None,None,None)
        B.__exit__(None,None,None)

        print("\nKey pressed! Closing plot and stopping hardware")
        plt.close(fig)
        
    else:
        print(f'Detected {event.key}')
        

        
        
def update(frame):
    # devices = {info.serial_number: info for info in dwf.Device.enumerate()}
    # print(devices.keys())  # sanity-check both serials are present
    global V
    V = optimize_step(V, STEP, ALPHA, SETTLE_TIME, apply_voltages, measure_power)



    A.analog_output[0].setup("dc", offset=V[0], start=True)
    A.analog_output[1].setup("dc", offset=V[1], start=True)
    B.analog_output[0].setup("dc", offset=V[2], start=True)
    B.analog_output[1].setup("dc", offset=V[3], start=True)

            
    
    current_power = meter.read()
    current_time = time.time() - start_time
    
    
    print(f"Time: {current_time:>6.2f}s | Voltages: [{V[0]:>6.3f}V, {V[1]:>6.3f}V, {V[2]:>6.3f}V, {V[3]:>6.3f}V] | Power: {current_power:.4e}")
    
    
    if not math.isnan(current_power):
        x_data.append(current_time)
        y_data.append(current_power)
        
    line.set_data(x_data, y_data)
    
    
    
    ax.relim()
    ax.autoscale_view()
    
    return line, 

print("\n>>> Click on the plot window, then press 'q' key to stop <<<\n")

ani = FuncAnimation(
    fig, 
    update, 
    interval=500, 
    blit=False, 
    cache_frame_data=False
)


fig.canvas.mpl_connect('key_press_event', on_key)           
    



# plt.show()




