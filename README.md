# APSK-Simulator 
This application simulates a telecommunication system where the Amplitude Phase Shift Keying (APSK) constellation is used to send data over a simple Additive White Gaussian Noise (AWGN) channel.

## Description
The simulator works by first generating random bits based on the desired number of symbols to be sent. These bits are then converted into symbols based on the user defined APSK constellation. Each symbol has an AWGN sample, with 0 mean and variance depending on the desired Signal to Noise Ratio (SNR), added to it. Finally the symbols are run through a Maximum Likelihood Detector (MLD) which decodes them to symbols and bits. Finally the Symbol Error Rate (SER) and Bit Error Rate (BER) are calculated and are graphed along with SNR levels.  

## Usage
1. Install a 64 bit version of Python 3 and all dependencies listed bellow
2. Run apsk_simulator.py

## Requirements
* Python 3
* numpy
* bitarray
* matplotlib.pyplot 
* matplotlib.patches
* bidict

## Credits
The simulator was authored by myself and [EvaSArv](https://github.com/EvaSArv/)
