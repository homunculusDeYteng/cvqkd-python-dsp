
import numpy as np

from qosst_hal.dac import GenericDAC
from qosst_hal.exceptions import QOSSTHardwareError


from typing import List

import time

import pyarbtools


class KeysightAWG(GenericDAC):
    """DAC of the Keysight M8195A AWG."""
    
    awg: "pyarbtools.instruments.M8195A"
    location: str = 'localhost'
    channels: List[int]
    dac_rate: float 
    amplitude: float
    
    MAX_VOLTAGE: float = 0.5
    DEFAULT_FS: float = 64e9
    
    
    def __init__(self, location: str, channels: List[int], **kwargs):
        self.location = location
        '''
        Initialize the DAC with its location and the list of channels to use
        '''
        self.channels = channels
        # self.wfm_ids = {} #Dictionary to store waveform ids TODO check
        
        self.awg = pyarbtools.instruments.M8195A(self.location, apiType='pyvisa', protocol='hislip', port=0, timeout=10, reset=False)
        
        # Configure clock and AWG mode
        self.awg.configure(dacMode='four', refSrc='ext')
        
        
            
    def open(self):
        pass
    
    def close(self):
        pass
            
    def set_emission_parameters(self, **kwargs) -> None:
        '''
        Set emission parameters like sample rate, amplitude, or DAC mode.
        
        Args:
            channels  (List[int]): list of channels to use.
            dac_rate (float): rate to use.
            amplitudes (float, optional): list of amplitude to use for the different DAC channels.

        '''
        channels = kwargs.pop("channels")
        dac_rate = kwargs.pop("dac_rate")
        amplitude = kwargs.pop("amplitude", self.MAX_VOLTAGE)
        self._set_emission_parameters(channels, dac_rate, amplitude)
    
    def _set_emission_parameters(
            self,
            channels: List[int],
            dac_rate: float,
            amplitude: float = MAX_VOLTAGE):
        
        self.channels = channels
        
        self.dac_rate = dac_rate
        self.awg.configure(fs=dac_rate)
        
        if amplitude > self.MAX_VOLTAGE:
            raise QOSSTHardwareError(
                f"Amplitude ({amplitude} V) is greater than the maximum allowed voltage ({self.MAX_VOLTAGE} V)"
            )
        
        self.amplitude = amplitude
        for i, channel_id in enumerate(self.channels):
            exec(f"self.awg.configure(amp{channel_id} = self.amplitude)")
        
        
        
    def load_data(self, data: List[np.ndarray]):
        """
        Load a list of numpy arrays into the DAC, one for each channel.
        """
        
        
        if len(data) != len(self.channels):
            raise ValueError("The number of numpy arrays in 'data' must match the number of channels.")
            
        
        # Clear the AWG memory
        self.awg.clear_all_wfm()
        
        # for i, channel in enumerate(self.channels):
            
        #     norm_data = data[i] / np.amax(data[i])
        #     self.awg.download_wfm(norm_data, ch = channel, name = f'qosst_wfm_ch{channel}')


        for i, channel in enumerate(self.channels):
            if np.amax(np.abs(data[i])) > 1:
                print(f'Channel {channel}: data normalized')
                norm_data = data[i] / np.amax(np.abs(data[i]))
            else:
                print(f'Channel {channel}: data not normalized')
                norm_data = data[i]
                
            
            
            self.awg.download_wfm(norm_data, ch = channel, name = f'qosst_wfm_ch{channel}')
            time.sleep(0.2)

        

    def set_data_extended_memory_mode(self):
        
        
        #clear 
        self.awg.write(':ABOR')
        time.sleep(1)
        
        for ch in [1,2,3,4]:
            self.awg.write(f':TRAC{ch}:DEL:ALL')
        
        time.sleep(1)
            
        #Divider    
        self.awg.write(':INST:MEM:EXT:RDIV DIV4')
        
        time.sleep(1)
        
        #Switch mode
        #self.awg.write(':TRAC4:MMOD EXT')
        for ch in [1,2,3,4]:
            self.awg.write(f':TRAC{ch}:MMOD EXT')
        
        time.sleep(1)
            
            
    def set_data_internal_memory_mode(self):
        
        # clear
        self.awg.write(':ABOR')
        time.sleep(1)

        for ch in [1,2,3,4]:
            self.awg.write(f':TRAC{ch}:DEL:ALL')
        
        time.sleep(1)

        #Switch mode
        # self.awg.write(':TRAC1:MMOD INT')
        for ch in [4,3,2,1]:
            self.awg.write(f':TRAC{ch}:MMOD INT')
        
        time.sleep(1)
                
        #Divider    
        self.awg.write(':INST:MEM:EXT:RDIV DIV1')

            
        
        
    def start_emission(self):
        '''
        Start the emission of the loaded data on all configured channels.
        '''
        for i, channel in enumerate(self.channels):
            self.awg.write(f':TRAC{channel}:SEL 1')
            self.awg.write(f':OUTP{channel} ON')
        
        self.awg.write("init:cont on")
        self.awg.write("init:imm")

            
    def stop_emission(self):
        '''
        Stop the emission of the data, turn off outputs, and clear memory.
        '''
        
        self.awg.write(':ABOR')
            
    