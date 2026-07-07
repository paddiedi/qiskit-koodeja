from qiskit import transpile, QuantumCircuit
from qiskit_aer import AerSimulator


import matplotlib.pyplot as plt
import random
import numpy as np

ANCILLA_START = 7
HAMMING_D = [7,3]

# This is an implementation of the 7,1,3 Steane code, in the stabilizer formalism.
# Could use enums for these classes?
class Generator():
    def __init__(self):
        pass

class Generator_x(Generator):
    def __init__(self,ancilla_index, check_index):
        self.ancilla_index = ancilla_index
        self.check_index = check_index
        self.eigen_value = 0 # 0 undetermined error or not

class Generator_z(Generator):
    def __init__(self,ancilla_index, check_index):
        self.ancilla_index = ancilla_index
        self.check_index = check_index
        self.eigen_value = 0

def trim_results(results):
    trimmed_dict = {}
    for key, value in results.items():
        # Qiskit for some reason reverses the qubit order.
        trimmed_dict[f"{key[6:]}"[::-1]] = value

    return trimmed_dict

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
    ones = [1 for i in range(HAMMING_D[0])]
    # The most cursed shi I have ever seen
    for d1 in (0,1):
        for d2 in (0,1):
            for d3 in (0,1):
                # Group theory stuff, check out cosets n stuff
                simplex_values.append(d1*matrix[0] ^ d2*matrix[1] ^ d3*matrix[2])

    simplex_values = np.array(simplex_values)      # 0_L qubits
    dual_values = simplex_values ^ ones # 1_L qubits
    return simplex_values, dual_values

def prepare_state_amp(steane_matrix):
    bit_string = ""
    n_string = len(steane_matrix[0])
    amps = np.zeros(2**n_string, dtype=complex) # The amplitude can be complex
    n_rows = len(steane_matrix)
    for column in steane_matrix:
        for char in column:
            bit_string += str(int(char))
        # The bitstring has to be reversed, apparently reading
        # order during the ancilla stuff is reversed... Thanks
        # QISKIT (though can be probably fixed with putting
        # the ancillas to the index 0 etc.)
        amps[int(bit_string[::-1],2)] = 1/np.sqrt(n_rows)
        bit_string = ""
    return amps

def create_generators(qc, ancilla_start, hamming_matrix, Classtype: Generator) -> list:
    gen_list = []
    GenClass = Classtype
    for row_index , row in enumerate(hamming_matrix):
        ancilla_index = ancilla_start + row_index
        gen = GenClass(ancilla_index, [])
        qc.h(ancilla_index)
        for i,b in enumerate(row):
            if b:
                if GenClass is Generator_x:
                    qc.cx(ancilla_index, i)
                elif GenClass is Generator_z:
                    qc.cz(ancilla_index, i)
                else:
                    raise TypeError
                gen.check_index.append(i)
        gen_list.append(gen)
        qc.h(ancilla_index)
    return gen_list

def check_error(qc_samples, generators, Classtype: Generator):
    # Need to copy the circuit I guess?
    qc_measured = qc_samples.copy()
    for gen in generators:
        qc_measured.measure(gen.ancilla_index, gen.ancilla_index)
    result = simulate_measurements(qc_measured, 1)
    outcome = next(iter(result.get_counts()))

    syndrome = tuple(int(outcome[len(outcome) - 1 - gen.ancilla_index]) for gen in generators)
    print(syndrome)

    if sum(syndrome) == 0:
        print("No error happened")
        return

    for gen in generators:
        gen.eigen_value = int(outcome[len(outcome) - 1 - gen.ancilla_index])
    # Craziest stuff I've ever seen (did not make this tho)
    for qubit_index in range(HAMMING_D[0]):
        qubit_syndrome = tuple(int(qubit_index in gen.check_index) for gen in generators)
        if qubit_syndrome == syndrome:
            print(f"Found error on {qubit_index}")
            if Classtype is Generator_x:
                qc_samples.z(qubit_index)
            elif Classtype is Generator_z:
                qc_samples.x(qubit_index)
            else:
                raise TypeError
            break

