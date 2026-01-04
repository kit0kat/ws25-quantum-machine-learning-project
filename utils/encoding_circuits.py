import numpy as np
from matplotlib import pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm
from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit.circuit import ParameterVector
from qiskit.providers import Backend
from qiskit.quantum_info import PauliList, Statevector, partial_trace
from qiskit.visualization.bloch import Bloch
from squlearn.encoding_circuit.encoding_circuit_base import EncodingCircuitBase
from squlearn.observables.observable_base import ObservableBase


def get_num_gates(encoding_circuit: EncodingCircuitBase, backend: Backend | None) -> int:
    quantum_circuit = encoding_circuit.get_circuit(
        features=ParameterVector("x", encoding_circuit.num_features),
        parameters=ParameterVector("p", encoding_circuit.num_parameters),
    )
    transpiled_circuit = transpile(
        circuits=quantum_circuit,
        backend=backend,
    )
    return transpiled_circuit.size()


def get_transpiled_encoding_circuit(encoding_circuit: EncodingCircuitBase, backend: Backend | None) -> QuantumCircuit:
    return transpile(
        circuits=encoding_circuit.get_circuit(
            features=ParameterVector("x", encoding_circuit.num_features),
            parameters=ParameterVector("p", encoding_circuit.num_parameters),
        ),
        backend=backend,
    )


def get_measurement_circuits(
        encoding_circuit: EncodingCircuitBase,
        observable: ObservableBase,
        backend: Backend = None,
        parameters: np.ndarray = None,
        features: np.ndarray = None,
) -> list[QuantumCircuit]:
    quantum_circuit = encoding_circuit.get_circuit(
        parameters=parameters if parameters is not None else ParameterVector("p", encoding_circuit.num_parameters),
        features=features if features is not None else ParameterVector("x", encoding_circuit.num_features),
    )
    pauli_strings = observable.get_operator(
        parameters=ParameterVector("p", observable.num_parameters),
    ).paulis.to_labels()
    pauli_lists = PauliList(pauli_strings).group_qubit_wise_commuting()
    measurement_circuits = []
    for pauli_list in pauli_lists:
        measurement_circuit: QuantumCircuit = quantum_circuit.copy()
        measurement_circuit.barrier()
        classical_register = ClassicalRegister(
            size=pauli_list.num_qubits,
            name="+".join(pauli_list.to_labels()),
        )
        measurement_circuit.add_register(classical_register)
        for idx in range(pauli_list.num_qubits):
            basis = None
            for pauli in pauli_list:
                if pauli.to_label()[idx] != "I":
                    basis = pauli.to_label()[idx]
                    break
            if basis == "X":
                measurement_circuit.h(idx)
                measurement_circuit.measure(idx, idx)
            elif basis == "Y":
                measurement_circuit.sdg(idx)
                measurement_circuit.h(idx)
                measurement_circuit.measure(idx, idx)
            elif basis == "Z":
                measurement_circuit.measure(idx, idx)
        measurement_circuits.append(measurement_circuit)
    if backend:
        measurement_circuits = [
            transpile(measurement_circuit, backend)
            for measurement_circuit in measurement_circuits
        ]
    return measurement_circuits


def plot_encoded_quantum_data(
        encoding_circuit: EncodingCircuitBase,
        X: np.ndarray,
        y: np.ndarray,
) -> None:
    quantum_states = [
        Statevector.from_instruction(encoding_circuit.get_circuit(example, None))
        for example in X
    ]
    num_qubits = encoding_circuit.num_qubits
    num_classes = len(np.unique(y))
    fig, ax = plt.subplots(
        nrows=1,
        ncols=num_qubits,
        figsize=(5 * num_qubits, 8),
        subplot_kw={"projection": "3d"},
    )
    cmap = plt.get_cmap("tab10")
    norm = BoundaryNorm(np.arange(-0.5, num_classes, 1), cmap.N)
    for qubit in range(num_qubits):
        bloch = Bloch(fig=fig, axes=ax[qubit])
        for state_idx, state in enumerate(quantum_states):
            trace_indices = [i for i in range(num_qubits) if i != qubit]
            rho = partial_trace(state, trace_indices)
            c_x = float((rho.data[0, 1] + rho.data[1, 0]).real)
            c_y = float((rho.data[1, 0] - rho.data[0, 1]).imag)
            c_z = float((rho.data[0, 0] - rho.data[1, 1]).real)
            bloch.add_vectors([c_x, c_y, c_z])
        bloch.vector_color = [cmap(norm(label)) for label in y]
        bloch.render()
        ax[qubit].set_title(f"$q_{qubit}$", fontsize=18, pad=48)
    fig.colorbar(
        mappable=ScalarMappable(cmap=cmap, norm=norm),
        ax=ax,
        ticks=np.arange(num_classes),
        shrink=0.5,
    )
