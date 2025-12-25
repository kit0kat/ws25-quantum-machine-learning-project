import random

from squlearn.observables import CustomObservable


class SummedNeighbours(CustomObservable):

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
        for idx in range(num_qubits - 1):
            op_list = list("I" * num_qubits)
            op_list[idx] = random.choice(bases)
            op_list[idx + 1] = random.choice(bases)
            operator_string.append("".join(op_list))
        operator_string.append("I" * num_qubits)
        return operator_string
