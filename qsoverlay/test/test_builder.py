from qsoverlay.circuit_builder import Builder
from qsoverlay.experiment_setup import Setup
from qsoverlay.DiCarlo_setup import quick_setup
from quantumsim.sparsedm import SparseDM
import pytest
import numpy as np


class TestBuilder:

    def test_init(self):

        qubit_dic = {'q_test': {}}
        gate_dic = {}
        gate_set = {}
        setup = Setup(qubit_dic=qubit_dic,
                      gate_dic=gate_dic,
                      gate_set=gate_set)
        b = Builder(setup=setup,
                    circuit_title='Test')
        assert len(b.setup.qubit_dic.keys()) == 1
        assert b.setup.gate_dic == {}
        assert b.setup.gate_set == {}
        assert len(b.times.keys()) == 1
        assert b.circuit.title == 'Test'
        assert len(b.circuit.qubits) == 1
        assert b.circuit.qubits[0].name == 'q_test'
        assert b.circuit.qubits[0].t1 == np.inf
        assert b.circuit.qubits[0].t2 == np.inf

    def test_T1T2(self):

        qubit_dic = {'q_test': {'t1': 10, 't2': 20}}
        gate_dic = {}
        gate_set = {}
        setup = Setup(qubit_dic=qubit_dic,
                      gate_dic=gate_dic,
                      gate_set=gate_set)
        b = Builder(setup=setup,
                    circuit_title='Test')
        assert b.circuit.qubits[0].t1 == 10
        assert b.circuit.qubits[0].t2 == 20

    def test_T1T2_kwarginit(self):
        qubit_dic = {'q_test': {}}
        gate_dic = {}
        gate_set = {}
        setup = Setup(qubit_dic=qubit_dic,
                      gate_dic=gate_dic,
                      gate_set=gate_set)
        b = Builder(setup=setup,
                    circuit_title='Test',
                    t1=20,
                    t2=30)
        assert b.circuit.qubits[0].t1 == 20
        assert b.circuit.qubits[0].t2 == 30

    def test_make_perfect_bell(self):
        qubit_list = ['swap', 'cp']
        with pytest.warns(UserWarning):
            # We did not provide any seed
            setup = quick_setup(qubit_list, noise_flag=False)
        b = Builder(setup)
        b.add_gate('RotateY', ['swap'], angle=np.pi/2)
        b.add_gate('RotateY', ['cp'], angle=np.pi/2)
        b.add_gate('CZ', ['cp', 'swap'])
        b.add_gate('RotateY', ['cp'], angle=-np.pi/2)
        b.finalize()

        bell_circuit = b.circuit
        bell_state = SparseDM(bell_circuit.get_qubit_names())
        bell_circuit.apply_to(bell_state)
        diag = np.diag(bell_state.full_dm.to_array())

        assert np.abs(diag[0]-0.5) < 1e-10
        assert np.abs(diag[3]-0.5) < 1e-10
        assert np.abs(diag[1]) < 1e-10
        assert np.abs(diag[2]) < 1e-10

    def test_override(self):
        qubit_list = ['swap', 'cp']
        with pytest.warns(UserWarning):
            # We did not provide any seed
            setup = quick_setup(qubit_list, noise_flag=False)
        b = Builder(setup)
        b < ('RotateY', 'swap', np.pi/2)
        b < ('RotateY', 'cp', np.pi/2)
        b < ('CZ', 'cp', 'swap')
        b < ('RotateY', 'cp', -np.pi/2)
        b.finalize()

        bell_circuit = b.circuit
        bell_state = SparseDM(bell_circuit.get_qubit_names())
        bell_circuit.apply_to(bell_state)
        diag = np.diag(bell_state.full_dm.to_array())

        assert np.abs(diag[0]-0.5) < 1e-10
        assert np.abs(diag[3]-0.5) < 1e-10
        assert np.abs(diag[1]) < 1e-10
        assert np.abs(diag[2]) < 1e-10

    def test_qasm(self):
        qubit_list = ['swap', 'cp']
        with pytest.warns(UserWarning):
            # We did not provide any seed
            setup = quick_setup(qubit_list, noise_flag=False)
        b = Builder(setup)
        qasm0 = 'Ry 1.57079632679 swap'
        qasm1 = 'Ry 1.57079632679 cp'
        qasm2 = 'CZ cp swap'
        qasm3 = 'Ry -1.57079632679 cp'
        qasm_list = [qasm0, qasm1, qasm2, qasm3]
        b.add_qasm(qasm_list, qubits_first=False)
        b.finalize()

        bell_circuit = b.circuit
        bell_state = SparseDM(bell_circuit.get_qubit_names())
        bell_circuit.apply_to(bell_state)
        diag = np.diag(bell_state.full_dm.to_array())

        assert np.abs(diag[0]-0.5) < 1e-10
        assert np.abs(diag[3]-0.5) < 1e-10
        assert np.abs(diag[1]) < 1e-10
        assert np.abs(diag[2]) < 1e-10

    def test_make_imperfect_bell(self):
        qubit_list = ['swap', 'cp']
        with pytest.warns(UserWarning):
            # We did not provide any seed
            setup = quick_setup(qubit_list)
        b = Builder(setup)
        b.add_gate('RotateY', ['swap'], angle=np.pi/2)
        b.add_gate('RotateY', ['cp'], angle=np.pi/2)
        b.add_gate('CZ', ['cp', 'swap'])
        b.add_gate('RotateY', ['cp'], angle=-np.pi/2)
        b.finalize()

        bell_circuit = b.circuit
        bell_state = SparseDM(bell_circuit.get_qubit_names())
        bell_circuit.apply_to(bell_state)
        diag = np.diag(bell_state.full_dm.to_array())

        assert np.abs(diag[0]-0.5) < 1e-2
        assert np.abs(diag[3]-0.5) < 1e-2
        assert np.abs(diag[1]) < 3e-2
        assert np.abs(diag[2]) < 3e-2

    def test_shrink(self):
        qubit_list = ['q0','q1']
        with pytest.warns(UserWarning):
            setup = quick_setup(qubit_list)
        sq_gate_time = setup.qubit_dic['q0']['oneq_gate_time']
        cp_gate_time = setup.qubit_dic['q0']['CZ_gate_time']
        b = Builder(setup)
        b.add_gate('RotateY', ['q0'], angle=np.pi/2)
        b.add_gate('CZ', ['q0', 'q1'])
        b.add_gate('RotateY', ['q1'], angle=-np.pi/2)
        b.finalize(shrink=True)
        assert min([gate.time for gate in b.circuit.gates
                    if 'q1' in gate.involved_qubits]) == sq_gate_time + cp_gate_time/4
        assert max([gate.time for gate in b.circuit.gates
                    if 'q0' in gate.involved_qubits]) == sq_gate_time + 3*cp_gate_time/4

    def test_noshrink(self):
        qubit_list = ['q0','q1']
        with pytest.warns(UserWarning):
            setup = quick_setup(qubit_list)
        sq_gate_time = setup.qubit_dic['q0']['oneq_gate_time']
        cp_gate_time = setup.qubit_dic['q0']['CZ_gate_time']
        b = Builder(setup)
        b.add_gate('RotateY', ['q0'], angle=np.pi/2)
        b.add_gate('CZ', ['q0', 'q1'])
        b.add_gate('RotateY', ['q1'], angle=-np.pi/2)
        b.finalize(shrink=False)
        assert min([gate.time for gate in b.circuit.gates
                    if 'q1' in gate.involved_qubits]) == sq_gate_time/2 + cp_gate_time/4
        assert max([gate.time for gate in b.circuit.gates
                    if 'q0' in gate.involved_qubits]) == sq_gate_time*3/2 + cp_gate_time*3/4
        
    def test_simultaneous_gates(self):
        qubit_list = ['q0', 'q1']
        with pytest.warns(UserWarning):
            # We did not provide any seed
            setup = quick_setup(qubit_list)
        b = Builder(setup)
        b < ('RY', 'q0', np.pi/2)
        b < (('RY', 'q0', np.pi/2), ('RY', 'q1', np.pi/2))
        assert b.circuit.gates[-2].time == b.circuit.gates[-1].time
        assert b.times['q0'] == b.times['q1']

    def test_artificial_time(self):
        qubit_list = ['q0']
        with pytest.warns(UserWarning):
            # We did not provide any seed
            setup = quick_setup(qubit_list)
        b = Builder(setup)
        b.add_gate('RY', ['q0'], angle=np.pi/2)
        b.add_gate('RY', ['q0'], angle=np.pi/2, time=0)
        assert b.times['q0'] == setup.gate_set[('RY', 'q0')][1]['gate_time']
        assert b.circuit.gates[-1].time == 0
