import time
from typing import List
import numpy as np 
import pyvisa

class KeysightDSOZ540A:
    
    def __init__(self, resource_address: str = 'TCPIP0::192.168.0.10::hislip0::INSTR'):
        self.resource_address = resource_address
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(self.resource_address)
        self.inst.timeout = 10000
        self.active_channels = [1, 2, 3, 4]
        self.inst.write("*CLS")
    def run(self):
        self.inst.write(":RUN")
        
    def __enter__(self):
        return self
    

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def set_acquisition_parameters(self, 
                                   channels: List[int] = None, 
                                   points: int = None, 
                                   sample_rate: float = None,
                                   voltage_scale: float = None,
                                   voltage_range: float = None) -> None:
        
        # Channel Selection and Display
        if channels is not None:
            self.active_channels = channels
            for ch in self.active_channels:
                self.inst.write(f":CHANnel{ch}:DISPlay ON")

        # Points and Sample Rate
        if points is not None:
            self.inst.write(f":ACQuire:POINts:ANALog {points}")
            
        if sample_rate is not None:
            self.inst.write(f":ACQuire:SRATe:ANALog {sample_rate}")

        # Read actual values back
        self.points = int(self.inst.query(":ACQuire:POINts?").strip())
        self.sample_rate = float(self.inst.query(":ACQuire:SRATe:ANALog?").strip())
        
        if points is not None and self.points != points:
            print(f"WARNING: Requested {points} points, but scope changed to {self.points}.")
        if sample_rate is not None and self.sample_rate != sample_rate:
            print(f"WARNING: Requested {sample_rate} Sa/s, but scope chenaged to {self.sample_rate} Sa/s.")

        # Timebase Scale Calculation
        if points is not None and sample_rate is not None:
            timebase_scale = points / sample_rate / 10.0
            self.inst.write(f":TIMebase:SCALe {timebase_scale}")

        # Vertical Settings (Range OR Scale)
        if voltage_range is not None:
            for ch in self.active_channels:
                self.inst.write(f":CHANnel{ch}:RANGe {voltage_range}")
        elif voltage_scale is not None:
            for ch in self.active_channels:
                self.inst.write(f":CHANnel{ch}:SCALe {voltage_scale}")

        #  Static Setup Commands 
        self.inst.write(":TIMebase:POSition 0")
        self.inst.write(":TIMebase:REFerence CENTER")
        
        # 6. Data Transfer Formatting
        self.inst.write(":WAVeform:FORMat WORD")
        self.inst.write(":WAVeform:BYTeorder MSBFIRST")
        self.inst.write(":ACQuire:INTerpolate OFF")
        self.inst.write(":ACQuire:MODE RTIMe")

    def set_trigger_parameters(self, trigger_level: float = 0.0, slope: str = 'POSitive',
                               source: str = 'AUX'):
        self.inst.write(":TRIGger:MODE EDGE")
        self.inst.write(f":TRIGger:EDGE:SOURce {source}")
        self.inst.write(f":TRIGger:LEVel {source},{trigger_level}")
        self.inst.write(f":TRIGger:EDGE:SLOPe {slope}")
        self.inst.write(":TRIGger:SWEep TRIGgered")
        
        src = self.inst.query(":TRIGger:EDGE:SOURce?").strip()
        lvl = self.inst.query(f":TRIGger:LEVel? {source}").strip()
        print(f"DPO trigger set to source: {src}, level: {lvl}, slope: {slope}")
    def arm_acquisition(self):
        self.inst.query(":ADER?")
        self.inst.write(":SINGLE")
        
    def stop_acquisition(self):
        self.inst.write(":STOP")
        
    def trigger(self):
        self.inst.write("*TRG")
        
    def get_data(self):
        retry = 0
        done = False
        while not done and retry < 500:
            try:
                if int(self.inst.query(":ADER?").strip()) != 0:
                    done = True
            except ValueError:
                pass
            if not done:
                time.sleep(0.1)
                retry += 1

        if not done:
            raise TimeoutError("Scope did not trigger or acquisition timed out.")

        results = []
        for ch in self.active_channels:
            self.inst.write(f":WAVeform:SOURce CHANnel{ch}")
            preamble = self.inst.query(":WAVeform:PREamble?").split(',')
            y_increment = float(preamble[7])
            y_origin = float(preamble[8])
            y_reference = float(preamble[9])
            
            raw_data = self.inst.query_binary_values(
                ":WAVeform:DATa?", datatype='h', is_big_endian=True, container=np.ndarray
            )
            
            voltage_data = (raw_data - y_reference) * y_increment + y_origin
            results.append(voltage_data)

        return results
        
    def close(self):
        self.inst.close()
        self.rm.close()