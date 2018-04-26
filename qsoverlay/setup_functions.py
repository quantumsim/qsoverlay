'''
setup_functions: functions to assist in creating a setup file
for a qsoverlay circuit builder.
'''

'''
Gate-set creation:

A gate_set is a dictionary of allowed gates for a circuit,
containing the parameters for each gate.

Gates are stored as tuples:
    (name,q0,q1,...), where 'name' corresponds to
    a label in gate_dic, and q0, q1 corresponds to
    the involved qubits.

The parameters themselves are contained within a dictionary
that can be pulled out, combined with any kwargs sent to the
user, and pushed to quantumsim.

The following functions provide some assistance in gate-set
creation.
'''

def fill_gateset(qubit_dic, gate_dic, gate_set):
    '''
    A function to fill a pre-existing gate set
    with gate/qubit parameters (so that one may
    say, define a restricted set of 2-qubit gates
    and then fill them up with data).

    This assumes some symmetry between qubits:
    namely, every 2 (or higher)-qubit gate will
    take on any qubit parameters from the first qubit
    in its list, and all gate parameters will be the
    same. This can be adjusted before or after within
    the gate set (parameters that are preset in the
    gate set beforehand will not be overwritten here).
    '''

    for gate_instance, [circuit_args, builder_args] in gate_set.items():

        # Get the gate and the first qubit
        gate = gate_instance[0]
        q0 = gate_instance[1]

        # Find the parameters to add to the gate set
        qbargs = {kw: (qubit_dic[q0][kw_orig]
                       if type(kw_orig) == str else kw_orig)
                  for kw, kw_orig in gate_dic[gate]['builder_args'].items()}
        qcargs = {kw: (qubit_dic[q0][kw_orig]
                       if type(kw_orig) == str else kw_orig)
                  for kw, kw_orig in gate_dic[gate]['circuit_args'].items()}

        # Update the gate set with the parameters.
        # Reverse order saves any parameters already
        # in the gate set from being overwritten.
        gate_set[gate_instance] = [{
            **qcargs, **circuit_args}, {
            **qbargs, **builder_args}]

    return gate_set


def make_1q2q_gateset(qubit_dic, gate_dic, connectivity_dic=None):

    '''
    A function to make a full set of 1 and 2 qubit
    gates given a qubit_dic and a gate_dic.

    This then assumes that a) the system is symmetric,
    and b) the system has full connectivity.
    '''

    # Make gate set
    gate_set = {}

    for qubit, qparams in qubit_dic.items():

        # Classical bits don't get quantum gates.
        if 'classical' in qparams.keys() \
                and qparams['classical'] is True:
            continue

        for gate, gparams in gate_dic.items():

            qcargs = {kw: (qparams[kw_orig] if type(kw_orig) == str
                           else kw_orig)
                      for kw, kw_orig in gparams['circuit_args'].items()}
            qbargs = {kw: (qparams[kw_orig] if type(kw_orig) == str
                           else kw_orig)
                      for kw, kw_orig in gparams['builder_args'].items()}

            if gparams['num_qubits'] == 1:

                # insert everything - no need to copy
                gate_set[(gate, qubit)] = [qcargs, qbargs]

            elif gparams['num_qubits'] == 2:

                for q2, q2params in qubit_dic.items():

                    # Classical bits don't get quantum gates,
                    # and 2 qubit gates don't go back to the same
                    # qubit.
                    if q2 == qubit \
                            or 'classical' in q2params \
                            and q2params['classical'] is True:
                        continue
                    if connectivity_dic and (
                            qubit not in connectivity_dic[q2] and
                            q2 not in connectivity_dic[qubit]):
                        continue

                    # Insert everything - copy as these dictionaries
                    # are used multiple times.
                    gate_set[(gate, qubit, q2)] = [{**qcargs}, {**qbargs}]
            else:
                raise ValueError('Sorry, I can only do 1' +
                                 ' and 2 qubit gates')

    return gate_set
