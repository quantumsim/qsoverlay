import pytest

from qsoverlay.DiCarlo_setup import quick_setup, get_gate_dic, get_qubit,\
    get_update_rules
from qsoverlay.experiment_setup import Setup
import numpy as np
import tempfile

class FuzzyDict(object):
    def __init__(self, iterable, float_eq):
        self._float_eq = float_eq
        self._dict = dict(iterable)

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, val):
        self._dict[key] = val

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __contains__(self, key):
        return key in self._dict

    def __eq__(self, other):
        def compare(a, b):
            if isinstance(a, float) and isinstance(b, float):
                out = self._float_eq(a, b)
            else:
                out = a == b
            if not out:
                print('{} and {} are different'.format(a, b))
            return out
        try:
            if len(self) != len(other):
                return False
            for key in self:
                if not compare(self[key], other[key]):
                    return False
            return True
        except Exception:
            return False

    def __getattr__(self, attr):
        # free features borrowed from dict
        attr_val = getattr(self._dict, attr)
        if callable(attr_val):
            def wrapper(*args, **kwargs):
                result = attr_val(*args, **kwargs)
                if isinstance(result, dict):
                    return FuzzyDict(result, self._float_eq)
                return result
            return wrapper
        return attr_val


class TestSetup:

    def test_qubitdic_req_params(self):
        qubit_dic = get_qubit()
        assert 't1' in qubit_dic.keys()
        assert 't2' in qubit_dic.keys()
        assert 'sampler' in qubit_dic.keys()

    def test_qubitdic_nonoise(self):
        qubit_dic = get_qubit(noise_flag=False)
        assert qubit_dic['t1'] is np.inf
        assert qubit_dic['t2'] is np.inf
        assert 'sampler' in qubit_dic.keys()

    def test_gate_dic(self):
        gate_dic = get_gate_dic()
        for gparams in gate_dic.values():
            assert 'function' in gparams.keys()
            assert 'num_qubits' in gparams.keys()
            assert type(gparams['num_qubits']) is int
            assert 'circuit_args' in gparams.keys()
            assert type(gparams['circuit_args']) is dict
            assert 'builder_args' in gparams.keys()
            assert type(gparams['builder_args']) is dict
            assert 'user_kws' in gparams.keys()
            assert type(gparams['user_kws']) is list

    def test_update_rules(self):
        update_rules = get_update_rules()
        assert type(update_rules) is list

    def test_quick_setup_1q(self):
        qubit_list = ['q_test']
        with pytest.warns(UserWarning):
            # We did not provide any seed
            setup = quick_setup(qubit_list)
        assert hasattr(setup, 'gate_set')
        assert hasattr(setup, 'update_rules')
        assert hasattr(setup, 'qubit_dic')
        assert hasattr(setup, 'gate_dic')
        assert 'q_test' in setup.qubit_dic.keys()
        assert len(setup.qubit_dic.keys()) == 1
        for gate_name, gparams in setup.gate_dic.items():
            assert 'function' in gparams.keys()
            assert 'user_kws' in gparams.keys()

            if gparams['num_qubits'] == 1:
                assert (gate_name, 'q_test') in setup.gate_set

            for kw0, kw1 in gparams['circuit_args'].items():

                if type(kw1) is not str:
                    continue

                assert kw1 in setup.qubit_dic['q_test']
                if gparams['num_qubits'] == 1:

                    assert kw0 in setup.gate_set[(gate_name, 'q_test')][0]
                    assert setup.qubit_dic['q_test'][kw1] ==\
                        setup.gate_set[(gate_name, 'q_test')][0][kw0]

            for kw0, kw1 in gparams['builder_args'].items():

                if type(kw1) is not str:
                    continue

                assert kw1 in setup.qubit_dic['q_test']
                if gparams['num_qubits'] == 1:

                    assert kw0 in setup.gate_set[(gate_name, 'q_test')][1]
                    assert setup.qubit_dic['q_test'][kw1] ==\
                        setup.gate_set[(gate_name, 'q_test')][1][kw0]

    def test_quick_setup_2q(self):
        qubit_list = ['q0', 'q1']
        with pytest.warns(UserWarning):
            # We did not provide any seed
            setup = quick_setup(qubit_list)
        assert 'q0' in setup.qubit_dic.keys()
        assert 'q1' in setup.qubit_dic.keys()
        assert len(setup.qubit_dic.keys()) == 2
        for gate_name, gparams in setup.gate_dic.items():
            if gparams['num_qubits'] == 2:
                assert (gate_name, 'q0', 'q1') in setup.gate_set
                assert (gate_name, 'q1', 'q0') in setup.gate_set

                for kw0, kw1 in gparams['circuit_args'].items():
                    if type(kw1) is not str:
                        continue
                    assert setup.qubit_dic['q0'][kw1] ==\
                        setup.gate_set[(gate_name, 'q0', 'q1')][0][kw0]
                    assert setup.qubit_dic['q1'][kw1] ==\
                        setup.gate_set[(gate_name, 'q1', 'q0')][0][kw0]

                for kw0, kw1 in gparams['builder_args'].items():
                    if type(kw1) is not str:
                        continue
                    assert setup.qubit_dic['q0'][kw1] ==\
                        setup.gate_set[(gate_name, 'q0', 'q1')][1][kw0]
                    assert setup.qubit_dic['q1'][kw1] ==\
                        setup.gate_set[(gate_name, 'q1', 'q0')][1][kw0]

    @pytest.mark.xfail
    def test_save_load(self):
        rng = np.random.RandomState(42)
        qubit_list = ['q1', 'q2']
        connectivity_dic = {'q1': ['q2'], 'q2':['q1']}
        a = quick_setup(qubit_list=qubit_list,
                        connectivity_dic=connectivity_dic,
                        rng=rng)
        with tempfile.NamedTemporaryFile() as f:
            a.save(filename=f.name)
            b = Setup(filename=f.name, state=rng)

        for name in ('gate_dic', 'qubit_dic', 'gate_set'):
            assert a.__dict__[name]== b.__dict__[name]
        assert a.update_rules == b.update_rules
