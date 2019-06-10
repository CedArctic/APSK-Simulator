#
#   APSK Simulator
#   Author: CedArctic, EvaSArv
#   Usage: Simulates a dual ring APSK through an AWGN channel and calculates and plots BER and SER = f(SNR)
#

import random, csv, datetime, numpy, bitarray, math, matplotlib.pyplot as plt, matplotlib.patches as mpatches
from bidict import bidict


class Symbol:

    # Symbol constructor
    def __init__(self, symbol_length, constellation, noise):

        # Length variable for the bit length per symbol (bits = log2(number_of_symbols))
        self.symbol_length = symbol_length

        # Original Symbol - the symbol as generated by the source, and its vector on the constellation
        self.original_symbol = None
        self.original_symbol_vector = None

        # Identified Symbol - the symbol as identified by the MLD Detector and its vector as received by the receiver
        # (received vector = original vector + additive white gaussian noise)
        self.identified_symbol = None
        self.received_symbol_vector = None

        self.generate_bits(constellation)
        self.add_awgn(noise, constellation)
        self.mld(constellation)


    # Generates a set of random bits for this symbol and identifies the symbol from the mapping table
    # of the provided constellation
    def generate_bits(self, constellation):

        # Initialize bits to an empty bit array and then populate it
        bits = bitarray.bitarray()

        for i in range(0, self.symbol_length):
            bits.append(random.getrandbits(1))

        # Get symbol according to bitarray from mapping table
        self.original_symbol = constellation.bit_mapping_table.inverse[bits.to01()]
        self.original_symbol_vector = constellation.vector_mapping_table[self.original_symbol]

    # AWGN Generator - Generate an Additive White Gaussian Noise sample using a Noise object and add it to the original
    # symbol vector to create the received symbol vector
    def add_awgn(self, noise, constellation):
        self.received_symbol_vector = self.original_symbol_vector + complex(float(noise.generate_awgn()),
                                                                            float(noise.generate_awgn()))

    # Identify symbol by comparing received vector with the vectors of the constellation symbols (euclidean distance)
    def mld(self, constellation):
        min_dist = math.sqrt(
            (constellation.symbols[0].original_symbol_vector.real - self.received_symbol_vector.real) ** 2
            + (constellation.symbols[0].original_symbol_vector.imag - self.received_symbol_vector.imag) ** 2)
        min_symbol = 0
        for i in range(0, constellation.ring_symbols_number * 2):
            cur_dist = math.sqrt(
                (constellation.symbols[i].original_symbol_vector.real - self.received_symbol_vector.real) ** 2
                + (constellation.symbols[i].original_symbol_vector.imag - self.received_symbol_vector.imag) ** 2)
            if cur_dist < min_dist:
                min_dist = cur_dist
                min_symbol = i
        self.identified_symbol = 's' + str(min_symbol)

    # Check if identified symbol matches original symbol
    def symbol_check(self):
        if self.original_symbol == self.identified_symbol:
            return True
        return False

    # If symbol_check returns false, check individual bits for errors and return number of bit errors according to
    # provided constellation and its mapping table
    def bits_check(self, constellation):

        # If symbols match => 0 bits errors
        if self.symbol_check() == True:
            return 0

        # If symbols don't match, compare the bitarrays
        bit_errors = 0
        for i in range(0, self.symbol_length):
            if constellation.bit_mapping_table[self.original_symbol][i] != \
                    constellation.bit_mapping_table[self.identified_symbol][i]:
                bit_errors += 1
        return bit_errors


# Symbol class for constallation constant symbols
class Constellation_Symbol(Symbol):

    # Constellation Symbol constructor
    def __init__(self, symbol_length, bits, original_symbol_vector, original_symbol):
        self.symbol_length = symbol_length
        self.bits = bits
        self.original_symbol_vector = original_symbol_vector
        self.original_symbol = original_symbol


