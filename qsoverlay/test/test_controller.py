import numpy as np
from qsoverlay.DiCarlo_setup import quick_setup
from qsoverlay import Controller, Builder


class TestController:

    def test_expectation_vals(self):
        q_list = ['q' + str(i) for i in range(2)]
        setup = quick_setup(qubit_list=q_list, noise_flag=False)
        b = Builder(setup=setup)

        b.new_circuit('test_expect_vals')
        b.add_gate('ISwapRotation', ['q0', 'q1'], angle=-np.pi / 8)
        b.add_gate('Rz', ['q0'], angle=-np.pi / 2)

        cont = Controller(qubits=q_list, circuits={
                          'test_expect_vals': b.circuit})
        cont.make_state()
        cont.apply_circuit('test_expect_vals')

        exact = cont.get_expectation_values(msmts=[{'q0': 'X', 'q1': 'X'}])[0]
        noisy = cont.get_expectation_values(msmts=[{'q0': 'X', 'q1': 'X'}],
                                            num_repetitions=1000000)[0]

        assert abs((noisy-exact) / np.sqrt(1000000)) < 1e-6
