#!/usr/bin/env python3
"""generate_nb.py — Module D2: Quantum Gates as Matrix Operations"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# D2 — Quantum Gates as Matrix Operations
**Track:** Developer | **Difficulty:** ⭐⭐⭐☆☆ | **Est. Time:** 30 min

| | |
|---|---|
| **Prerequisites** | F1–F4, D1; linear algebra fundamentals |
| **Qiskit Modules** | `qiskit.quantum_info.Operator`, `qiskit.circuit.library` |
| **Companion Video** | Developer Module D2 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Extract the **unitary matrix** of any Qiskit gate using `Operator`
2. Verify gate properties: **unitarity**, **Hermiticity** (for Pauli gates), **self-inverse**
3. Compute multi-gate circuits as **matrix products** and verify against Qiskit
4. Understand **tensor products** ($\otimes$) for multi-qubit gates
5. Connect gate matrices to the **neural network weights analogy**
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Gates Are Unitary Matrices

A quantum gate on $n$ qubits is a $2^n \times 2^n$ **unitary matrix** $U$:

$$U^\dagger U = UU^\dagger = I$$

This means gates are:
- **Reversible:** $U^{-1} = U^\dagger$ (Hermitian conjugate is the inverse)
- **Norm-preserving:** $\|U|\psi\rangle\| = \||\psi\rangle\|$ (probability stays 1)
- **Composable:** circuits are matrix products (right to left in Dirac notation)

### The Single-Qubit Pauli Family

$$I = \begin{pmatrix}1&0\\0&1\end{pmatrix}, \;
  X = \begin{pmatrix}0&1\\1&0\end{pmatrix}, \;
  Y = \begin{pmatrix}0&-i\\i&0\end{pmatrix}, \;
  Z = \begin{pmatrix}1&0\\0&-1\end{pmatrix}$$

Key identities: $X^2 = Y^2 = Z^2 = I$, $XY = iZ$, $YZ = iX$, $ZX = iY$

### Two-Qubit Gate: Tensor Product

For a gate $U_A \otimes U_B$ acting on qubits A and B independently:

$$U_A \otimes U_B = \begin{pmatrix} u_{00}U_B & u_{01}U_B \\ u_{10}U_B & u_{11}U_B \end{pmatrix}$$

The CNOT gate is **not** a tensor product — it creates entanglement.

### ML Bridge

Unitary matrices are like **pure functions** in functional programming — reversible, no side effects, composable. In quantum ML, parameterized unitaries $U(\theta)$ play the role of weight matrices in neural networks.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Extract and Inspect Gate Matrices"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

def get_gate_matrix(gate_name: str, n_qubits: int = 1, **kwargs) -> np.ndarray:
    '''Build a 1-gate circuit and extract its unitary matrix.'''
    qc = QuantumCircuit(n_qubits)
    if gate_name == "cx":
        qc.cx(0, 1)
    elif gate_name == "cz":
        qc.cz(0, 1)
    elif gate_name == "swap":
        qc.swap(0, 1)
    elif gate_name in ("rz", "rx", "ry"):
        theta = kwargs.get("theta", np.pi/4)
        getattr(qc, gate_name)(theta, 0)
    else:
        getattr(qc, gate_name)(0)
    return Operator(qc).data

# Single-qubit gates
single_gates = ["x", "y", "z", "h", "s", "t", "sdg", "tdg"]
print(f"{'Gate':6s} {'Unitary?':9s} {'Hermitian?':11s} {'Self-inverse?':14s} {'det':>8s}")
print("-" * 55)
for name in single_gates:
    U = get_gate_matrix(name)
    is_unitary   = np.allclose(U.conj().T @ U, np.eye(2))
    is_hermitian = np.allclose(U, U.conj().T)
    is_self_inv  = np.allclose(U @ U, np.eye(2))
    det          = np.linalg.det(U)
    print(f"{name.upper():6s} {'✓' if is_unitary else '✗':9s} "
          f"{'✓' if is_hermitian else '✗':11s} {'✓' if is_self_inv else '✗':14s} "
          f"{det.real:+.4f}{det.imag:+.4f}j")

# Two-qubit gates
print("\nTwo-qubit gate shapes:")
for name in ["cx", "cz", "swap"]:
    U = get_gate_matrix(name, n_qubits=2)
    print(f"  {name.upper():6s}: {U.shape}  det = {np.linalg.det(U):.4f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Circuit = Matrix Product"""))

