'''
Experiment_controller: A controller to take one or more quantumsim circuits
and run them as black boxes, i.e. to create states, apply circuits, measure
states (single-shot or generate statistics), update circuit parameters (i.e.
for a VQE).
'''

from quantumsim.sparsedm import SparseDM
import numpy as np

sx = np.array([[0, 1], [1, 0]])
sy = np.array([[0, -1j], [1j, 0]])
sz = np.array([[1, 0], [0, -1]])
s0 = np.array([[1, 0], [0, 1]])
pauli_dic = {1: s0, 'X': sx, 'Y': sy, 'Z': sz}


class Controller:
    def __init__(self,
                 qubits,
                 mbits,
                 circuits,
                 adjust_gates):

        '''
        qubits: list of qubits in the experiment
        mbits: the set of bits to receive measurements
        op_circuits: dictionary of circuits to apply to a state
            to perform an operation.
        msmt_circuits: dictionary of circuits to measure a state.
        adjust_gates: a list of adjustable gates in a circuit
            that the user might pass parameters to when they run
            the circuit.
        '''

        if 'record' in circuits:
            raise ValueError('record is a protected keyword')

        self.mbits = mbits
        self.qubits = qubits
        if any([type(c) == int for c in circuits]):
            raise ValueError('Circuits must not use integers for labels')
        self.circuits = circuits
        self.adjust_gates = adjust_gates

        self.make_state()

    def make_state(self):

        self.state = SparseDM(self.qubits+self.mbits)

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
        if circuit[0] == 'record':
            output = []
            for mbit in circuit[1:]:
                output.append(self.state.classical[mbit])
            return output

        elif type(circuit) is list or type(circuit) is tuple:
            op_name = circuit[0]
            if type(op_name) == int:
                return self.apply_circuit(circuit[1])

            else:
                for gate, param in zip(
                        self.adjust_gates[op_name], circuit[1:]):

                    gate.adjust(param)
                self.circuits[op_name].apply_to(self.state,
                                                apply_all_pending=False)
                return None

        else:
            op_name = circuit
            self.circuits[op_name].apply_to(self.state,
                                            apply_all_pending=False)

            return None

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

            if num_repetitions is not None:
                bernoulli_rv = (result + 1)/2
                sample_std = np.sqrt(bernoulli_rv*(1-bernoulli_rv) /
                                     num_repetitions)
                noisy_result = np.random.normal(loc=bernoulli_rv,
                                                scale=sample_std) * 2 - 1
                if noisy_result < -1:
                    noisy_result = -1
                if noisy_result > 1:
                    noisy_result = 1
                results.append(noisy_result)
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
