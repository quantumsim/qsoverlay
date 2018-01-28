from qsoverlay.circuit_builder import Builder
from qsoverlay.DiCarlo_setup import quick_setup
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