cells.append(nbf.v4.new_code_cell(r"""# A circuit with multiple gates = matrix multiplication (right to left)
# Circuit: H then Z then H
# Math: U_circuit = H @ Z @ H = X (the identity HZH = X)

H = get_gate_matrix("h")
Z = get_gate_matrix("z")
X = get_gate_matrix("x")

U_manual = H @ Z @ H   # right to left: first gate is rightmost

qc_hzh = QuantumCircuit(1)
qc_hzh.h(0); qc_hzh.z(0); qc_hzh.h(0)
U_qiskit = Operator(qc_hzh).data

print("Manual H @ Z @ H:")
print(np.round(U_manual.real, 6))
print("\nQiskit HZH circuit operator:")
print(np.round(U_qiskit.real, 6))
print("\nX gate:")
print(np.round(X.real, 6))
print(f"\nAre they equal? {np.allclose(np.abs(U_manual), np.abs(X))}")
print("Insight: HZH = X  →  Z in X-basis = X in Z-basis (basis rotation identity)")

# Visualize the matrix multiplication cascade
fig, axes = plt.subplots(1, 5, figsize=(16, 3))
matrices = {"H": H, "Z": Z, "H": H, "→ HZH =": U_manual, "X": X}
for ax, (label, M) in zip(axes, matrices.items()):
    im = ax.imshow(M.real, cmap="RdBu", vmin=-1, vmax=1)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{M.real[i,j]:.2f}", ha="center", va="center", fontsize=12,
                    color="white" if abs(M.real[i,j]) > 0.5 else "black")
    ax.set_title(label, fontsize=12, fontweight="bold")
    ax.set_xticks([]); ax.set_yticks([])

plt.suptitle("H @ Z @ H = X  (circuit = matrix product)", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("matrix_product.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Tensor Products for Multi-Qubit Circuits"""))

cells.append(nbf.v4.new_code_cell(r"""# When gates act on different qubits independently: tensor product
# H on q0, I on q1  →  H ⊗ I

H = get_gate_matrix("h")
I2 = np.eye(2)
X = get_gate_matrix("x")

# Tensor product: H ⊗ I (H on qubit 0, identity on qubit 1)
HI = np.kron(H, I2)  # numpy's kron = tensor product

# Build circuit and get matrix
qc_HI = QuantumCircuit(2)
qc_HI.h(0)  # only on qubit 0
U_qiskit_HI = Operator(qc_HI).data

print("Tensor product H ⊗ I (manual via numpy.kron):")
print(np.round(HI.real, 4))
print("\nQiskit H on qubit 0 only:")
print(np.round(U_qiskit_HI.real, 4))
print(f"Match: {np.allclose(HI, U_qiskit_HI)}")

# CNOT is NOT a tensor product
CNOT = get_gate_matrix("cx", n_qubits=2)
print(f"\nCNOT matrix (cannot be written as A ⊗ B):")
print(np.round(CNOT.real, 4))

# Prove CNOT is entangling: apply to |+0⟩ = (|0⟩+|1⟩)/√2 ⊗ |0⟩
from qiskit.quantum_info import Statevector
psi_in = Statevector([1/np.sqrt(2), 0, 1/np.sqrt(2), 0])  # |+0⟩
psi_out = psi_in.evolve(Operator(CNOT))  # Wait — need correct qubit ordering
qc_bell = QuantumCircuit(2); qc_bell.h(0); qc_bell.cx(0,1)
psi_bell = Statevector(qc_bell)
print(f"\nH⊗I then CNOT = Bell state: {np.round(psi_bell.data, 4)}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Rotation Gates — Parameterized Unitaries (ML Bridge)"""))

