
    
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 14:41:18 2026

@author: admin
"""

import time
import math
from typing import List
import numpy as np
import pyvisa

class TektronixMSO:
    
    def __init__(self, resource_address: str = 'TCPIP0::192.168.0.5::inst0::INSTR'):
        self.resource_address = resource_address
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(self.resource_address)
        self.inst.timeout = 15000  # ms
        
        self.active_channels = [1]
        self.points = 1000000
        self.sample_rate = 500e6
        
        self.inst.clear()
        self.inst.write("*CLS")
    def run(self):
        self.inst.write("RUN")
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
        
    def set_acquisition_parameters(self, channels: List[int] = None, points: int = None, sample_rate: float = None):
        
        if channels is not None:
            self.active_channels = channels
            
        self.inst.write(":HORIZONTAL:MODE MANUAL")
            
        if points is not None:
            self.inst.write(f"HORizontal:MODE:RECOrdlength {points}")
            
        if sample_rate is not None:
            self.inst.write(f"HORizontal:MODE:SAMPLERate {sample_rate}")
            
        
        self.points = int(self.inst.query("HORizontal:MODE:RECOrdlength?"))
        self.sample_rate = float(self.inst.query("HORizontal:MODE:SAMPLERate?"))
        
        if points is not None and self.points != points:
            print(f"WARNING: Requested {points} points, but scope changed to {self.points}.")
            
        if sample_rate is not None and self.sample_rate != sample_rate:
            print(f"WARNING: Requested {sample_rate} Sa/s, but scope changed to {self.sample_rate} Sa/s.")
            
        self.inst.chunk_size = int(math.floor(10.1 * self.points))

        self.inst.write(":DATA:ENCdg SRPbinary")
        self.inst.write("DATa:WIDth 2")
        
    def set_trigger_parameters(self, level: float = 1.0, slope: str = 'RISE'):#RISe|FALL|EITher
        
        self.inst.write("TRIGger:A:TYPe EDGE")
        
        self.inst.write("TRIGger:A:EDGE:SOUrce AUX")
        
        self.inst.write(f"TRIGger:A:EDGE:SLOpe {slope}")
        
        self.inst.write(f"TRIGger:AUXLevel {level}")
        
        print(f"Trigger set to AUX, Level: {level}V, Slope: {slope}")
    
    def force_trigger(self):
        """Force an immediate trigger, regardless of the trigger source."""
        self.inst.write("TRIGger FORCe")
    
    def arm_acquisition(self):
        self.inst.write("ACQUIRE:STOPAFTER SEQUENCE")
        self.inst.write("ACQuire:SEQuence:MODe 1")
        self.inst.write(":ACQuire:STATE RUN")
        
    def stop_acquisition(self):
        self.inst.write("ACQ:STATE STOP")
        
    def trigger(self):
        self.inst.write("*TRG")
        
    def set_vertical_scale(self, scale_volts: float, channels: List[int] = None):
        if channels is None:
            channels = self.active_channels
        for ch in channels:
            self.inst.write(f":CH{ch}:SCAle {scale_volts}")

    def set_bandwidth(self, bandwidth_hz: float, channels: List[int] = None):
        if channels is None:
            channels = self.active_channels
        for ch in channels:
            self.inst.write(f":CH{ch}:BANdwidth {bandwidth_hz}")

    def set_trigger_mode(self, mode: str = 'NORMal'):#NORMal or AUTO
        
        self.inst.write(f"TRIGger:A:MODe {mode}")
        
    def set_aux_output(self, source: str = 'ATRIGger'): #source: ATRIGger | REFOUT | AFG"
        self.inst.write(f'AUXout:SOUrce {source}')
        
        
    def set_aux_sync(self, source='ATRIGger'):
        self.inst.write(f'AUXout:SOUrce {source}')
        
    def get_data(self) -> List[np.ndarray]:
        retry = 0
        done = False
        
        while not done and retry < 500:
            try:
                state = int(self.inst.query("ACQ:STATE?"))
                if state == 0:
                    done = True
            except ValueError:
                pass
            if not done:
                time.sleep(0.1)
                retry += 1

        if not done:
            raise TimeoutError("Scope did not complete acquisition or timed out.")

        results = []
        for ch in self.active_channels:
            self.inst.write(f":DATa:SOUrce CH{ch}")
            self.inst.write(":DATA:START 1")
            self.inst.write(f"DATA:STOP {self.points}")

            yzero = float(self.inst.query("WFMOutpre:YZEro?"))
            yoff = float(self.inst.query("WFMOutpre:YOff?"))
            ymult = float(self.inst.query("WFMOutpre:YMult?"))

            self.inst.write(":CURVe?")
            raw_data = self.inst.read_binary_values(
                datatype='H', 
                is_big_endian=False, 
                container=np.ndarray
            )
            
            raw_data = raw_data.astype(np.float64) - math.floor(65535 / 2)
            voltage_data = (raw_data - yoff) * ymult + yzero
            results.append(voltage_data)

        return results
    
        
    def close(self):
        self.inst.close()
        self.rm.close()
'''
if __name__ == '__main__':
    scope = TektronixMSO()
    scope.set_acquisition_parameters(
        channels=[2,3], 
        points=int(1e6), 
        sample_rate=625e6
    )
    scope.arm_acquisition()
    
    start_time = time.time()
    data = scope.get_data()
    ch3 = data[2]
    ch4 = data[3]
    
    print(f"Elapsed time: {time.time() - start_time:.3f} seconds")
    print(f"Acquired {ch3.size} points on CH3.")
    print(f"Acquired {ch4.size} points on CH4.")
    
    scope.close()
'''
    
    
    
    
    
    
    
