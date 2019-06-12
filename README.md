# APSK-Simulator 
This application simulates a telecommunication system where the Amplitude Phase Shift Keying (APSK) constellation is used to send data over a simple Additive White Gaussian Noise (AWGN) channel. We then study APSK constellation performance for a varying ratio of inner / outer ring radius and Signal to Noise Ratio (SNR).

## Description
The simulator works by first generating random bits based on the desired number of symbols to be sent. These bits are then converted into symbols based on the user defined APSK constellation with two rings. Each symbol has an AWGN sample, with 0 mean and variance depending on the desired SNR, added to it. Note that when we refer to SNR in this application, we are refering to the bit energy to N0 fraction (Eb / N0) in decibels, which is directly connected to the actual SNR. Finally the symbols are run through a Maximum Likelihood Detector (MLD) which decodes them to symbols and bits. Finally the Symbol Error Rate (SER) and Bit Error Rate (BER) are calculated and are graphed along with SNR levels.

When running the application the user is first prompted for a sample size which is how many symbols the simulation will run for. Note that if we desire to study an APSK constellation for a range of SNR that will result in a BER of 10^(-6) for example, it is advised to use at least 10^7 symbols for a reliable output.

The user is then prompted to enter the number of symbols on both rings of the APSK constellation and then 5 pairs of values for b and starting SNR points. We define b as ratio of the inner circle radius of the APSK constellation to the outter ring radius. The constellations are built automatically using b and the symbols per ring provided. Note that for the purposes of the simulation we have predefined the radius of the inner circle to 1 as our objective is to study the constellations performance based on their value of b. The SNR starting point defines from where graphing will begin for the curve of that specific b. The application is currently set to graph for fine points onwards from the starting point, each 0.5 dB further than the previous one. 

The end result will be a graph of 5 curves each corresponding to a different value of b. The X axis is the SNR in dB and the Y axis is the BER.

## Problem modeling
In this section the relationships of our model objects will be explained. More details about how the objects interact with eachother to produce the end result can be seen in the well documented with comments code.

### Experiment
An Experiment object is connected with a Constellation object that correspond to that specific experiment. Each experiment contains a number of random generated symbols to which AWGN samples are added and are then run through an MLD leading finally to the calculation of SER and BER for the constellation. Experiments are graphed as dots in the end results.

### Constellation
A Constellation object contains all the information related to an APSK constellation including a set of symbols that are generated based on b and the number of symbols on each ring.

### Symbol
A symbol object contains information related to a specific instance of a symbol including its original symbol and vector as sent by the sender and the vector and symbol as detected by the receiver's MLD as well as a noise object. The constellation symbol object is a modified version of the symbol especially to be used inside Constellation objects.

### Noise
Contains information required to generate AWGN samples to be added to each symbol.


## Usage
1. Install a 64 bit version of Python 3 and all dependencies listed bellow
2. Run apsk_simulator.py and enter information according to the description given above when prompted

## Requirements
* Python 3
* numpy
* bitarray
* matplotlib.pyplot 
* matplotlib.patches
* bidict

## Credits
The simulator was authored by myself and [EvaSArv](https://github.com/EvaSArv/)