cells.append(nbf.v4.new_code_cell(r"""# Rz, Ry, Rx are continuous-parameter gates — the "weights" in quantum ML

theta_vals = np.linspace(0, 2*np.pi, 200)

fig, axes = plt.subplots(2, 3, figsize=(15, 8))

for row, (gate, title, formula) in enumerate([
    ("rz", "R_z(\\theta)", r"$R_z(\theta) = \begin{pmatrix}e^{-i\theta/2}&0\\0&e^{i\theta/2}\end{pmatrix}$"),
    ("ry", "R_y(\\theta)", r"$R_y(\theta) = \begin{pmatrix}\cos(\theta/2)&-\sin(\theta/2)\\\sin(\theta/2)&\cos(\theta/2)\end{pmatrix}$"),
]):
    # Real and imag parts of matrix elements vs theta
    real_00, real_01, real_10, real_11 = [], [], [], []
    for t in theta_vals:
        U = get_gate_matrix(gate, theta=t)
        real_00.append(U[0,0].real); real_01.append(U[0,1].real)
        real_10.append(U[1,0].real); real_11.append(U[1,1].real)

    ax = axes[row][0]
    ax.plot(theta_vals, real_00, label="Re(U₀₀)", lw=2)
    ax.plot(theta_vals, real_11, label="Re(U₁₁)", lw=2, ls="--")
    ax.plot(theta_vals, real_01, label="Re(U₀₁)", lw=2, ls=":")
    ax.set_xlabel("θ (radians)"); ax.set_ylabel("Matrix element (real)")
    ax.set_title(f"{gate.upper()} gate elements vs θ", fontsize=11, fontweight="bold")
    ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
    ax.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
    ax.set_xticklabels(["0", "π/2", "π", "3π/2", "2π"])

    # P(0) measurement outcome from |0⟩ state
    ax2 = axes[row][1]
    p0 = [np.cos(t/2)**2 if gate == "ry" else 1.0 for t in theta_vals]
    ax2.plot(theta_vals, p0, lw=2.5, color="green")
    ax2.set_xlabel("θ"); ax2.set_ylabel("P(|0⟩)")
    ax2.set_title(f"{gate.upper()}(θ)|0⟩ → P(|0⟩)\n(measurement probability)", fontsize=11, fontweight="bold")
    ax2.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
    ax2.set_xticklabels(["0", "π/2", "π", "3π/2", "2π"])
    ax2.grid(True, alpha=0.3); ax2.set_ylim(-0.05, 1.05)

# Special gate values
ax3 = axes[0][2]
special = {
    r"$R_y(0) = I$":        ("ry", 0),
    r"$R_y(\pi/2) = H'$":   ("ry", np.pi/2),
    r"$R_y(\pi) = X'$":     ("ry", np.pi),
    r"$R_z(\pi/2) = S$":    ("rz", np.pi/2),
    r"$R_z(\pi/4) = T$":    ("rz", np.pi/4),
    r"$R_z(\pi) = Z'$":     ("rz", np.pi),
}
for i, (label, (gate, t)) in enumerate(special.items()):
    U = get_gate_matrix(gate, theta=t)
    ax3.text(0.02, 0.92 - i*0.15, f"{label}: [{U[0,0]:.2f}, {U[0,1]:.2f}; {U[1,0]:.2f}, {U[1,1]:.2f}]",
             transform=ax3.transAxes, fontsize=9)
ax3.axis("off")
ax3.set_title("Special angle values", fontsize=11, fontweight="bold")

ax4 = axes[1][2]
ax4.axis("off")
ax4.text(0.1, 0.8, "ML/AI Bridge:\n\nRotation angles θ, φ, λ in quantum gates\nplay the role of WEIGHTS in neural networks.\n\nTraining a quantum circuit = optimizing θ\nusing gradient descent (parameter shift rule).\n\nU(θ) ↔ W (weight matrix)\nRy(θ) ↔ Linear layer with activation",
         transform=ax4.transAxes, fontsize=11, va="top",
         bbox=dict(boxstyle="round", facecolor="#E3F2FD", alpha=0.8))

plt.suptitle("Rotation Gates: Parameterized Unitaries — The Foundation of Quantum ML",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("rotation_gates.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Identity Verification

Verify these gate identities numerically:
1. $H^2 = I$
2. $S^2 = Z$
3. $T^2 = S$
4. $CNOT^2 = I$ (applying CNOT twice returns to identity)
5. $X \otimes X \cdot CNOT \cdot X \otimes X = CNOT$ (reversing control and target with local gates)
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — verify each identity

identities_to_verify = {
    "H² = I":           (lambda: get_gate_matrix("h") @ get_gate_matrix("h"),  np.eye(2)),
    "S² = Z":           (lambda: None,   get_gate_matrix("z")),   # YOUR CODE
    "T² = S":           (lambda: None,   get_gate_matrix("s")),   # YOUR CODE
    "CNOT² = I":        (lambda: None,   np.eye(4)),              # YOUR CODE
}

for identity, (lhs_fn, rhs) in identities_to_verify.items():
    lhs = lhs_fn()
    if lhs is None:
        print(f"  [SKIP] {identity} — implement me!")
        continue
    match = np.allclose(lhs, rhs, atol=1e-10)
    print(f"  {'✓' if match else '✗'} {identity}")
    if not match:
        print(f"    LHS:\n{np.round(lhs, 4)}")
        print(f"    RHS:\n{np.round(rhs, 4)}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Decompose a Target Gate

Any single-qubit unitary can be written as $U = e^{i\alpha} R_z(\beta) R_y(\gamma) R_z(\delta)$.

Find the parameters for the **Hadamard gate** and verify.

Hint: $H = R_z(\pi) R_y(\pi/2) \cdot e^{i\pi/2}$ (up to global phase)
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — decompose H into Rz, Ry, Rz
Ry_halfpi = get_gate_matrix("ry", theta=np.pi/2)
Rz_pi     = get_gate_matrix("rz", theta=np.pi)
H_target  = get_gate_matrix("h")

# Try: Rz(pi) @ Ry(pi/2)
decomp = None  # YOUR CODE HERE

print("Target H:")
print(np.round(H_target, 4))
print("\nDecomposed (Rz(π) @ Ry(π/2)):")
print(np.round(decomp, 4) if decomp is not None else "Not implemented")

# Global phase doesn't matter for measurement, check via inner product
# |⟨ψ_target|ψ_decomp⟩|² should be 1 for pure global phase difference
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Implement the **Solovay-Kitaev approximation** (simplified 1D version):

Given a target single-qubit unitary $U_{target}$, find a sequence of $\{H, T\}$ gates that approximates $U_{target}$ with fidelity $> 0.99$.

This is the basis of universal quantum gate sets — any gate can be approximated arbitrarily well using only H and T gates.

1. Enumerate sequences of H/T of length 1 through 8
2. For each sequence, compute the operator norm distance to the target
3. Return the best approximation found
4. Plot fidelity vs sequence length
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Gate Approximation via H, T enumeration
import itertools

H_mat = get_gate_matrix("h")
T_mat = get_gate_matrix("t")
gate_set = {"H": H_mat, "T": T_mat}

target = get_gate_matrix("rz", theta=np.pi/5)  # Target: Rz(π/5)
print(f"Target Rz(π/5):\n{np.round(target, 4)}")

best_fid = 0
best_seq = None

# YOUR CODE HERE: enumerate sequences and find best approximation
# Hint: for length in range(1, 7):
#           for seq in itertools.product(["H","T"], repeat=length):
#               U = compute_sequence_product(seq, gate_set)
#               fid = |Tr(U† @ target)|² / 4
#               if fid > best_fid: update best

print("Challenge: Implement the enumeration above")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Qiskit Operator class** — `qiskit.quantum_info.Operator` — full API reference
2. **Nielsen & Chuang**, Section 4.5 — Universal quantum gates and the Solovay-Kitaev theorem
3. **Barenco et al. (1995)** — "Elementary gates for quantum computation" — seminal paper
4. **Qiskit circuit.library** — All pre-built gate matrices with decompositions
5. **Schuld et al. (2021)** — "Effect of data encoding on the expressive power of variational quantum ML models" — matrix theory meets QML
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D2_gates_as_matrices.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
