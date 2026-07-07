from qiskit import transpile, QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
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

def prepare_state_amp_FIXED(steane_matrix):
    n_string = len(steane_matrix[0])
    amps = np.zeros(2**n_string, dtype=complex)
    n_rows = len(steane_matrix)
    for column in steane_matrix:
        # REVERSE so qubit 0 is the LSB, matching Qiskit's little-endian convention
        bit_string = "".join(str(int(b)) for b in reversed(column))
        amps[int(bit_string,2)] = 1/np.sqrt(n_rows)
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


def noise(qc):
    coinflip = random.randint(0,1)
    # X error
    if coinflip == 0:
        error_loc = random.randint(0, qc.num_qubits-7)
        qc.x(error_loc)
        print('X', error_loc+1)
    # Z error
    if coinflip == 1:
        error_loc = random.randint(0, qc.num_qubits-7)
        qc.z(error_loc)
        print('Z', error_loc+1)


def get_key(dictionary):
    for key in dictionary:
        return key


def error_correction(qc, result_counts):
    measurement = ''.join(reversed(get_key(result_counts)))
    loc = {
    'X': 0,
    'Z': 0
    }
    loc['X'] += int(measurement[3:], 2)
    loc['Z'] += int(measurement[:3], 2)

    if loc['X'] != 0:
        qc.x(loc['X']-1)
    
    elif loc['Z'] != 0:
        qc.z(loc['Z']-1)
            


if __name__ == "__main__":
    # Apparently we need 2 different circuits (because qiskit is goofy)
    qc_simplex = QuantumCircuit(13, 6) # 7 data qubits, 6 ancilla qubits
    qc_dual = QuantumCircuit(13, 6)
    hamming_code = gen_hamming_code()
    pair_steane_matrix = gen_steane_code(hamming_code)
    simplex_matrix = pair_steane_matrix[0] # |0_L>
    dual_matrix = pair_steane_matrix[1]    # |1_L>

    amp_simplex = prepare_state_amp_FIXED(simplex_matrix)
    amp_dual = prepare_state_amp(dual_matrix)
    output_register = ClassicalRegister(0, "output")
    qc_simplex.initialize(amp_simplex, [i for i in range(0,len(simplex_matrix)-1)])
    qc_dual.initialize(amp_dual, [i for i in range(0, len(dual_matrix)-1)])

    noise(qc_simplex)

    ancilla(qc_simplex, hamming_code)

    qc_simplex_samples = qc_simplex.copy()
    qc_dual_samples = qc_dual.copy()

    result = simulate_measurements(qc_simplex_samples, 100000)
    plot_histogram(result.get_counts(), sort='asc')

    error_correction(qc_simplex, result.get_counts())

    qc_simplex.draw('mpl')
    plt.show()