[readme.md](https://github.com/user-attachments/files/31072903/readme.md)
# Attention!!!
#Remember to close the feedbackloops(press Q on the matplot animation) before closing this project!!! If not, reboot the computer.

# CV-QKD Automation 13/08/2026

Author of code: Yulin Teng 

This document explains how the codebase is organized
## 1.structure

```
Working_codes_Yulin/
|
+-- instruments/                      HAL classes
|   +-- dac_HAL_v1.py                 KeysightAWG   (Keysight M8195A AWG)
|   +-- DSOZ540A_measurement_V1.py    KeysightDSOZ540A (classical channel Oscilloscope/big)
|   +-- MSO44_measurement_V1.py       TektronixMSO  (quantum channel Oscilloscope/small)
|   +-- HPvoa.py                      HP variable optical attenuator
|   +-- local_oscillator.py           local_oscillator (NKT_Koheras laser(bottom))
|   +-- powermeter_HAL_v1.py          AndoPowerMeter, HP437BPowerMeter(feedback_loops)
|
+-- waveform_generation/              Alice-side signal generation
|   +-- waveform_gen.py               generate_waveforms, generate_quantum_only_waveform
|   +-- AWG_load.py                   load and emit waveform
|   +-- functions/                    DSP building blocks used by waveform_gen.py to build the classical and quantum waveforms.
|       +-- lfsr.py                   Generates a pseudo-random bit sequence using a Fibonacci-style linear feedback shift register.
|       +-- qpsk.py                   Maps a flat bit sequence to QPSK symbols.
|       +-- generate_nqam_mapping.py  Builds a square N-QAM constellation.
|       +-- sample_symbols.py         Draws N symbols from a constellation with Gaussian amplitude shaping
|       +-- encode_bits_to_symbols.py Convert between a flat bit sequence and QAM symbol indices
|       +-- decode_symbols_to_bits.py 
|       +-- rrcfilter.py              Applies a root-raised-cosine pulse-shaping filter in the frequency domain
|       +-- pilot_frame.py            composes several of the functions above into the actual quantum frame
|
+-- measurement/                      Bob-side acquisition
|   +-- noise_measurement.py          shot-noise acquisition
|   +-- signal_measurement.py         combined classical+quantum acquisition
|   +-- simultaneous_mso_dpo.py       synchronized two scopes capture
|   +-- data_measurement.py           full measurement run
|   +-- Measure_elec_noise.py         electronic noise calibration
|
+-- feedback_control/                 Polarization stabilization (Alice + Bob loops)
    +-- feedback_alice.py             entry point: Alice loop
    +-- feedback_bob.py               entry point: Bob loop
    +-- optimizer_min.py              optimizer used by feedback_alice.py
    +-- optimizer_max.py              optimizer used by feedback_bob.py
```

##2.operation

Emit waveform(AWG_load.py) ---> Open both feedback loops(feedback_alice(bob).py), wait the power to be stable
---> measurement(data_measurement.py)









