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
    matrix = []
    for d1 in (0,1):
        for d2 in (0,1):
            for d3 in (0,1):
                matrix.append((d1,d2,d3))
    
    return np.array(matrix)[1:].T

def gen_steane_code(matrix):
    simplex_values = []
    # The most cursed shi I have ever seen
    for d1 in (0,1):
        for d2 in (0,1):
            for d3 in (0,1):
                # Group theory stuff, check out cosets n stuff
                simplex_values.append(d1*matrix[0] ^ d2*matrix[1] ^ d3*matrix[2])

    simplex_values = np.array(simplex_values)      # 0_L qubits
    dual_values = simplex_values ^ [1,1,1,1,1,1,1] # 1_L qubits

    return simplex_values, dual_values

if __name__ == "__main__":
    pass

# Next one does the XZ thingy