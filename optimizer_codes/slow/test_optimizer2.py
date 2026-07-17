# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 15:19:49 2026

@author: admin
"""

'''
#Initial guess
V = [1.5, 1.5, 1.5, 1.5]


#Parameters
step = 0.1                # voltage perturbation
alpha = 1e5               # update gain
settle = 0.02             # wait after voltage output
save_interval =  60 * 60  # Save data every 60 minutes (in seconds)

'''

import time 
import math

def optimize_step(V, step, alpha, settle, apply_voltages, measure_power):
    
    
    grads=[0]*4
    for k in range(4):
        P_base = measure_power()
        if math.isnan(P_base):
            continue
        
        V_orig = list(V)
        
        
        
        if V_orig[k] > 5.0 - step:
            V[k] = V_orig[k] - step
            apply_voltages(V)
            time.sleep(settle)
            P_minus = measure_power()
            grads[k] = (P_base - P_minus) / step
            
        else:
            V[k] = V_orig[k] + step
            apply_voltages(V)
            time.sleep(settle)
            P_plus = measure_power()
            grads[k] = (P_plus - P_base) / step
            
            
            
            
            
        V[k] = V_orig[k]
        
        
        if not math.isnan(grads[k]):
            V[k] = V[k] + alpha * grads[k]
           
            
            V[k] = max(0.0, min(5.0, V[k]))
       
        
        # Apply updated voltages before moving to the next channel
        apply_voltages(V)
        time.sleep(settle)
        
    return V
'''
        # Boundary check
        if V_orig[k] > 5.0 - step:
            V[k] = V_orig[k] - step
            apply_voltages(V)
            time.sleep(settle)
            P_minus = measure_power()
            grads[k] = (P_base - P_minus) / step
            
        elif V_orig[k] < step:
            V[k] = V_orig[k] + step
            apply_voltages(V)
            time.sleep(settle)
            P_plus = measure_power()
            grads[k] = (P_plus - P_base) / step
            
        else:
            V[k] = V_orig[k] + step
            apply_voltages(V)
            time.sleep(settle)
            P_plus = measure_power()
            
            # Perturb -step
            
            V[k] = V_orig[k] - step
            apply_voltages(V)
            time.sleep(settle)
            P_minus = measure_power()
            
            # Restore original V
            V[k] = V_orig[k]
            
            # Approximate gradient
            grads[k] = (P_plus - P_minus) / (2 * step)
           
        V[k] = V_orig[k]
        
        
        if not math.isnan(grads[k]):
            V[k] = V[k] + alpha * grads[k]
           
            
            V[k] = max(0.0, min(5.0, V[k]))
       
        
        # Apply updated voltages before moving to the next channel
        apply_voltages(V)
        time.sleep(settle)
        
    return V
'''

       
     

            
       
        