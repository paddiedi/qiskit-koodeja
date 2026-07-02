from qiskit.quantum_info import Statevector
from qiskit import transpile, QuantumCircuit
#from qiskit.circuit import Parameter
from qiskit_aer import AerSimulator
from qiskit.circuit.library import ZGate
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np


# This is an implementation of the 7,1,3 Steane code, in the stabilizer formalism.

def gen_hamming_code():
    columns = []
    for b1 in (0,1):
        for b2 in (0,1):
             for b3 in (0,1):
                  columns.append()



def css_generate_basis():
	return gen_hamming_code()

if __name__ == "__main__":
     gen_hamming_code()