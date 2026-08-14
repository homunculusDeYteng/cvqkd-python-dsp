# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 15:19:46 2026

@author: admin
"""

import time
import math
# import numpy as np

VMIN = 0.0
VMAX = 5.0
N = 4

# === Adaptive Alpha Parameters (tune these) ===
HIGH_THRESH = 5e-2   # If gradient_norm * alpha > this, decrease alpha
LOW_THRESH = 8e-3    # If gradient_norm * alpha < this, increase alpha
MAX_ALPHA = 1e5     # Upper bound for alpha
MIN_ALPHA = 1e-3     # Lower bound for alpha
ALPHA_GROWTH = 10   # Multiplier when increasing alpha
ALPHA_SHRINK = 0.1   # Multiplier when decreasing alpha

def _clip(v):
    if v < VMIN:
        return VMIN
    elif v > VMAX:
        return VMAX
    else:
        return v

def optimize_step_fd_adaptive(V, step, alpha, settle, set_voltage, measure_power, p_base=None):
    if p_base is None or math.isnan(p_base):
        p_base = measure_power()
    if math.isnan(p_base):
        return V, alpha, float('nan')

    grads = [0.0] * N
    
    # bit = np.random.choice( (-1,1) )
    # bit = 1

    # Compute gradients (forward difference)
    for k in range(N):
        base_k = V[k]
        if base_k > VMAX - step:
            set_voltage(k, base_k - step)
            time.sleep(settle)
            P = measure_power()
            grads[k] = 0.0 if (math.isnan(P) or step == 0) else (p_base - P) / step
        elif base_k < step:
            set_voltage(k, base_k + step)
            time.sleep(settle)
            P = measure_power()
            grads[k] = 0.0 if (math.isnan(P) or step == 0) else (P - p_base) / step
        else:
            # TWO-WAY GRADIENT CALCULATION
            set_voltage(k, base_k - step)
            time.sleep(settle)
            P_minus = measure_power()
            set_voltage(k, base_k + step)
            time.sleep(settle)
            P_plus = measure_power()
            grads[k] = 0.0 if (math.isnan(P_plus) or math.isnan(P_minus) or step == 0) else (P_plus - P_minus) / (2*step)
            
            # RANDOM CHOICE OF DIRECTION
            # set_voltage(k, base_k + bit*step)
            # time.sleep(settle)
            # P = measure_power()
            # grads[k] = 0.0 if (math.isnan(P) or step == 0) else bit * (P - p_base) / step


        set_voltage(k, base_k)  # Restore

    # === Adaptive Alpha Logic ===
    gradient_norm = math.sqrt(sum(g**2 for g in grads))
    
    # print(gradient_norm * alpha)

    if gradient_norm * alpha > HIGH_THRESH:
        new_alpha = alpha * ALPHA_SHRINK   # Large gradient → bigger steps
    elif gradient_norm * alpha < LOW_THRESH:
        new_alpha = alpha * ALPHA_GROWTH   # Small gradient → smaller steps
    else:
        new_alpha = alpha                   # Keep current alpha
        
    # if p_base > 1e-6:
    #     new_alpha = 1e4
    # else:
    #     new_alpha = 1e5

    new_alpha = max(MIN_ALPHA, min(MAX_ALPHA, new_alpha))  # Clamp

    # Update voltages with new_alpha
    for k in range(N):
        # print(f'V[{k}] = {V[k] + new_alpha * grads[k]}')
        V[k] = _clip(V[k] + new_alpha * grads[k])
        set_voltage(k, V[k])

    time.sleep(settle)
    p_new = measure_power()
    return V, new_alpha, p_new

# Backwards-compatible alias (optional)
optimize_step_fd = optimize_step_fd_adaptive