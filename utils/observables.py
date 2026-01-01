from qiskit.circuit import ParameterVector
from squlearn.observables.observable_base import ObservableBase


def get_num_terms(observable: ObservableBase) -> int:
    param_vector = ParameterVector("p", observable.num_parameters)
    pauli_list = observable.get_operator(param_vector).paulis
    return len(pauli_list)


def get_pauli_strings(observable: ObservableBase) -> list[str]:
    return observable.get_operator(ParameterVector("p", observable.num_parameters)).paulis.to_labels()


def get_pauli_sum(observable: ObservableBase) -> str:
    return " + ".join(get_pauli_strings(observable))
