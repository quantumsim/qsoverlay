"""
gate_templates: dictionaries of gate templates for use in a qsoverlay builder.

A gate template is a prototype gate (as opposed to a gate, which has a
well-defined set of qubits to act on). In qsoverlay, this is represented
by a dictionary, containing the following information:

'function': the object to call when creating the gate in the builder;
    either a quantumsim gate, or a gate creation function.
'num_qubits': number of qubits the gate acts upon.
'builder_args': the arguments needed by the builder to construct the
    gate. The value of the argument is stored in the gate_set object,
    which in turn either inherits this from the qubit object or has
    it defined by the user. We store the names of such inheritable
    parameters in the gate template (so that we can find them), and
    occasionally some gate parameters (e.g. for a composite gate
    the gate time should be set to 0).
"""

import quantumsim.circuit
from .gate_functions import (
    insert_CZ, insert_CPhase, insert_measurement,
    had_from_rot, CNOT_from_CZ, X_gate, Y_gate, Z_gate,
    CRX_from_CZ, insert_reset)


def make_gate(func, num_qubits, gate_time_label, **kwargs):
    """
    Helper function to make a legitimate
    gate for processing in a circuit builder.
    """

    gate_template = {
        'function': func,
        'num_qubits': num_qubits,
        'builder_args': {
            'gate_time': gate_time_label
        },
        'circuit_args': {},
        'user_kws': []
    }

    if 'circuit_args' in kwargs.keys():
        gate_template['circuit_args'] = kwargs['circuit_args']
    if 'builder_args' in kwargs.keys():
        gate_template['builder_args'] = {
            **gate_template['builder_args'],
            **kwargs['builder_args']
        }
    if 'user_kws' in kwargs.keys():
        gate_template['user_kws'] = kwargs['user_kws']

    return {**gate_template, **kwargs}


# A labeled list of all gates to be found below.
# As this eventually contains functions, I don't know
# of a better way than hard-coding
class GateData:

    def __init__(self):
        self.available_gate_dic = {
            'CZ': CZ,
            'CPhase': CPhase,
            'RotateX': RotateX,
            'RotateY': RotateY,
            'RotateZ': RotateZ,
            'RotateXY': RotateXY,
            'RotateEuler': RotateEuler,
            'XGate': XGate,
            'YGate': YGate,
            'ZGate': ZGate,
            'Measure': Measure,
            'ISwap': ISwap,
            'ISwapRotation': ISwapRotation,
            'ResetGate': ResetGate,
            'Had': Had,
            'CNOT': CNOT,
            'CRX': CRX
        }


# Pre-defined gate dictionaries for ease of reading.

CZ = {
    'name': 'CZ',
    'function': insert_CZ,
    'num_qubits': 2,
    'builder_args': {
        'gate_time': 'CZ_gate_time'
    },
    'circuit_args': {
        'quasistatic_flux': 'quasistatic_flux',
        'dephase_var': 'dephase_var'
    },
    'user_kws': []
}

CPhase = {
    'name': 'CPhase',
    'function': insert_CPhase,
    'num_qubits': 2,
    'builder_args': {
        'gate_time': 'CZ_gate_time'
    },
    'circuit_args': {
        'quasistatic_flux': 'quasistatic_flux',
        'dephase_var': 'dephase_var'
    },
    'user_kws': ['angle']
}

RotateEuler = {
    'name': 'RotateEuler',
    'function': quantumsim.circuit.RotateEuler,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 'oneq_gate_time'
    },
    'circuit_args': {},
    'user_kws': ['phi', 'theta', 'lamda']
}

RotateX = {
    'name': 'RotateX',
    'function': quantumsim.circuit.RotateX,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 'oneq_gate_time'
    },
    'circuit_args': {
        'dephasing_axis': 'dephasing_axis',
        'dephasing_angle': 'dephasing_angle'
    },
    'user_kws': ['angle']
}

