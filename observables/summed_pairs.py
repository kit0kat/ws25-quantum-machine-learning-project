import itertools
import random

from squlearn.observables import CustomObservable


class SummedPairs(CustomObservable):

    def __init__(self, num_qubits: int, bases: list[str], seed: int = 0):
        super().__init__(
            num_qubits=num_qubits,
            operator_string=self._operator_string(num_qubits, bases, seed),
            parameterized=True,
        )

    @staticmethod
    def _operator_string(num_qubits: int, bases: list[str], seed: int = 0) -> list[str]:
        random.seed(seed)
        operator_string = []
        for idx1, idx2 in itertools.combinations(range(num_qubits), 2):
            op_list = list("I" * num_qubits)
            op_list[idx1] = random.choice(bases)
            op_list[idx2] = random.choice(bases)
            operator_string.append("".join(op_list))
        operator_string.append("I" * num_qubits)
        return operator_string
