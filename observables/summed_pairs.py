import itertools
import random

from squlearn.observables import CustomObservable


def SummedPairs(num_qubits: int, bases: list[str], seed: int = 0) -> CustomObservable:
    random.seed(seed)
    operator_string = []
    for idx1, idx2 in itertools.combinations(range(num_qubits), 2):
        op_list = list("I" * num_qubits)
        op_list[idx1] = random.choice(bases)
        op_list[idx2] = random.choice(bases)
        operator_string.append("".join(op_list))
    operator_string.append("I" * num_qubits)
    return CustomObservable(
        num_qubits=num_qubits,
        operator_string=operator_string,
        parameterized=True,
    )
