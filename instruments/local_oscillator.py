# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 12:01:18 2026

@author: Yulin Teng
"""
from nkt_tools import NKTP_DLL as nkt
import time


PORT = 'COM4'
MODULE = 15


REG_POWER_SETPOINT = 0x23
REG_WAVELENGTH_SETPOINT = 0x25
REG_WAVELENGTH_OFFSET = 0x28
REG_EMISSION = 0x30
    
    
    
class local_oscillator:
    
    def __init__(self, port:str = PORT, module:int = MODULE):
        self.port = port
        self.module = module
        nkt.closePorts(self.port) #closes serial connection
        nkt.openPorts(self.port, 1, 0)
        
            
        time.sleep(3)
        
    
    def emission_on(self):
        nkt.registerWriteU8(self.port, self.module, REG_EMISSION, 1, -1)
        
            
    def emission_off(self):
        nkt.registerWriteU8(self.port, self.module, REG_EMISSION, 0, -1)
        
    
    def set_power_mw(self, power_mw:float):
        value = int(power_mw * 100)
        nkt.registerWriteU16(self.port, self.module, REG_POWER_SETPOINT, value, -1)
        
        
        return power_mw
    
    def get_power_mw(self):
        result, value = nkt.registerReadU16(self.port, self.module, REG_POWER_SETPOINT, -1)
        
        return value / 100

    def set_wavelength_nm(self, wavelength_nm: float):
        offset_nm = self.get_wavelength_offset_nm()
        setpoint_pm = int((wavelength_nm- offset_nm)*1000)
        nkt.registerWriteU16(self.port, self.module, REG_WAVELENGTH_SETPOINT, setpoint_pm, -1)
        
    
    def get_wavelength_nm(self):
        offset_nm = self.get_wavelength_offset_nm()
        result, setpoint_pm = nkt.registerReadU16(self.port, self.module, REG_WAVELENGTH_SETPOINT, -1)
        
        return offset_nm + setpoint_pm / 1000.0

    def get_wavelength_offset_nm(self):
        result, value = nkt.registerReadU16(self.port, self.module, REG_WAVELENGTH_OFFSET, -1)
        
        return float(value)

    def close(self):
        nkt.closePorts(self.port)

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        