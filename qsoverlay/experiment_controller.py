'''
Experiment_controller: A controller to take one or more quantumsim circuits
and run them as black boxes, i.e. to create states, apply circuits, measure
states (single-shot or generate statistics), update circuit parameters (i.e.
for a VQE).
'''

from quantumsim.sparsedm import SparseDM


class Controller:
    def __init__(self, qubits, mbits, op_circuits, msmt_circuits):

        '''
        qubits: list of qubits in the experiment
        mbits: the set of bits to receive measurements
        op_circuits: dictionary of circuits to apply to a state
            to perform an operation.
        msmt_circuits: dictionary of circuits to measure a state.
        '''

        self.mbits = mbits
        self.qubits = qubits
        self.op_circuits = op_circuits
        self.msmt_circuits = msmt_circuits

        self.make_state()

    def make_state(self):

        self.state = SparseDM(self.qubits+self.mbits)

    def apply_op_list(self, op_list):

        for op_name in op_list:
            self.op_circuits[op_name].apply_to(self.state)

    
