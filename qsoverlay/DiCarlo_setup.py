'''
DiCarlo_setup: functions to return the parameters for noise and experimental
design of DiCarlo qubits, in a format compatable with a circuit builder.
'''

import numpy as np
from numpy import pi
from quantumsim.circuit import uniform_noisy_sampler, uniform_sampler
from .setup_functions import make_1q2q_gateset
from .gate_templates import CZ, CPhase, RotateX, RotateY, RotateZ, Measure,\
                   ISwap, ISwapRotation, ResetGate, Had, CNOT, XGate, YGate, ZGate, CRX,\
                   PrepGate
from .update_functions import update_quasistatic_flux
from .experiment_setup import Setup


def quick_setup(qubit_list,
                connectivity_dic=None,
                seed=None,
                **kwargs):
    '''
    Quick setup: a function to return a setup that may be immediately
    used to make a qsoverlay builder.

    The setup file accepts the following parameters, defined in
    arXiv:1703:04136 (or elsewhere):

    noise_flag(=True): turn on or off noise (for debugging)
    scale(=1): multiplier for t1,t2 (and divides other error rates
            by same amount)
    t1(=30000ns): standard T1 time
                (arXiv:1703.04136, App.B.1, eq. B2)
    t2(=30000ns): standard T2 time
                (arXiv:1703.04136, App.B.1, eq. B3
                                   and Sec.IV.B.1 eq. 6)
    dephasing_axis(=1e-4): dephasing of x/y rotations along the
            axis (arXiv:1703.04136 App.B.3 eq below B5
                  defined as p_axis)
    dephasing_angle(=5e-4): dephasing of x/y rotations in the plane
                (arXiv:1703.04136 App.B.3 eq below B5
                 defined as p_plane)
    dephasing(=5e-4): dephasing of z rotations in the plane
                (arXiv:1703.04136 App.B.3 eq below B5
                 defined as p_plane)
    p_exc_init(=0.0): additional excitations between initial
                dephasing and readout in measurement
                (separate from T1 effects!)
                (arXiv:1703.04136 App.B.6 Fig.9
                 defined as $p_1^uparrow$)
    p_dec_init(=0.005): additional relaxation between initial
                dephasing and readout in measurement
                (separate from T1 effects!)
                (arXiv:1703.04136 App.B.6 Fig.9
                 defined as $p_1^downarrow$)
    p_exc_fin(=0.0): additional excitations between readout
                and end of the measurement period
                (separate from T1 effects!)
                (arXiv:1703.04136 App.B.6 Fig.9
                 defined as $p_2^uparrow$)
    p_dec_fin(=0.015): additional relaxation between readout
                and end of the measurement period
                (separate from T1 effects!)
                (arXiv:1703.04136 App.B.6 Fig.9
                 defined as $p_2^downarrow$)
    residual_excitations(=0.01): residual excitation population
                in transmon qubits after readout.
    photons(=False): whether to include dephasing due to
                resonator photons after measurements.
                (arXiv:1703.04136 App.B.2)
    alpha0(=4 photons): photon population at the end of the
                measurement window
                (arXiv:1703.04136 App.B.2 equation
                 bottom-left of page 12.)
    kappa(=1 / 250 ns^-1): Resonator kappa
                (arXiv:1703.04136 App.B.2 equation
                 bottom-left of page 12.)
    chi(=1.3 * 1e-3 ns^-1): Resonator chi
                (arXiv:1703.04136 App.B.2 equation
                 bottom-left of page 12.)
    static_flux_std(=None): Variance of static flux
                in the resonator. None=off.
                Note - turning this on
                will require a circuit be repeatedly simulated
                to acquire good statistics of this noise.
                (arXiv:1703.04136 App.B.5 final
                 equation.)
    high_frequency(=False): Whether this qubit
                is affected by two-qubit flux noise.
    dephase_var(=1e-2/(2*pi)): Variance of incoherent version
                of static flux noise (integrated over
                all realisations).
    msmt_time(=600ns): Total time for measurement (including
                time for resonator depletion/relaxation).
    interval_time(=150ns): Point in the measurement time that
                the readout occurs at.
    oneq_gate_time(=20ns): Time that every single qubit gate
                takes to perform.
    CZ_gate_time(=40ns): time required to perform CZ gate.
                ISwap gate times are fixed to sqrt(2) times this.
    reset_time(=500ns): time required to reset qubits (following
                arXiv:1801.07689, but currently without any error
                in the reset itself).
    sampler(=None): sampler to generate measurement results.
    seed(=None): seed to generate new sampler if the above is None.
    readout_error(=0.005): readout error in a sampler if the
                above is None
                (epsilon_{RO}^0=epsilon_{RO}^1 in
                 arXiv:1703.04136, App.B.6 Fig.9)
    '''

    if seed is not None:
        state = np.random.RandomState(seed)
        kwargs['state'] = state

    setup = {
        'gate_dic': get_gate_dic(),
        'update_rules': get_update_rules(**kwargs),
        'qubit_dic': {
            q: get_qubit(**kwargs) for q in qubit_list
        }
    }

    if connectivity_dic:
        for qubit in qubit_list:
            if qubit not in connectivity_dic:
                connectivity_dic[qubit] = []

    setup['gate_set'] = make_1q2q_gateset(qubit_dic=setup['qubit_dic'],
                                          gate_dic=setup['gate_dic'],
                                          connectivity_dic=connectivity_dic)
    return Setup(**setup)


