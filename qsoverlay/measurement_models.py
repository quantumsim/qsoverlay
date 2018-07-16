'''
Measurement_model:
qsoverlay measurement models are separate to the measurement function in
quantumsim. In particular, these are designed to not have to worry about
repeatedly preparing a state and sampling it for measurement, and to
take care of measurement crosstalk. Later they should possibly be included in
quantumsim.
'''
import numpy as np


class CorrelatedMeasurement:
    def __init__(self, qubits,
                 cc_matrix, populations,
                 random_state):
        '''
        A class to provide (currently) correlated
        measurement that includes measurement crosstalk.

        @qubits: list of qubits (giving order in which results
            will be returned)
        @cc_matrix: the cross-correlation measurement matrix
            ***as reported by an experimentalist*** - i.e.
            not the cross-correlation matrix that takes into
            account residual population.
        @populations: the residual excitations of the qubits
            in order.
        '''

        self.qubits = qubits
        self.num_qubits = len(qubits)
        self.lit_string = r'{' + '0:0{}b'.format(self.num_qubits) + r'}'
        self.random_state = random_state
        self.EQ_TOL = 1e-9

        pop_matrix = np.zeros([2**self.num_qubits, 2**self.num_qubits])

        # Make pop_matrix
        for j in range(2**self.num_qubits):
            for k in range(2**self.num_qubits):
                diff = j ^ k
                pop_matrix[j, k] = 1
                for n in range(self.num_qubits):
                    if diff % 2 == 1:
                        pop_matrix[j, k] *= populations[n]
                    else:
                        pop_matrix[j, k] *= (1-populations[n])
                    diff = diff // 2
                pop_matrix[k, j] = pop_matrix[j, k]

        # Calculate the real cc matrix taking into account the
        # fact that the experimental cc matrix is poisoned by
        # the residual excitations not accounted for in experiment.
        self.cc_matrix = cc_matrix @ np.linalg.inv(pop_matrix)

    def sample(self, rho_dist,
               num_measurements,
               data_type='shots',# If averages put single_shot to False in tomo
               output_format='full'):
        '''
        Calculates the true distribution of measurements from the
        peak_multiple_measurement function given in quantumsim,
        and generates a sampling of num_measurements measurements
        from this distribution.
        '''
        # rho_vec will hold the leading diagonal of the density matrix
        # (This is horribly inefficient, should be directly integrated
        # with quantumsim.)
        rho_vec = np.zeros(2**self.num_qubits)

        for j in range(2**self.num_qubits):
            j_list = list(reversed(self.lit_string.format(j)))

            rho_vec[j] = sum([
                x[1] for x in rho_dist if all([
                    x[0][q] == int(j_list[n])
                    for n, q in enumerate(self.qubits)])])

        if np.abs(sum(rho_vec) - 1) > self.EQ_TOL:
            raise ValueError('my rho normalization is: ', sum(rho_vec))

        # M_vec contains the measurement distributions.
        M_vec = self.cc_matrix @ rho_vec

        if np.abs(sum(M_vec) - 1) > self.EQ_TOL:
            raise ValueError('my measurement normalization is: ', sum(M_vec))

        if data_type == 'shots':

            measurements = self.random_state.choice(
                range(2**self.num_qubits),
                size=num_measurements,
                p=M_vec)

            measurements = [
                np.array(list(reversed(self.lit_string.format(m))),
                         dtype=int)
                for m in measurements]

            if output_format is not 'full':
                measurements = [[sum(m[indices]) % 2
                                 for indices in output_format]
                                for m in measurements]

        else:
            measurements = M_vec
            if output_format is not 'full':
                measurements = [sum([m for m, j in enumerate(measurements)
                                     if self.indices_in_j(indices, j)])
                                for indices in output_format]
                                
        return measurements

    def indices_in_j(self,indices, j):
        n = 0
        while j > 0:
            if n in indices and j % 2 == 0:
                return False
            n += 1
            j = j // 2
