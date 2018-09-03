from qsoverlay.circuit_builder import Builder
from qsoverlay.DiCarlo_setup import quick_setup
from quantumsim.sparsedm import SparseDM
import pytest
import numpy as np


class TestBuilder:

    def test_init(self):

        qubit_dic = {'q_test': {}}
        gate_dic = {}
        gate_set = {}
        b = Builder(qubit_dic=qubit_dic,
                    gate_dic=gate_dic,
                    gate_set=gate_set,
                    circuit_title='Test')
        assert len(b.qubit_dic.keys()) == 1
        assert b.gate_dic == {}
        assert b.gate_set == {}
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
        b = Builder(qubit_dic=qubit_dic,
                    gate_dic=gate_dic,
                    gate_set=gate_set,
                    circuit_title='Test')
        assert b.circuit.qubits[0].t1 == 10
        assert b.circuit.qubits[0].t2 == 20

    def test_T1T2_kwarginit(self):
        qubit_dic = {'q_test': {}}
        gate_dic = {}
        gate_set = {}
        b = Builder(qubit_dic=qubit_dic,
                    gate_dic=gate_dic,
                    gate_set=gate_set,
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