def noise(qc):
    error_type = random.randint(0,2)
    # X error
    if error_type == 0:
        error_loc = random.randint(0, qc.num_qubits-7)
        qc.x(error_loc)
        print(f'Error type: X on position {error_loc}')
    # Z error
    if error_type == 1:
        error_loc = random.randint(0, qc.num_qubits-7)
        qc.z(error_loc)
        print(f'Error type: Z on position {error_loc}')
    # Z and X errors
    if error_type == 2:
        error_loc_x = random.randint(0, qc.num_qubits-7)
        error_loc_z = random.randint(0, qc.num_qubits-7)
        qc.x(error_loc_x)
        qc.z(error_loc_z)
        print(f'Error type: X & Z on positions X: {error_loc_x} and Z: {error_loc_z}')

def post_processing(qc_samples, errors):
    pass
    # Insert post processing here
if __name__ == "__main__":
    # Apparently we need 2 different circuits (because qiskit is goofy)
    generators_simplex = {"X": [], "Z": []}
    generators_dual = {"X": [], "Z": []}
    qc_simplex = QuantumCircuit(13, 13) # 7 sized qubits + 6 ancillas, 3 for both X and Z
    qc_dual = QuantumCircuit(13, 13)
    hamming_code = gen_hamming_code()
    pair_steane_matrix = gen_steane_code(hamming_code)
    simplex_matrix = pair_steane_matrix[0] # |0_L>
    dual_matrix = pair_steane_matrix[1]    # |1_L>

    amp_simplex = prepare_state_amp(simplex_matrix)
    amp_dual = prepare_state_amp(dual_matrix)

    qc_simplex.initialize(amp_simplex, [i for i in range(0,len(simplex_matrix[0]))])
    qc_dual.initialize(amp_dual, [i for i in range(0, len(dual_matrix[0]))])
    #init_simplex = Statevector
    #qc_simplex.z(6)

    noise(qc_simplex)

    # X-generators
    generators_simplex["X"] = create_generators(qc_simplex, 7, hamming_code, Generator_x)
    generators_dual["X"] = create_generators(qc_dual, 7, hamming_code, Generator_x)
    # Z-generators
    generators_simplex["Z"] = create_generators(qc_simplex, 10, hamming_code, Generator_z)
    generators_dual["Z"] = create_generators(qc_dual, 10, hamming_code, Generator_z)
    # Sample circuits
    qc_simplex_samples = qc_simplex.copy()
    qc_dual_samples = qc_dual.copy()

    #print(generators_dual)
    # Steane code can fix only a single error, bit flip/phase flip
    # (or both at the same time, but not for instance 2 bit flips)
    # This is because of the amount of ancillas is 3
    # Check/Fix errors on both circuits
    check_error(qc_simplex_samples, generators_simplex["X"], Generator_x)
    check_error(qc_simplex_samples, generators_simplex["Z"], Generator_z)
    
    check_error(qc_dual_samples, generators_dual["X"], Generator_x)
    check_error(qc_dual_samples, generators_dual["Z"], Generator_z)

    qc_simplex_samples.measure(range(0, 7), range(0,7))
    qc_dual_samples.measure(range(0,7), range(0,7))
    
    circuit_fig = qc_simplex_samples.draw("mpl", fold=-1, reverse_bits=True)
    circuit_fig.set_size_inches(12, 4)
    result_simplex = simulate_measurements(qc_simplex_samples, 1000)
    result_dual = simulate_measurements(qc_dual_samples, 1000)
    # Trim out the 6 ancilla qubits from the result.
    print(trim_results(result_simplex.get_counts()))
    #plot_histogram(result_simplex.get_counts(), sort='asc')
    plt.show()
