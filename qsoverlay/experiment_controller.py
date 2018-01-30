'''
Experiment_controller: A controller to take one or more quantumsim circuits
and run them as black boxes, i.e. to create states, apply circuits, measure
states (single-shot or generate statistics), update circuit parameters (i.e.
for a VQE).
'''

from quantumsim.sparsedm import SparseDM


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

        if 'record' is in circuits:
            raise ValueError('record is a protected keyword')

        self.mbits = mbits
        self.qubits = qubits
        self.circuits = circuits
        self.adjust_gates = adjust_gates

        self.make_state()

    def make_state(self):

        self.state = SparseDM(self.qubits+self.mbits)

    def apply_op_list(self, circuit_list):
        '''
        Apply a set of operations to a state.

        circuit_list: a list of circuits to apply.
        Each entry is either:
        a) a string corresponding to an entry in self.circuits
        b) a tuple or list with the first entry a string corresponding
            to an entry in self.circuits and the remaining entries
            angles to input for self.adjust_gates.
        c) a tuple or list with the first entry the reserved keyword
            'measure', and the remaining entries a list of mbits to
            store the current value of.
        '''
        output_list = []
        for c in circuit_list:

            # Record is a reserved keyword to copy the output
            # from a set of classical bits to return to the user.
            if c[0] is 'record':
                output = []
                for mbit in c[1:]:
                    output.append(self.state.classical[mbit])
                output_list.append(output)
                continue

            if type(c) is list or type(c) is tuple:
                op_name = c[0]
                for gate, param in zip(
                        self.adjust_gates[op_name], c[1:]):
                    gate.adjust(param)
            else:
                op_name = c
            self.circuits[op_name].apply_to(self.state,
                                            apply_all_pending=False)

    def measure(self, msmts, num_repetitions=None):
        '''
        Measures a set of Pauli strings on the current state.
        If num_repetitions is None this is performed perfectly.
        Otherwise, we treat the calculated value as a bernoulli
        random variable we are attempting to approximate, and
        sample an answer.
        '''

        return NotImplemented
