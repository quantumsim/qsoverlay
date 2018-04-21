'''
DiCarlo_setup: functions to return the parameters for noise and experimental
design of DiCarlo qubits, in a format compatable with a circuit builder.
'''

import numpy as np
from numpy import pi
from quantumsim.circuit import uniform_noisy_sampler, uniform_sampler
from .setup_functions import make_1q2q_gateset
from .gate_templates import CZ, CPhase, RotateX, RotateY, RotateZ, Measure,\
                   ISwap, ISwapRotation, ResetGate, Had, CNOT, XGate, YGate, ZGate, CRX
from .update_functions import update_quasistatic_flux
from .experiment_setup import Setup


def quick_setup(qubit_list,
                **kwargs):
    '''
    Quick setup: a function to return a setup that may be immediately
    used to make a qsoverlay builder.
    '''

    setup = {
        'gate_dic': get_gate_dic(),
        'update_rules': get_update_rules(**kwargs),
        'qubit_dic': {
            q: get_qubit(**kwargs) for q in qubit_list
        }
    }

    setup['gate_set'] = make_1q2q_gateset(qubit_dic=setup['qubit_dic'],
                                          gate_dic=setup['gate_dic'])
    return Setup(**setup)


def get_gate_dic():
    '''
    Returns the set of gates allowed on DiCarlo qubits.
    Measurement time is something that's still being optimized,
    so this might change.
    (msmt_time = the total time taken for measurement + depletion)
    '''

    # Initialise gate set with all allowed gates
    gate_dic = {
        'CZ': CZ,
        'C-Phase': CPhase,
        'CPhase': CPhase,
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
        'ISwapRotation': ISwapRotation,
        'ResetGate': ResetGate,
        'Reset': ResetGate,
        'Had': Had,
        'H': Had,
        'CNOT': CNOT,
        'CRX': CRX,
        'X': XGate,
        'Y': YGate,
        'Z': ZGate
    }

    return gate_dic


def get_qubit(noise_flag=True,
              scale=1,
              t1=30000,
              t2=30000,
              dephasing_axis=1e-4,
              dephasing_angle=5e-4,
              dephasing=5e-4,
              p_exc_init=0.0,
              p_dec_init=0.005,
              p_exc_fin=0.0,
              p_dec_fin=0.015,
              photons=False,
              alpha0=4,
              kappa=1 / 250,
              chi=1.3 * 1e-3,
              static_flux_std=None,
              high_frequency=False,
              dephase_var=1e-2/(2*pi),
              msmt_time=600,
              interval_time=150,
              oneq_gate_time=20,
              CZ_gate_time=40,
              reset_time=500,
              sampler=None,
              seed=None,
              readout_error=0.005,
              **kwargs):
    '''
    The dictionary for parameters of the DiCarlo qubits, with standard
    parameters pre-set.

    This is a bit messy right now, but has the advantage of telling
    the user which parameters they can set. Not sure how to improve
    over this.
    '''
    if sampler is None:
        if noise_flag is True:
            sampler = uniform_noisy_sampler(seed=seed,
                                            readout_error=readout_error)
        else:
            sampler = uniform_sampler(seed=seed)

    if static_flux_std is not None:
        quasistatic_flux = static_flux_std * np.random.randn()
    else:
        quasistatic_flux = None

    if noise_flag is True:

        param_dic = {
            't1': t1/scale,
            't2': t2/scale,
            'dephasing_axis': dephasing_axis*scale,
            'dephasing': dephasing*scale,
            'dephasing_angle': dephasing_angle*scale,
            'dephase_var': dephase_var*scale,
            'p_exc_init': p_exc_init*scale,
            'p_dec_init': p_dec_init*scale,
            'p_exc_fin': p_exc_fin*scale,
            'p_dec_fin': p_dec_fin*scale,
            'msmt_time': msmt_time,
            'interval_time': interval_time,
            'oneq_gate_time': oneq_gate_time,
            'CZ_gate_time': CZ_gate_time,
            'ISwap_gate_time': CZ_gate_time*np.sqrt(2),
            'reset_time': reset_time,
            'photons': photons,
            'alpha0': alpha0,
            'kappa': kappa,
            'chi': chi,
            'quasistatic_flux': quasistatic_flux,
            'high_frequency': high_frequency,
            'sampler': sampler
        }
    else:

        param_dic = {
            't1': np.inf,
            't2': np.inf,
            'dephasing_axis': 0,
            'dephasing': 0,
            'dephasing_angle': 0,
            'dephase_var': 0,
            'p_exc_init': 0,
            'p_dec_init': 0,
            'p_exc_fin': 0,
            'p_dec_fin': 0,
            'msmt_time': msmt_time,
            'interval_time': interval_time,
            'oneq_gate_time': oneq_gate_time,
            'CZ_gate_time': CZ_gate_time,
            'ISwap_gate_time': CZ_gate_time*np.sqrt(2),
            'reset_time': reset_time,
            'photons': False,
            'quasistatic_flux': None,
            'high_frequency': False,
            'sampler': sampler
        }

    for key, val in kwargs.items():
        param_dic[key] = val

    return param_dic


def get_update_rules(**kwargs):
    update_rules = ['update_quasistatic_flux']
    return update_rules
