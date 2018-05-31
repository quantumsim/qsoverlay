'''
Setup: a class to make and store setup files.
Setup files contain the experimental details required by
quantumsim to simulate actual quantum hardware given a
circuit (i.e. as a theorist would define).
'''
import json
from .gate_templates import GateData
from quantumsim.circuit import uniform_noisy_sampler


class Setup:

    def __init__(
            self, filename=None,
            seed=None, state=None,
            gate_dic={}, update_rules=[],
            qubit_dic={}, gate_set={}):

        if filename is not None:
            self.load(filename, seed, state)
        else:
            self.gate_dic = gate_dic
            self.update_rules = update_rules
            self.qubit_dic = qubit_dic
            self.gate_set = gate_set

    def load(self, filename, seed=None, state=None):
        with open(filename, 'r') as infile:
            setup_load_format = json.load(infile)

        self.update_rules = setup_load_format['update_rules']
        self.qubit_dic = setup_load_format['qubit_dic']

        # Currently assumes each qubit uses the same
        # uniform_noisy_sampler - this needs fixing

        if seed is None and state is None:
            seed = list(self.qubit_dic.values())[0]['seed']
        readout_error = list(self.qubit_dic.values())[0]['readout_error']
        sampler = uniform_noisy_sampler(
            seed=seed, state=state, readout_error=readout_error)

        for qb_params in self.qubit_dic.values():
            qb_params['sampler'] = sampler

        self.gate_set = {
            tuple(gate['key']): gate['val']
            for gate in setup_load_format['gate_set']
        }
        for gate in self.gate_set.values():
            if 'sampler' in gate[0] and gate[0]['sampler'] is True:
                gate[0]['sampler'] = sampler

        gd = GateData()

        self.gate_dic = {
            key: gd.available_gate_dic[val]
            for key, val in setup_load_format['gate_dic'].items()
        }

    def save(self, filename):
        # Save gate_dic

        # switch from functions to names of functions in
        # gate_dic to allow saving
        gate_dic_save_format = {
            key: val['name']
            for key, val in self.gate_dic.items()
        }

        # remove link to sampler in qubit_dic to allow saving
        qubit_dic_save_format = {
            key: {**val} for key, val in self.qubit_dic.items()
        }
        for qd in qubit_dic_save_format.values():
            del qd['sampler']

        gate_set_save_format = [
            {'key': key, 'val': [{**val[0]}, {**val[1]}]}
            for key, val in self.gate_set.items()
        ]
        for gate_desc in gate_set_save_format:
            if 'sampler' in gate_desc['val'][0]:
                gate_desc['val'][0]['sampler'] = True

        setup_save_format = {
            'gate_dic': gate_dic_save_format,
            'update_rules': self.update_rules,
            'qubit_dic': qubit_dic_save_format,
            'gate_set': gate_set_save_format
        }
        with open(filename, 'w') as outfile:
            json.dump(setup_save_format, outfile)