# APSK Constellation class
class Constellation:

    # Constellation Constructor
    def __init__(self, ring_symbols_number, ri, ro):

        # Symbols per ring (an M-M APSK has M symbols per ring)
        self.ring_symbols_number = ring_symbols_number

        # Constellation Symbol Length - Calculate symbol length based on symbol number
        self.symbol_length = int(math.log2(2 * self.ring_symbols_number))

        # Inner ring radius
        self.ri = ri

        # Outer ring radius
        self.ro = ro

        # B is the ratio of ri/ro - Calculate b
        self.b = self.ri / self.ro

        # Offset Angle - The angle between two consecutive symbols, an inner and an outer ring one (in degrees)
        self.angle = 360 / (2 * self.ring_symbols_number)

        # Calculate average symbol power
        self.symbol_power = (self.ri ** 2 + self.ro ** 2) / 2

        # Constellation Power - Calculate constellation power
        self.power = self.ring_symbols_number * 2 * self.symbol_power

        # Bidirectional symbol to bit Mapping Table - used to map bit arrays to symbols and their vectors and vice versa
        self.bit_mapping_table = bidict()

        # Bidirectional symbol to vector Mapping Table - used to map bit arrays to symbols and their vectors and vice versa
        self.vector_mapping_table = bidict()

        # Create constellation symbols
        # Constellation symbols - an array containing symbol objects for the constellation - Initialize symbols list
        self.symbols = [None] * (self.ring_symbols_number * 2)

        for i in range(0, 2 * self.ring_symbols_number):

            # If i is even, place symbol on the inner ring, else place it on the outer
            if i % 2 == 0:
                x = self.ri * math.cos(i * self.angle * (math.pi / 180))
                y = self.ri * math.sin(i * self.angle * (math.pi / 180))
            else:
                x = self.ro * math.cos(i * self.angle * (math.pi / 180))
                y = self.ro * math.sin(i * self.angle * (math.pi / 180))

            # Create symbol vector and name
            original_symbol_vector = complex(x, y)
            original_symbol = 's' + str(i)

            # Create constellation symbol bitarray, add leading 0s if needed
            bits = bin(i)[2:]
            if self.symbol_length > len(bits):
                for j in range(0, self.symbol_length - len(bits)):
                    bits = '0' + bits

            # Create mapping table entry (key: original_symbol, val: bits)
            self.bit_mapping_table.put(original_symbol, bits)

            # Create mapping table entry (key: original_symbol, val: bits)
            self.vector_mapping_table.put(original_symbol, original_symbol_vector)

            # Create Constellation Symbol
            self.symbols[i] = Constellation_Symbol(self.symbol_length, bits, original_symbol_vector, original_symbol)

    # Displays the constellation
    def plot_constellation(self):
        # Plot constellation
        for i in range(0, (self.ring_symbols_number * 2)):
            plt.plot(self.symbols[i].original_symbol_vector.real,
                     self.symbols[i].original_symbol_vector.imag, 'ro-')
        circle1 = plt.Circle((0, 0), self.ri, color='r', fill=False)
        circle2 = plt.Circle((0, 0), self.ro, color='b', fill=False)
        plt.gcf().gca().add_artist(circle1)
        plt.gcf().gca().add_artist(circle2)
        plt.show()
        #plt.savefig('constellation_' + str(self.ring_symbols_number) + '-apsk_b-' + str(self.b) + '.png')


# AWGN (Additive White Gaussian Noise) class
class Noise:

    # Noise constructor
    def __init__(self, var, mean=0):
        # Noise Variance and Mean - variance determines noise power
        self.var = var
        self.mean = mean
        self.power = 2 * self.var

    # Sample Generator - generates an awgn sample or an array of them
    def generate_awgn(self, samples_number=1):
        return numpy.random.normal(self.mean, math.sqrt(self.var), size=samples_number)


