
from qosst_hal.powermeter import GenericPowerMeter
import pyvisa
import sys
import math
import time
import re

class AndoPowerMeter(GenericPowerMeter):
    """
    Ando AQ2140 PowerMeter implementation.
    """
    def __init__(self,resource_name:str, *args, **kwargs):
        self.resource_name = resource_name
        self.rm = pyvisa.ResourceManager()
        
        self.inst = self.rm.open_resource(self.resource_name)
        
    def open(self) -> None:
        pass
            
    def close(self) -> None:
        pass
        
    def read(self):
        pow_str = self.inst.query('OD1').strip()
        
        if len(pow_str) < 7:
            return math.nan
        
        prefix = pow_str[0:6]  
        val = float(pow_str[7:])
        
        if prefix == 'AI1RRA':
            pow_w = val * 1e-9
        elif prefix == 'AI1PRA':
            pow_w = val * 1e-3
        elif prefix == 'AI1QRA':
            pow_w = val * 1e-6
        elif prefix == 'AI1SRA':
            pow_w = val * 1e-12
        elif prefix == 'AIAURA':
            # Value is in dBm, convert to Watts
            pow_w = 10 ** ((val - 30) / 10)
        else:
            pow_w = math.nan

        return pow_w
    
    def __str__(self):
        return "Generic PowerMeter"
    
class HP437BPowerMeter(GenericPowerMeter):
    def __init__(self, resource_name: str, read_mode: str = "TR1_READ", 
                 trigger_delay_s: float = 0.15, use_auto_range: bool = True, 
                 force_linear_watts: bool = True, *args, **kwargs):
        
        self.resource_name = resource_name
        self.read_mode = read_mode.upper()
        self.trigger_delay_s = trigger_delay_s
        self.rm = pyvisa.ResourceManager()
        
        self.inst = self.rm.open_resource(self.resource_name)
        
        # Configure terminator and timeout
        self.inst.timeout = 10000  # PyVISA uses milliseconds (10s = 10000ms)
        self.inst.read_termination = '\r\n'
        self.inst.write_termination = '\r\n'
        
        # Instrument initialization
        if force_linear_watts:
            
            self.inst.write("LN")  # HP437 syntax for Linear Watts
            time.sleep(0.2)
            
        if use_auto_range:
            self.inst.write("RA")
            time.sleep(0.2)
            
        if self.read_mode == "TALK_ONLY":
            self.inst.write("TR3")
            time.sleep(0.2)
            
    
    def open(self) -> None:
        """Open the connection (handled in __init__, but kept for interface consistency)."""
        pass
            
    def close(self) -> None:
        """Close the instrument connection."""
        if hasattr(self, 'inst') and self.inst:
            self.inst.close()
        
    def read(self) -> float:
        try:
            self.inst.flush(pyvisa.constants.BufferOperation.discard_read_buffer)
        except AttributeError:
            self.inst.clear()

        if self.read_mode == "TR1_READ":
            self.inst.write("TR1")
            time.sleep(self.trigger_delay_s)
            raw = self.inst.read()
        elif self.read_mode == "TALK_ONLY":
            raw = self.inst.read()
        elif self.read_mode == "TK_QUERY":
            raw = self.inst.query("TK?")
        else:
            raw = self.inst.read()
            
        raw = raw.strip()

        # Pass the raw string directly through your validation method!
        return self._parse_and_validate(raw)

    def _parse_and_validate(self, raw: str) -> float:
        if "E+40" in raw or "ERR" in raw.upper():
            raise RuntimeError(f"HP437B Instrument Error / Sensor Unplugged! Raw string: '{raw}'")

        match = re.search(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', raw)
        if not match:
            raise ValueError(f"Could not parse HP437B string: '{raw}'")
            
        p_w = float(match.group(0))
        
        # NO CLAMPING! Let the negative thermal noise pass through.
        
        if abs(p_w) > 1e10:
            raise RuntimeError(f"HP437B returned out-of-range value: {p_w}")
            
        return p_w

    def _decode_error(self, p_w: float) -> str:
        s = f"{abs(p_w):.4E}"
        # Match 9.00 or 9.02 (or any 9.xx) error codes
        match = re.search(r'9\.(\d\d)(\d\d)E\+40', s)
        if match:
            return match.group(1) + match.group(2)
        return "unknown"

    def __str__(self):
        return f"HP437B PowerMeter ({self.resource_name})"
    
'''  
if __name__ == "__main__":
    print("Start")
    
    try:
       
        powermeter = AndoPowerMeter("GPIB0::2::INSTR")
        print("connected")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit()

    print("3 power readings")
    for i in range(3):
        power_val = powermeter.read()
        print(f"Reading {i+1}: {power_val} Watts")
        time.sleep(1)  # Pause for 1 second between reads
'''