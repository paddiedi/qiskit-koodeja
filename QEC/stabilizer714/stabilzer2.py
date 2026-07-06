from qiskit import transpile, QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import qiskit_aer.noise as noise 
from qiskit.circuit.library import ZGate
from qiskit.visualization import plot_histogram
import random

import numpy as np
import matplotlib.pyplot as plt


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


def ancilla(qc, hamming_matrix):
    qc.h([i for i in range(7,13)])
     
    for row in range(len(hamming_matrix)):
        for i, b in enumerate(hamming_matrix[row]):
            if b == 1:
                qc.cx(row+7, i)
    
    for row in range(len(hamming_matrix)):
        for i, b in enumerate(hamming_matrix[row]):
            if b == 1:
                qc.cz(row+10, i)
    
    qc.h([i for i in range(7,13)])
    qc.measure([7, 8, 9, 10, 11, 12], [0, 1, 2, 3, 4, 5])


if __name__ == "__main__":
    # Apparently we need 2 different circuits (because qiskit is goofy)
    qc_simplex = QuantumCircuit(13, 6) # 7 data qubits, 6 ancilla qubits
    qc_dual = QuantumCircuit(13, 6)
    hamming_code = gen_hamming_code()
    pair_steane_matrix = gen_steane_code(hamming_code)
    simplex_matrix = pair_steane_matrix[0] # |0_L>
    dual_matrix = pair_steane_matrix[1]    # |1_L>

    amp_simplex = prepare_state_amp(simplex_matrix)
    amp_dual = prepare_state_amp(dual_matrix)
    output_register = ClassicalRegister(0, "output")
    qc_simplex.initialize(amp_simplex, [i for i in range(0,len(simplex_matrix)-1)])
    qc_dual.initialize(amp_dual, [i for i in range(0, len(dual_matrix)-1)])

    ancilla(qc_simplex, hamming_code)

    qc_simplex_samples = qc_simplex.copy()
    qc_dual_samples = qc_dual.copy()

    result = simulate_measurements(qc_simplex_samples, 100000)
    plot_histogram(result.get_counts(), sort='asc')
    print(len(result.get_counts()))

    qc_simplex.draw('mpl')
    plt.show()