'''
circuit_builder: an overlay for quantumsim to build circuits slightly easier.
Assumes a gate set for a system, and inserts new gates end-on, keeping track
of at what time the next gate can be executed.

Does not do any compilation; this should possibly be inserted later.
'''

import numpy as np
import quantumsim.circuit
import quantumsim.ptm


class Builder:

    def __init__(self,
                 qubit_dic,
                 gate_dic,
                 gate_set,
                 update_rules=[],
                 **kwargs):
        '''
        qubit_dic: list of the qubits in the system.
            Each qubit should have a set of parameters,
            which is called whenever required by the gates.
        gate_dic: a dictionary of allowed gates.
            Each 'allowed gate' consists of:
                - the function to be called
                - a set of 'qubit_args' that will be found in
                    the qubit dictionary and passed to the gate.
                - a 'time' - the length of the gate
            Note that 'Measure' should be in the gate_set
        gate_set: a dictionary of allowed gate instances.
            An allowed gate instance is a list of the gate
            along with the qubits it is performed between.
        update_rules: a set of rules for updating the system.
            (i.e. between experiments).

        kwargs: Can add t1 and t2 via the kwargs instead of
            passing them with the qubit_dic.
        '''
        self.qubit_dic = qubit_dic
        self.gate_dic = gate_dic
        self.gate_set = gate_set
        self.update_rules = update_rules

        self.make_circuit(**kwargs)

    def make_circuit(self, circuit_title='New Circuit', **kwargs):

        '''
        Make a new circuit within the builder.
        '''

        self.circuit = quantumsim.circuit.Circuit(circuit_title)

        # Update the circuit list
        self.circuit_list = []

        # Times stores the current time of every qubit (beginning at 0)
        self.times = {}

        # Make qubits
        for qubit, qubit_args in self.qubit_dic.items():

            if 'classical' in qubit_args.items() and\
                    qubit_args['classical'] is True:
                self.circuit.add_qubit(quantumsim.circuit.ClassicalBit(qubit))
                continue

            # Get t1 values if we can, otherwise assume infinite.
            if 't1' not in qubit_args.keys():
                if 't1' in kwargs.keys():
                    qubit_args['t1'] = kwargs['t1']
                else:
                    qubit_args['t1'] = np.inf
            if 't2' not in qubit_args.keys():
                if 't2' in kwargs.keys():
                    qubit_args['t2'] = kwargs['t2']
                else:
                    qubit_args['t2'] = np.inf

            self.circuit.add_qubit(qubit, qubit_args['t1'], qubit_args['t2'])

            # Initialise the time of the latest gate on each qubit to 0
            self.times[qubit] = 0

    def add_qasm(self, qasm_generator):
        '''
        Converts a qasm file into a circuit.
        qasm_generator should yield lines of qasm when called.

        I assume that qasm lines take the form:
        GATE [arg0, arg1, ..] qubit0 [qubit1, ..]
        Importantly, currently only allowing for a single space
        in between words.
        '''
        for line in qasm_generator:

            # Get positions of spaces in line
            spaces = [line.find(' ', 0)]
            while spaces[-1] != -1:
                spaces.append(line.find(' ', spaces[-1]+1))
            spaces[-1] = len(line)

            # Get the gate name
            gate_name = line[:spaces[0]]

            num_qubits = self.gate_dic[gate_name]['num_qubits']
            user_kws = self.gate_dic[gate_name]['user_kws']

            if gate_name == 'measure':
                # line looks like 'measure q -> c;'
                qubit_list = [line[spaces[0]+1:spaces[1]]]
                output_bit = [line[spaces[2]+1:spaces[3]]]
                self.add_gate('Measure', qubit_list,
                              output_bit=output_bit)
                continue

            # Add arguments from qasm to kwargs
            kwargs = {}
            for n, kw in enumerate(user_kws):
                try:
                    kwargs[kw] = float(line[spaces[n]+1:spaces[n+1]])
                except:
                    kwargs[kw] = line[spaces[n]+1:spaces[n+1]]

            # Create qubit list
            qubit_list = [line[spaces[len(user_kws)+j]+1:
                          spaces[len(user_kws)+j+1]]
                          for j in range(num_qubits)]

            self.add_gate(gate_name, qubit_list, **kwargs)

    def add_circuit_list(self, circuit_list):

        '''
        Adds a circuit in the list format stored by qsoverlay
        to the builder.
        '''

        for gate_desc in circuit_list:
            self < gate_desc

    def __lt__(self, gate_desc):
        gate_name = gate_desc[0]

        num_qubits = self.gate_dic[gate_name]['num_qubits']
        user_kws = self.gate_dic[gate_name]['user_kws']

        assert len(gate_desc) == len(user_kws) + num_qubits + 1

        qubit_list = gate_desc[1:num_qubits + 1]

        kwargs = {kw: arg for kw, arg in
                  zip(user_kws, gate_desc[num_qubits+1:])}

        self.add_gate(gate_name, qubit_list, **kwargs)

    def add_gate(self, gate_name, qubit_list, return_flag=False, **kwargs):
        '''
        Adds a gate at the appropriate time to our system.
        The gate is always added in the middle of the time period
        in which it occurs.

        @ gate_name: name of the gate in the gate_set dictionary
        @ qubit_list: list of qubits that the gate acts on (in
            whatever order is appropriate)
        @ kwargs: whatever is additionally necessary for the gate.
            e.g. classical bit output names for a measurement,
                angles for a rotation gate.
            Note: times, or error parameters that can be obtained
                from a qubit will be ignored.
        '''

        # The gate tuple is a unique identifier for the gate, allowing
        # for asymmetry (as opposed to the name of the gate, which is
        # the same for every qubit/pair of qubits).
        gate_tuple = (gate_name, *qubit_list)

        circuit_args, builder_args = self.gate_set[gate_tuple]

        # kwargs is the list of arguments that gets passed to the gate
        # itself. We initiate with the set of additional arguments passed
        # by the user and the arguments from the gate dic intended for
        # quantumsim.
        kwargs = {**circuit_args, **kwargs}

        # Find the length of the gate
        gate_time = builder_args['gate_time']

        # Calculate when to apply the gate
        time = max(self.times[qubit] for qubit in qubit_list)
        try:
            kwargs['time'] = time + builder_args['exec_time']

        except:
            # If we have no exec time, assume the gate occurs in the
            # middle of the time window allocated.
            kwargs['time'] = time + gate_time/2

        # Add qubits to the kwargs as appropriate.
        # Note that we do *not* add classical bits here.
        if len(qubit_list) == 1:
            kwargs['bit'] = qubit_list[0]
        else:
            for j, qubit in enumerate(qubit_list):
                kwargs['bit'+str(j)] = qubit

        # Store a representation of the circuit for ease of access.
        # Note that this representation does not account for any
        # standard parameters (i.e. those changed in the gate_set)
        # that are changed by the user.

        # This also ensures that the user has entered all necessary
        # data.
        user_data = [kwargs[kw]
                     for kw in self.gate_dic[gate_name]['user_kws']]
        self.circuit_list.append((gate_name, *qubit_list, *user_data))

        # Get the gate to add to quantumsim.
        gate = self.gate_dic[gate_name]['function']

        if isinstance(gate, str):
            self.circuit.add_gate(gate, **kwargs)

        elif isinstance(gate, type) and\
                issubclass(gate, quantumsim.circuit.Gate):
            self.circuit.add_gate(gate(**kwargs))

        else:
            gate(builder=self, **kwargs)

        # Update time on qubits after gate is created
        for qubit in qubit_list:
            self.times[qubit] = max(self.times[qubit], time + gate_time)

        # My current best idea for adjustable gates - return the
        # gate that could be adjusted to the user.
        if return_flag is not False:
            return [self.circuit.gates[-int(return_flag)]]

    def update(self, **kwargs):
        for rule in self.update_rules:
            rule(self, **kwargs)

    def finalize(self, topo_order=False, t_add=0):
        '''
        Adds resting gates to all systems as required.
        quantumsim currently assumes fixed values for photon
        numbers, so we take them from a random qubit

        Photons in quantumsim are currently broken, so
        they're not in here right now.
        '''

        circuit_time = max(self.times.values()) + t_add

        # args = list(self.qubit_dic.values())[0]

        # if 'photons' in args.keys() and args['photons'] is True:
        #     quantumsim.photons.add_waiting_gates_photons(
        #         self.circuit,
        #         tmin=0, tmax=circuit_time,
        #         alpha0=args['alpha0'], kappa=args['kappa'],
        #         chi=args['chi'])
        # else:

        self.circuit.add_waiting_gates(tmin=0, tmax=circuit_time)
        if topo_order is True:
            self.circuit.order()
        else:
            self.circuit.gates = sorted(self.circuit.gates,
                                        key=lambda x: x.time)