# Experiment class
class Experiment:

    # Experiment constructor
    def __init__(self, des_snr, b, symbols_number, constellation):

        # Signal to Noise Ratio
        self.snr = 0

        # Symbol Error Rate
        self.ser = 0

        # Bit Error Rate
        self.ber = 0

        # Inner / Outer ring radius (b)
        self.b = b

        # Outer ring radius = 1 / desired b
        des_ro = 1 / self.b

        # Create constellation for experiment
        self.constellation = constellation

        # Calculate variance required to achieve desired SNR
        des_var = (1 + des_ro ** 2) / (4 * self.constellation.symbol_length * (10 ** (des_snr / 10)))
        print("Variance is: ", des_var)

        # Create noise for experiment
        self.noise = Noise(des_var, 0)

        # Calculate SNR
        self.snr = 10 * math.log10(
            self.constellation.symbol_power / (self.constellation.symbol_length * self.noise.power))

        # Get number of symbols for experiment - experiment symbols array size
        self.symbols_number = symbols_number

        # Symbols array for this experiment
        self.symbols_array = []

        # Plot constellation
        # self.constellation.plot_constellation()

        # Generate the symbols array
        self.symbols_array = [None] * symbols_number
        for i in range(0, self.symbols_number):
            self.symbols_array[i] = (Symbol(self.constellation.symbol_length, self.constellation, self.noise))

        # Calculate Symbol Error Rate (SER) and Bit Error Rate (BER)
        self.serNber()

        print("Length of symbols array is ", len(self.symbols_array))


    # Calculate Symbol Error Rate (SER) and Bit Error Rate (BER)
    def serNber(self):
        for i in self.symbols_array:
            if i.bits_check(self.constellation) != 0:
                self.ser += 1
                self.ber += i.bits_check(self.constellation)
        self.ser = self.ser / self.symbols_number
        self.ber = self.ber / (self.symbols_number * self.constellation.symbol_length)


# Plots results and exports them to csv
def plotter(snr_start, b, ring_symbols_number, symbols_number, color):
    with open('results.csv', 'a', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(['b = ' + str(b)])

        # Create constellation for the following experiments
        constellation = Constellation(ring_symbols_number, 1, (1/b))

        # Lists for results coordinates
        snrList=[]
        berList=[]

        # Create experiment and calculate SER and BER, then plot the points
        for i in range(0, 10):
            print("\nPlotter i is:", i)
            experiment = Experiment(snr_start + 0.25 * i, b, symbols_number, constellation)
            experiment.serNber()
            print("BER:", experiment.ber, "SER:", experiment.ser, "SNR:", experiment.snr)
            snrList.append(snr_start + 0.25 * i)
            berList.append(experiment.ber)
            plt.plot(snrList[i], berList[i], color)
            # Export results (ber, ser, snr)
            csv_writer.writerow([experiment.ber, experiment.ser, experiment.snr])

        #Plot lines connecting the already plotted points
        plt.plot(snrList, berList, color, linewidth=3)


# Main function
def main():
    print("Starting time:", datetime.datetime.now())

    # Get number of samples for the experiments
    symbols_number = int(input("Enter number of symbols for this experiment:"))

    # Get number of symbols per ring
    ring_symbols_number = int(input("Enter number of symbols per ring:"))

    # Get pairs of b and SNR starting points for plotting
    print("Enter inner / outer ring ratio (b) and the desired SNR from which plotting will begin")
    b_snrStart_table = []

    for i in range(0, 5):
        print("Pair ", i)
        b = float(input("Enter b:"))
        snr_start = float(input("Enter SNR plot starting point:"))
        b_snrStart_table.append([b, snr_start]);

    # Lists for plotting and legend creation
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    handles=[]

    # Run plotter and prepare handles for plot figure legend
    for j in range(0, 5):
        plotter(b_snrStart_table[j][1], b_snrStart_table[j][0], ring_symbols_number, symbols_number, colors[j] + 'o-')
        handles.append(mpatches.Patch(color=colors[j], label='b = ' + str(b_snrStart_table[j][0])))

    # Add titles, change y axis scale, and print plot
    plt.title(str(ring_symbols_number) + "-" + str(ring_symbols_number) + "-APSK")
    plt.legend(handles=handles)
    plt.xlabel("SNR: Eb/No dB")
    plt.ylabel("Bit Error Rate")
    plt.yscale('log', nonposy='clip')
    plt.show()

    # Print constellations after clearing plot
    for k in range(0, 5):
        plt.clf()
        plt.title(str(ring_symbols_number) + "-" + str(ring_symbols_number) + "-APSK Constellation with b = " + str(b_snrStart_table[k][0]))
        constellation = Constellation(ring_symbols_number, 1, (1/b_snrStart_table[k][0]))
        constellation.plot_constellation()
        plt.show()

    print("End time:", datetime.datetime.now())


# Call main to run the program
main()