def asymmetric_setup(qubit_parameters={},
                     connectivity_dic=None,
                     seed=None,
                     **kwargs):
    '''
    Prepares a setup for asymmetric qubits that may be immediately used to make
    a qsoverlay builder

    qubit_parameters is a dictionary that contains the paramters for each qubit
    in the following form:
    {'q1': {'t1': val, 't2': val, ...},
     'q2': {'t1': val, 't2': val, ...}}
    or:
    [['q1', 'q2', .., 'qn'],[{'t1': value, 't2': value, ...},
    {'t1': value, 't2: value, ...}, ..., {'t1': value, 't2': value, ...}]]
    Unspecified parameters will take the default values from get_qubit function
    '''
    if type(qubit_parameters) == list:
        qubit_parameters = {
            key: val
            for key, val in zip(qubit_parameters[0], qubit_parameters[1])}

    if seed is not None:
        for qubit in qubit_parameters.values:
            qubit['state'] = np.random.RandomState(seed)

    qubit_list = qubit_parameters.keys()
    asym_setup = {
        'gate_dic': get_gate_dic(),
        'update_rules': get_update_rules(**kwargs),
        'qubit_dic': {q: get_qubit(**params)
                      for q, params in qubit_parameters.items()}
    }
    if connectivity_dic:
        for qubit in qubit_list:
            if qubit not in connectivity_dic:
                connectivity_dic[qubit] = []

    asym_setup['gate_set'] = make_1q2q_gateset(
        qubit_dic=asym_setup['qubit_dic'],
        gate_dic=asym_setup['gate_dic'],
        connectivity_dic=connectivity_dic)
    return Setup(**asym_setup)


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
        'prepz': PrepGate,
        'PrepGate': PrepGate,
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
              t2_enh=np.inf,
              dephasing_axis=1e-4,
              dephasing_angle=5e-4,
              dephasing=5e-4,
              p_exc_init=0.0,
              p_dec_init=0.005,
              p_exc_fin=0.0,
              p_dec_fin=0.015,
              residual_excitations=0.01,
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
              state=None,
              sampler=None,
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
            sampler = uniform_noisy_sampler(state=state,
                                            readout_error=readout_error)
        else:
            readout_error = 0
            sampler = uniform_sampler(state=state)

    if static_flux_std is not None:
        quasistatic_flux = static_flux_std * np.random.randn()
    else:
        quasistatic_flux = None

    if noise_flag is True:

        param_dic = {
            't1': t1/scale,
            't2': t2/scale,
            't2_enh':t2_enh,
            'dephasing_axis': dephasing_axis*scale,
            'dephasing': dephasing*scale,
            'dephasing_angle': dephasing_angle*scale,
            'dephase_var': dephase_var*scale,
            'p_exc_init': p_exc_init*scale,
            'p_dec_init': p_dec_init*scale,
            'p_exc_fin': p_exc_fin*scale,
            'p_dec_fin': p_dec_fin*scale,
            'residual_excitations': residual_excitations*scale,
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
            'sampler': sampler,
            'readout_error': readout_error,
        }
    else:

        param_dic = {
            't1': np.inf,
            't2': np.inf,
            't2_enh':t2_enh,
            'dephasing_axis': 0,
            'dephasing': 0,
            'dephasing_angle': 0,
            'dephase_var': 0,
            'p_exc_init': 0,
            'p_dec_init': 0,
            'p_exc_fin': 0,
            'p_dec_fin': 0,
            'residual_excitations': 0,
            'msmt_time': msmt_time,
            'interval_time': interval_time,
            'oneq_gate_time': oneq_gate_time,
            'CZ_gate_time': CZ_gate_time,
            'ISwap_gate_time': CZ_gate_time*np.sqrt(2),
            'reset_time': reset_time,
            'photons': False,
            'quasistatic_flux': None,
            'high_frequency': False,
            'sampler': sampler,
            'readout_error': 0,
        }

    for key, val in kwargs.items():
        param_dic[key] = val

    return param_dic


def get_update_rules(**kwargs):
    update_rules = ['update_quasistatic_flux']
    return update_rules
