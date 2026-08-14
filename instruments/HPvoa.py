# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 15:34:33 2026

@author: Yulin Teng
"""

import pyvisa
from typing import Any



class HPVOA:
    """HP/Keysight Variable Optical Attenuator control class."""

    def __init__(self, _location: Any = 'GPIB0::20::INSTR', **_kwargs) -> None:
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(_location)
        self.instrument.timeout = 10000 
        self.instrument.read_termination = '\n'
        self.instrument.write_termination = '\n'

    def set_value(self, value: float) -> None:
        """Set VOA attenuation value in dB."""
        self.instrument.write(f":INPut:ATTenuation {value}")
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def block_light(self) -> None:
        """Turn off the optical output (Matches outputHP('OFF'))."""
        self.instrument.write(":OUTPUT OFF")

    def open_light(self) -> None:
        """Turn on the optical output (Matches outputHP('ON'))."""
        self.instrument.write(":OUTPUT ON")

    def close(self) -> None:
        """Close the VISA communication session."""
        if hasattr(self, 'instrument') and self.instrument:
            self.instrument.close()
        if hasattr(self, 'rm') and self.rm:
            self.rm.close()