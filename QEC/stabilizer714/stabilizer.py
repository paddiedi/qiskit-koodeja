from qiskit.quantum_info import Statevector
from qiskit import transpile, QuantumCircuit, ClassicalRegister
#from qiskit.circuit import Parameter
from qiskit_aer import AerSimulator
from qiskit.circuit.library import ZGate
from qiskit.visualization import plot_histogram

import matplotlib.pyplot as plt
import random
import numpy as np


# This is an implementation of the 7,1,3 Steane code, in the stabilizer formalism.


def simulate_measurements(qc_samples, shots):
    backend = AerSimulator(seed_simulator = random.randint(0,10000000))
    qc_t = transpile(qc_samples, backend)
    job = backend.run(qc_t, shots=shots)
    return job.result()


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

def add_x_gate(qubit,a):
    pass

def add_z_gate(qubit,a):
    pass

def prepare_state_amp(steane_matrix):
    bit_string = ""
    n_string = len(steane_matrix[0])
    amps = np.zeros(2**n_string, dtype=complex) # The amplitude can be complex
    n_rows = len(steane_matrix)
    for column in steane_matrix:
        for char in column:
            bit_string += str(int(char))
        amps[int(bit_string,2)] = 1/np.sqrt(n_rows)
        bit_string = ""
    return amps

if __name__ == "__main__":
    # Apparently we need 2 different circuits (because qiskit is goofy)
    qc_simplex = QuantumCircuit(7) # 7 sized qubits
    qc_dual = QuantumCircuit(7) # 7 sized qubits
    hamming_code = gen_hamming_code()
    pair_steane_matrix = gen_steane_code(hamming_code)
    simplex_matrix = pair_steane_matrix[0] # |0_L>
    dual_matrix = pair_steane_matrix[1]    # |1_L>

    amp_simplex = prepare_state_amp(simplex_matrix)
    amp_dual = prepare_state_amp(dual_matrix)
    output_register = ClassicalRegister(0, "output")
    qc_simplex.initialize(amp_simplex, [i for i in range(0,len(simplex_matrix)-1)])
    qc_dual.initialize(amp_dual, [i for i in range(0, len(dual_matrix)-1)])
    #init_simplex = Statevector
    qc_simplex_samples = qc_simplex.copy()
    qc_simplex_samples.measure_all()
    result = simulate_measurements(qc_simplex_samples, 1000)
    plot_histogram(result, sort='asc')

# Next one does the XZ thingy