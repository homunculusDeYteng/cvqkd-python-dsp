# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 13:07:03 2026

@author: admin
"""

import time
import math
import random

def optimize_step_spsa(V, step, alpha, settle, apply_voltages, measure_power):
  
    V = [float(x) for x in V]
   
    #Generate a random perturbation vector (+1 or -1 for each channel)
    delta = [random.choice([-1.0, 1.0]) for _ in range(4)]
   
    # ALL channels UP simultaneously
    V_plus = [max(0.0, min(5.0, V[i] + step * delta[i])) for i in range(4)]
    apply_voltages(V_plus)
    time.sleep(settle)
    P_plus = measure_power()
   
    #ALL channels DOWN simultaneously
    V_minus = [max(0.0, min(5.0, V[i] - step * delta[i])) for i in range(4)]
    apply_voltages(V_minus)
    time.sleep(settle)
    P_minus = measure_power()
   
    
    if math.isnan(P_plus) or math.isnan(P_minus):
        apply_voltages(V)
        return V
   
    V_new = [0.0] * 4
    for i in range(4):

        grad_i = (P_plus - P_minus) / (2.0 * step * delta[i])
       

        V_new[i] = V[i] - (alpha * grad_i)
       
        V_new[i] = max(0.0, min(5.0, V_new[i]))
       

    apply_voltages(V_new)
    time.sleep(settle)
   
    return V_new