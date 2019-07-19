from .gate_templates import make_gate
from .setup_functions import make_1q2q_gateset
from .experiment_setup import Setup
from quantumsim.models import depolarizing as gts
from quantumsim.models import noiseless as gts_nl
from quantumsim.circuit import (uniform_noisy_sampler, uniform_sampler)
import numpy as np

circuit_args = {'depol_noise': 'depol_noise'}

RotateX = make_gate(gts.RotateX, 1, 'dummy_time',
                    circuit_args=circuit_args, user_kws=['angle'],
                    name='RotateX')

RotateY = make_gate(gts.RotateY, 1, 'dummy_time',
                    circuit_args=circuit_args, user_kws=['angle'],
                    name='RotateY')

RotateZ = make_gate(gts.RotateZ, 1, 'dummy_time',
                    circuit_args=circuit_args, user_kws=['angle'],
                    name='RotateY')

CZ = make_gate(gts.CPhase, 2, 'dummy_time',
               circuit_args=circuit_args,
               name='CZ')

CNOT = make_gate(gts.CNOT, 2, 'dummy_time',
                 circuit_args=circuit_args,
                 name='CNOT')

ISwap = make_gate(gts.ISwap, 2, 'dummy_time',
                  circuit_args=circuit_args,
                  name='ISwap')

Hadamard = make_gate(gts.Hadamard, 1, 'dummy_time',
                     circuit_args=circuit_args,
                     name='H')

Measure = make_gate(gts_nl.Measurement, 1, 'dummy_time',
                    circuit_args={'sampler': 'sampler'},
                    name='Measure')

XGate = make_gate(gts.XGate, 1, 'dummy_time',
                  circuit_args=circuit_args,
                  name='X')

YGate = make_gate(gts.YGate, 1, 'dummy_time',
                  circuit_args=circuit_args,
                  name='Y')

ZGate = make_gate(gts.ZGate, 1, 'dummy_time',
                  circuit_args=circuit_args,
                  name='Z')


def quick_setup(qubit_list, depol_noise, readout_error=0, rng=None):

    gate_dic = {
        'CZ': CZ,
        'CNOT': CNOT,
        'RotateX': RotateX,
        'RX': RotateX,
        'Rx': RotateX,
        'RotateY': RotateY,
        'RY': RotateY,
        'Ry': RotateY,
        'RotateZ': RotateZ,
        'RZ': RotateZ,
        'Rz': RotateZ,
        'Measure': Measure,
        'ISwap': ISwap,
        'Had': Hadamard,
        'H': Hadamard,
        'X': XGate,
        'Y': YGate,
        'Z': ZGate
    }
    if readout_error > 0:
        sampler = uniform_noisy_sampler(state=rng, readout_error=readout_error)
    else:
        sampler = uniform_sampler(state=rng)

    qubit_dic = {q: {'t1': np.inf, 't2': np.inf,
                     'depol_noise': depol_noise,
                     'sampler': sampler,
                     'dummy_time': 1}
                 for q in qubit_list}
    gate_set = make_1q2q_gateset(qubit_dic=qubit_dic,
                                 gate_dic=gate_dic)

    return Setup(gate_dic=gate_dic,
                 qubit_dic=qubit_dic,
                 gate_set=gate_set)
