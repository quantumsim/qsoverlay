'''
Experiment_controller: A controller to take one or more quantumsim circuits
and run them as black boxes, i.e. to create states, apply circuits, measure
states (single-shot or generate statistics), update circuit parameters (i.e.
for a VQE).
'''

from quantumsim.sparsedm import SparseDM
from quantumsim.circuit import Measurement
import numpy as np
from .circuit_builder import Builder
from .experiment_setup import Setup
import json
import warnings

sx = np.array([[0, 1], [1, 0]])
sy = np.array([[0, -1j], [1j, 0]])
sz = np.array([[1, 0], [0, -1]])
s0 = np.array([[1, 0], [0, 1]])
pauli_dic = {1: s0, 'X': sx, 'Y': sy, 'Z': sz}


class Controller:
    def __init__(self,
                 filename=None,
                 setup=None,
                 random_state=None,
                 qubits=[],
                 circuits={},
                 circuit_lists={},
                 adjust_gates={},
                 measurement_gates={},
                 angle_convert_matrices={},
                 mbits=[]):

        '''
        qubits: list of qubits in the experiment
        mbits: the set of bits to receive measurements
        circuits: dictionary of circuits to apply to a state
            to perform an operation.
        circuit_lists: corresponding circuit lists (as output by qsoverlay
            builder for saving purposes)
        msmt_circuits: dictionary of circuits to measure a state.
        adjust_gates: a list of adjustable gates in a circuit
            that the user might pass parameters to when they run
            the circuit.
        measurement_gates: a set of Measurement type operators
            to extract extra details about the measurements made.
        '''

        if 'record' in circuits:
            raise ValueError('record is a protected keyword')

        self.mbits = mbits
        self.qubits = qubits
        if any([type(c) == int for c in circuits]):
            raise ValueError('Circuits must not use integers for labels')
        self.circuits = circuits
        self.circuit_lists = circuit_lists
        self.adjust_gates = adjust_gates
        self.angle_convert_matrices = angle_convert_matrices
        self.measurement_gates = measurement_gates

        if random_state is None:
            warnings.warn('No random state given, using system clock')
            random_state = np.random.RandomState()
        self.random_state = random_state

        if filename is not None:

            self.load(filename, setup)

        self.make_state()

    def load(self, filename, setup):

        with open(filename, 'r') as infile:
            data = json.load(infile)

        if type(setup) == str:
            setup = Setup(filename=setup)

        self.mbits = data['mbits']
        self.qubits = data['qubits']
        self.angle_convert_matrices = {
            key: np.array(val)
            for key, val in data['angle_convert_matrices'].items()
        }

        b = Builder(setup)
        for name, cl in data['circuit_lists'].items():
            b.new_circuit()
            adjust_gates = b.add_circuit_list(cl)
            b.finalize()
            self.circuits[name] = b.circuit
            self.circuit_lists[name] = cl
            self.adjust_gates[name] = [
                ag for ag in adjust_gates
                if type(ag) is not Measurement]
            self.measurement_gates[name] = [
                ag for ag in adjust_gates
                if type(ag) is Measurement]
            if name in data['angle_convert_matrices']:
                self.angle_convert_matrices =\
                    data['angle_convert_matrices'][name]

    def save(self, filename):
        data = {
            'mbits': self.mbits,
            'qubits': self.qubits,
            'circuit_lists': self.circuit_lists,
            'angle_convert_matrices': {
                key: val.tolist()
                for key, val in self.angle_convert_matrices.items()}
        }

        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    def make_state(self, dense_qubits=[]):

        self.state = SparseDM(self.qubits+self.mbits)
        for qubit in dense_qubits:
            self.state.ensure_dense(qubit)

    def apply_circuit(self, circuit):

        '''
        Applies a circuit to the state.

        Each entry is either:
        a) a string corresponding to an entry in self.circuits
        b) a tuple or list with the first entry a string corresponding
            to an entry in self.circuits and the remaining entries
            angles to input for self.adjust_gates.
        c) a tuple or list with the first entry the reserved keyword
            'record', and the remaining entries a list of mbits to
            store the current value of.
        d) a pair (n, circuit), where circuit is one of the above,
            and n is the number of times to repeat the circuit.
        '''

        # Record is a reserved keyword to copy the output
        # from a set of classical bits to return to the user.

        if type(circuit) is list or type(circuit) is tuple:

            if circuit[0] == 'record':
                output = []
                for mbit in circuit[1:]:
                    output.append(self.state.classical[mbit])
                return output

            op_name = circuit[0]
            if type(op_name) == int:
                return_data = []
                for _ in range(op_name):
                    return_data.append(self.apply_circuit(circuit[1]))
                return return_data

            else:
                if op_name in self.angle_convert_matrices:
                    angles = self.angle_convert_matrices[op_name] @ circuit[1:]
                else:
                    angles = circuit[1:]
                for gate, param in zip(
                        self.adjust_gates[op_name], angles):
                    gate.adjust(param)
                self.circuits[op_name].apply_to(self.state,
                                                apply_all_pending=False)

        else:
            op_name = circuit
            self.circuits[op_name].apply_to(self.state,
                                            apply_all_pending=False)

        if op_name in self.measurement_gates:
            return_data = [{
                'probabilities': m.probabilities[-1],
                'projects': m.projects[-1],
                'measurements': m.measurements[-1]}
                for m in self.measurement_gates[op_name]]
            return return_data

        return None

    def __lt__(self, circuit):
        self.apply_circuit(circuit)

    def apply_circuit_list(self, circuit_list):
        '''
        Apply a set of operations to a state.

        circuit_list: a list of circuits to apply.
        '''
        output_list = []
        for circuit in circuit_list:

            # Record is a reserved keyword to copy the output
            # from a set of classical bits to return to the user.
            output = self.apply_circuit(circuit)
            if output is not None:
                output_list.append(output)

        return output_list

    def simulate_tomo(self, circuit,
                      tomo_circuits,
                      measurement_model,
                      num_measurements,
                      output_format, data_type):
        '''
        Takes the current system state, copies it,
        applies multiple tomography circuits, and runs them through
        models for the measurement to return thresholded voltages.
        '''
        data = []
        for tomo_circuit in tomo_circuits:
            self.make_state()
            self < circuit
            self < tomo_circuit
            self.state.renormalize()
            rho_dist = self.state.peak_multiple_measurements(
                measurement_model.qubits)
            data.append(measurement_model.sample(rho_dist,
                        num_measurements, data_type=data_type, output_format=output_format))
        return data

    def get_expectation_values(self, msmts, num_repetitions=None):
        '''
        Measures a set of Pauli strings on the current state.
        If num_repetitions is None this is performed perfectly.
        Otherwise, we treat the calculated value as a bernoulli
        random variable we are attempting to approximate, and
        sample an answer.

        input: msmts: list of measurement dictionaries, containing
        'X', 'Y', or 'Z' for each non-trivial qubit label.
        '''

        results = []
        self.state.apply_all_pending()
        self.state.renormalize()
        dm = self.state.full_dm.to_array()

        for msmt in msmts:

            mult = 1

            # Make Pauli list
            pauli_list = [1] * len(self.state.idx_in_full_dm)
            for qubit in msmt:
                if qubit not in self.state.idx_in_full_dm:
                    if msmt[qubit] == 'Z':
                        mult *= (-1)**self.state.classical[qubit]
                    elif msmt[qubit] in ['X', 'Y']:
                        mult = 0
                    else:
                        raise ValueError('qubit measurements must be X, Y, Z')
                else:
                    pauli_list[self.state.idx_in_full_dm[qubit]] = msmt[qubit]

            # Make measurement operator
            op = pauli_dic[pauli_list[0]]
            for label in pauli_list[1:]:
                op = np.kron(pauli_dic[label], op)

            result = mult * np.trace(op @ dm)

            assert np.imag(result) < 1e-9
            result = float(np.real(result))

            if num_repetitions is not None:
                bernoulli_rv = (1 - result)/2
                if bernoulli_rv <= 0 and bernoulli_rv > -1e-6:
                    noisy_result = 0
                elif bernoulli_rv >= 1 and bernoulli_rv <= 1+1e-6:
                    noisy_result = 1
                else:
                    try:
                        noisy_result = np.random.beta(bernoulli_rv *
                                                      num_repetitions,
                                                      (1-bernoulli_rv) *
                                                      num_repetitions)
                    except:
                        raise ValueError('My bernoulli random variable is weird: {}'.format(bernoulli_rv))

                results.append(1-2*noisy_result)
            else:
                results.append(result)

        return np.array(results)

    def get_prob_all_zero(self, qubits):

        '''
        Returns the probability that all qubits in qubits
        will return a 0 measurement (regardless of any other qubit
        measurement).
        '''

        self.state.apply_all_pending()
        self.state.renormalize()

        indices = [self.state.idx_in_full_dm[q] for q in qubits]
        diagonal = self.state.full_dm.get_diag()

        return sum([x for j, x in enumerate(diagonal) if
                    all([(j//2**i) % 2 == 0 for i in indices])])