RotateY = {
    'name': 'RotateY',
    'function': quantumsim.circuit.RotateY,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 'oneq_gate_time'
    },
    'circuit_args': {
        'dephasing_axis': 'dephasing_axis',
        'dephasing_angle': 'dephasing_angle'
    },
    'user_kws': ['angle']
}

RotateXY = {
    'name': 'RotateXY',
    'function': quantumsim.circuit.RotateXY,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 'oneq_gate_time'
    },
    'circuit_args': {
        'dephasing_axis': 'dephasing_axis',
        'dephasing_angle': 'dephasing_angle'
    },
    'user_kws': ['phi', 'theta']
}

RotateZ = {
    'name': 'RotateZ',
    'function': quantumsim.circuit.RotateZ,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 'oneq_gate_time'
    },
    'circuit_args': {
        'dephasing': 'dephasing'
    },
    'user_kws': ['angle']
}

XGate = {
    'name': 'XGate',
    'function': X_gate,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 0  # Composite gate
    },
    'circuit_args': {
    },
    'user_kws': []
}

YGate = {
    'name': 'YGate',
    'function': Y_gate,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 0  # Composite gate
    },
    'circuit_args': {
    },
    'user_kws': []
}

ZGate = {
    'name': 'ZGate',
    'function': Z_gate,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 0  # Composite gate
    },
    'circuit_args': {
    },
    'user_kws': []
}

Measure = {
    'name': 'Measure',
    'function': insert_measurement,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 'msmt_time',
        'exec_time': 0
    },
    'circuit_args': {
        'p_exc_init': 'p_exc_init',  # initial excitation prob
        'p_dec_init': 'p_dec_init',  # initial decay prob (indep of T1)
        'p_exc_fin': 'p_exc_fin',  # final excitation prob
        'p_dec_fin': 'p_dec_fin',  # final decay prob (indep of T1)
        'interval_time': 'interval_time',
        'msmt_time': 'msmt_time',
        'sampler': 'sampler'
    },
    'user_kws': ['output_bit']
}

ISwap = {
    'name': 'ISwap',
    'function': quantumsim.circuit.ISwap,
    'num_qubits': 2,
    'builder_args': {
        'gate_time': 'ISwap_gate_time'
    },
    'circuit_args': {
        'dephase_var': 'dephase_var'
    },
    'user_kws': []
}

ISwapRotation = {
    'name': 'ISwapRotation',
    'function': quantumsim.circuit.ISwapRotation,
    'num_qubits': 2,
    'builder_args': {
        'gate_time': 'ISwap_gate_time'
    },
    'circuit_args': {
        'dephase_var': 'dephase_var'
    },
    'user_kws': ['angle']
}

ResetGate = {
    'name': 'ResetGate',
    'function': insert_reset,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 'reset_time',
    },
    'circuit_args': {
        'population': 'residual_excitations',
        'reset_time': 'reset_time'
    },
    'qubit_circuit_kws': [],
    'user_kws': []
}

PrepGate = {
    'name': 'ResetGate',
    'function': quantumsim.circuit.ResetGate,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 0,
    },
    'circuit_args': {
        'population': 'residual_excitations'
    },
    'qubit_circuit_kws': [],
    'user_kws': []
}

Had = {
    'name': 'Had',
    'function': had_from_rot,
    'num_qubits': 1,
    'builder_args': {
        'gate_time': 0,  # Composite gate
    },
    'circuit_args': {},
    'qubit_circuit_kws': [],
    'user_kws': []
}

CNOT = {
    'name': 'CNOT',
    'function': CNOT_from_CZ,
    'num_qubits': 2,
    'builder_args': {
        'gate_time': 0,  # Composite gate
    },
    'circuit_args': {},
    'qubit_circuit_kws': [],
    'user_kws': []
}

CRX = {
    'name': 'CRX',
    'function': CRX_from_CZ,
    'num_qubits': 2,
    'builder_args': {
        'gate_time': 0,  # Composite gate
    },
    'circuit_args': {},
    'qubit_circuit_kws': [],
    'user_kws': ['angle']
}
