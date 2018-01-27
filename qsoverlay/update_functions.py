'''
Update functions: functions to update a quantumsim circuit
(for instance, between experiments to account for fluctuating noise).
'''
from quantumsim import ptm
import numpy as np


def update_quasistatic_flux(builder, **kwargs):

    '''
    Puts new quasistatic flux for 2 qubit gates
    '''

    qubit_dic = builder.qubit_dic
    circuit = builder.circuit

    for qubit in qubit_dic:
        if qubit['static_flux_std'] is not None:

            qubit['quasistatic_flux'] =\
                qubit['static_flux_std'] * np.random.randn()

    for gate in circuit.gates:
        try:
            if gate.quasistatic_flux_flag is True:
                qubit = qubit_dic[gate.involved_qubits[0]]
                new_ptm = ptm.rotate_z_ptm(qubit['quasistatic_flux'])
                gate.ptm = new_ptm
        except:
            pass
