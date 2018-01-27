'''
Gates: dictionaries of gates for use in a qsoverlay builder.
'''

import quantumsim.circuit
from .gate_functions import *


def make_gate(function, **kwargs):

    '''
    Helper function to make a legitimate
    gate for processing in a circuit builder.
    '''

    gate_template = {
        'function': function,
        'num_qubits': 1,
        'builder_args': {
            'gate_time': None
        },
        'circuit_args': {},
        'qubit_kws': [],
        'user_kws': []
    }

    return {**gate_template, **kwargs}

# Pre-defined gate dictionaries for ease of reading.

CZ = {
    'function': insert_CZ,
    'num_qubits': 2,
    'builder_args': {
        'gate_time': None
    },
    'circuit_args': {},
    'qubit_kws': ['quasistatic_flux',
                  'dephase_var'],
    'user_kws': []
}

CPhase = {
    'function': insert_CPhase,
    'num_qubits': 2,
    'builder_args': {
        'gate_time': None
    },
    'circuit_args': {},
    'qubit_kws': ['quasistatic_flux',
                  'dephase_var'],
    'user_kws': ['angle']
}

RotateX = {
    'function': quantumsim.circuit.RotateX,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': None
    },
    'circuit_args': {},
    'qubit_kws': ['dephasing_axis',
                  'dephasing_angle'],
    'user_kws': ['angle']
}

RotateY = {
    'function': quantumsim.circuit.RotateY,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': None
    },
    'circuit_args': {},
    'qubit_kws': ['dephasing_axis',
                  'dephasing_angle'],
    'user_kws': ['angle']
}

RotateZ = {
    'function': quantumsim.circuit.RotateZ,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': None
    },
    'circuit_args': {},
    'qubit_kws': ['dephasing'],
    'user_kws': ['angle']
}

Measure = {
    'function': insert_measurement,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': None,
        'exec_time': 0
    },
    'circuit_args': {
        'sampler': None
    },
    'qubit_kws': ['p_exc_init',  # initial excitation prob
                  'p_dec_init',  # initial decay prob (indep of T1)
                  'p_exc_fin',  # final excitation prob
                  'p_dec_fin',  # final decay prob (indep of T1)
                  'interval_time',
                  'msmt_time'],
    'user_kws': ['output_bit']
}

ISwap = {
    'function': quantumsim.circuit.ISwap,
    'num_qubits': 2,
    'builder_args': {
        'gate_time': None
    },
    'circuit_args': {},
    'qubit_kws': ['dephase_var'],
    'user_kws': ['angle']
}

ISwapRotation = {
    'function': quantumsim.circuit.ISwapRotation,
    'num_qubits': 2,
    'builder_args': {
        'gate_time': None
    },
    'circuit_args': {},
    'qubit_kws': ['dephase_var'],
    'user_kws': ['angle']
}

ResetGate = {
    'function': quantumsim.circuit.ResetGate,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': None,
        'exec_time': 0
    },
    'circuit_args': {},
    'qubit_kws': [],
    'user_kws': []
}

Had = {
    'function': had_from_rot,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 0,
        'exec_time': 0
    },
    'circuit_args': {},
    'qubit_kws': [],
    'user_kws': []
}

CNOT = {
    'function': CNOT_from_CZ,
    'num_qubits': 2,
    'builder_args': {
        'gate_time': 0,
        'exec_time': 0
    },
    'circuit_args': {},
    'qubit_kws': [],
    'user_kws': []
}
