import numpy as np
from qiskit.quantum_info import Statevector, partial_trace
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate
from squlearn.encoding_circuit import RandomLayeredEncodingCircuit


def approx_cross_validate_random_encoding_circuit(
        num_qubits: int,
        num_features: int,
        num_layers: int,
        seed: int,
        bases: str,
        X: np.ndarray,
        y: np.ndarray,
) -> dict[str, int | float | str | None]:
    try:
        encoding_circuit = RandomLayeredEncodingCircuit(
            num_qubits=num_qubits,
            num_features=num_features,
            min_num_layers=num_layers,
            max_num_layers=num_layers,
            seed=seed,
        )
        quantum_states = [
            Statevector.from_instruction(encoding_circuit.get_circuit(example, None))
            for example in X
        ]
        num_qubits = encoding_circuit.num_qubits
        num_bases = len(bases)
        X_quantum = np.ndarray((len(X), num_qubits * num_bases))
        for state_idx, state in enumerate(quantum_states):
            feature_idx = 0
            for qubit in range(num_qubits):
                trace_indices = [i for i in range(num_qubits) if i != qubit]
                rho = partial_trace(state, trace_indices)
                if "X" in bases:
                    X_quantum[state_idx, feature_idx] = float((rho.data[0, 1] + rho.data[1, 0]).real)
                    feature_idx += 1
                if "Y" in bases:
                    X_quantum[state_idx, feature_idx] = float((rho.data[1, 0] - rho.data[0, 1]).imag)
                    feature_idx += 1
                if "Z" in bases:
                    X_quantum[state_idx, feature_idx] = float((rho.data[0, 0] - rho.data[1, 1]).real)
                    feature_idx += 1
        logistic_regression = LogisticRegression()
        cross_validation = cross_validate(logistic_regression, X_quantum, y, cv=5)
        score = cross_validation["test_score"].mean()
    except:
        score = None
    return {
        "num_qubits": num_qubits,
        "num_features": num_features,
        "num_layers": num_layers,
        "seed": seed,
        "bases": bases,
        "score": score,
    }
