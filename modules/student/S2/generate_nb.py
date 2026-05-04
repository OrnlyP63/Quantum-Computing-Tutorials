#!/usr/bin/env python3
"""generate_nb.py — Module S2: Quantum Gates — The Building Blocks"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# S2 — Quantum Gates: The Building Blocks
**Track:** Student | **Difficulty:** ⭐⭐☆☆☆ | **Est. Time:** 25 min

| | |
|---|---|
| **Prerequisites** | F1–F4, S1 |
| **Qiskit Modules** | `qiskit`, `qiskit_aer`, `qiskit.quantum_info` |
| **Companion Video** | Student Module S2 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Apply X, H, Z, Y, and S gates and describe each one's effect on the Bloch sphere
2. Verify that quantum gates are **unitary** ($U^\dagger U = I$) and therefore **reversible**
3. Compose multiple gates and predict the final state
4. Distinguish between gates that change **amplitude** vs gates that change **phase**
5. Use fill-in-the-blank circuits to complete a target transformation
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Concept Summary

### Gates as Unitary Matrices

A quantum gate is a **unitary matrix** $U$ acting on qubit state vectors:

$$U|\psi\rangle = |\psi'\rangle, \quad U^\dagger U = UU^\dagger = I$$

Unitary means: reversible (no information loss) and norm-preserving (probability still sums to 1).

### The Pauli Gates

$$X = \begin{pmatrix}0 & 1\\1 & 0\end{pmatrix}, \quad
  Y = \begin{pmatrix}0 & -i\\i & 0\end{pmatrix}, \quad
  Z = \begin{pmatrix}1 & 0\\0 & -1\end{pmatrix}$$

- **X (NOT gate):** Flips $|0\rangle \leftrightarrow |1\rangle$ — rotation of $\pi$ around X-axis
- **Z (Phase flip):** $|0\rangle \to |0\rangle$, $|1\rangle \to -|1\rangle$ — rotation of $\pi$ around Z-axis
- **Y:** Combines X and Z effects — rotation of $\pi$ around Y-axis

### Hadamard and Phase Gates

$$H = \frac{1}{\sqrt{2}}\begin{pmatrix}1 & 1\\1 & -1\end{pmatrix}, \quad
  S = \begin{pmatrix}1 & 0\\0 & i\end{pmatrix}, \quad
  T = \begin{pmatrix}1 & 0\\0 & e^{i\pi/4}\end{pmatrix}$$

On the Bloch sphere: **H** swaps X and Z axes; **S** rotates $\pi/2$ around Z; **T** rotates $\pi/4$ around Z.

> **Analogy:** Gates are turns of a spinning top. X, Y, Z are 180° spins on three perpendicular axes. H is a 180° spin on the diagonal X+Z axis.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Gate Matrix Inspection"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

# Inspect unitary matrices of common gates
gate_names = ["x", "y", "z", "h", "s", "t"]
matrices = {}

for name in gate_names:
    qc = QuantumCircuit(1)
    getattr(qc, name)(0)
    op = Operator(qc)
    matrices[name.upper()] = op.data
    print(f"{name.upper()} gate:\n{np.round(op.data, 4)}\n")

# Verify unitarity: U†U = I
print("=== Unitarity Check (U†U should be Identity) ===")
for name, U in matrices.items():
    residual = np.max(np.abs(U.conj().T @ U - np.eye(2)))
    ok = "✓" if residual < 1e-10 else "✗"
    print(f"{ok} {name}: ||U†U - I||_max = {residual:.2e}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Visualize Gate Effects on the Bloch Sphere"""))

cells.append(nbf.v4.new_code_cell(r"""from mpl_toolkits.mplot3d import Axes3D
from qiskit.quantum_info import DensityMatrix

def bloch_vec(sv):
    dm = DensityMatrix(sv).data
    return np.array([2*dm[0,1].real, 2*dm[0,1].imag, (dm[0,0]-dm[1,1]).real])

def draw_sphere(ax):
    u = np.linspace(0, 2*np.pi, 30); v = np.linspace(0, np.pi, 30)
    ax.plot_surface(np.outer(np.cos(u), np.sin(v)),
                    np.outer(np.sin(u), np.sin(v)),
                    np.outer(np.ones(30), np.cos(v)),
                    alpha=0.04, color="cyan")
    ax.plot_wireframe(np.outer(np.cos(u), np.sin(v)),
                      np.outer(np.sin(u), np.sin(v)),
                      np.outer(np.ones(30), np.cos(v)),
                      alpha=0.07, color="navy", lw=0.4)
    for (d, l) in [([0,0,1.25],"|0⟩"),([0,0,-1.25],"|1⟩"),
                   ([1.25,0,0],"|+⟩")]:
        ax.text(*d, l, fontsize=7, ha="center")
    ax.set_xlim(-1.4,1.4); ax.set_ylim(-1.4,1.4); ax.set_zlim(-1.4,1.4)

# Starting from |0⟩, show effect of each gate
start_sv = Statevector([1, 0])
gates_demo = [
    ("X\n(bit flip)", lambda qc: qc.x(0), "red"),
    ("H\n(superpose)", lambda qc: qc.h(0), "blue"),
    ("Z\n(phase flip)", lambda qc: qc.z(0), "green"),
    ("Y", lambda qc: qc.y(0), "orange"),
    ("S\n(phase π/2)", lambda qc: qc.s(0), "purple"),
    ("T\n(phase π/4)", lambda qc: qc.t(0), "brown"),
]

fig = plt.figure(figsize=(18, 6))
for i, (name, gate_fn, color) in enumerate(gates_demo):
    ax = fig.add_subplot(2, 6, i+1, projection="3d")
    draw_sphere(ax)

    # Draw starting vector (gray)
    ax.quiver(0,0,0, 0,0,1, arrow_length_ratio=0.12, color="gray", lw=1.5, alpha=0.5)
    ax.scatter(0,0,1, s=30, color="gray", zorder=3)

    # Draw result vector (colored)
    qc = QuantumCircuit(1)
    gate_fn(qc)
    sv = Statevector(qc)
    bv = bloch_vec(sv)
    ax.quiver(0,0,0, *bv, arrow_length_ratio=0.12, color=color, lw=2.5)
    ax.scatter(*bv, s=60, color=color, zorder=5)
    ax.set_title(f"Gate: {name}\n{qc.draw(output='text')}", fontsize=7, fontweight="bold")

plt.suptitle("Effect of Each Single-Qubit Gate on |0⟩ (Bloch Sphere View)\n"
             "Gray arrow = |0⟩ (north pole), Colored = result", fontsize=11, fontweight="bold")
plt.tight_layout()
plt.savefig("gates_bloch.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Gate Composition: Order Matters!"""))

cells.append(nbf.v4.new_code_cell(r"""from qiskit_aer import AerSimulator
from qiskit import transpile

sim = AerSimulator()

# XH vs HX — different results!
experiments = {
    "H|0⟩":    [("h", 0)],
    "X|0⟩":    [("x", 0)],
    "HX|0⟩":   [("x", 0), ("h", 0)],  # H applied AFTER X
    "XH|0⟩":   [("h", 0), ("x", 0)],  # X applied AFTER H
    "HZH|0⟩":  [("h", 0), ("z", 0), ("h", 0)],  # HZH = X (identity swap)
}

fig, axes = plt.subplots(1, len(experiments), figsize=(16, 4))

for ax, (label, gates) in zip(axes, experiments.items()):
    qc = QuantumCircuit(1, 1)
    for gate, qubit in gates:
        getattr(qc, gate)(qubit)

    # Show statevector (no measurement)
    sv = Statevector(qc)
    print(f"{label}: α={sv.data[0]:.3f}, β={sv.data[1]:.3f}  "
          f"→ P(0)={abs(sv.data[0])**2:.3f}, P(1)={abs(sv.data[1])**2:.3f}")

    # Add measurement and simulate
    qc.measure(0, 0)
    job = sim.run(transpile(qc, sim), shots=4096)
    counts = job.result().get_counts()
    total = sum(counts.values())
    vals = [counts.get("0", 0)/total, counts.get("1", 0)/total]
    bars = ax.bar(["0", "1"], vals, color=["#2196F3", "#FF5722"], edgecolor="black", width=0.5)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{bar.get_height():.2f}", ha="center", fontsize=11)
    ax.set_title(label, fontsize=11, fontweight="bold")
    ax.set_ylim(0, 1.2); ax.set_ylabel("Probability")

plt.suptitle("Gate Order Matters: XH ≠ HX\nBut HZH = X (basis rotation identity)",
             fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("gate_composition.png", dpi=120, bbox_inches="tight")
plt.show()

print("\nKey identity: HZH = X  →  Z in X-basis = X in Z-basis")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Fill in the Gate

Each row gives a starting state and target state. Find the single gate that performs the transformation.

| Start | Target | Gate |
|---|---|---|
| $\|0\rangle$ | $\|1\rangle$ | ??? |
| $\|+\rangle$ | $\|-\rangle$ | ??? |
| $\|0\rangle$ | $\|+\rangle$ | ??? |
| $\|1\rangle$ | $i\|1\rangle$ | ??? |
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — fill in the gate for each transformation
transformations = [
    ("|0⟩ → |1⟩",   Statevector([1,0]), Statevector([0,1]),  "???"),  # X
    ("|+⟩ → |−⟩",   Statevector([1/np.sqrt(2), 1/np.sqrt(2)]),
                     Statevector([1/np.sqrt(2),-1/np.sqrt(2)]), "???"),  # Z
    ("|0⟩ → |+⟩",   Statevector([1,0]), Statevector([1/np.sqrt(2), 1/np.sqrt(2)]), "???"),  # H
    ("|1⟩ → i|1⟩",  Statevector([0,1]), Statevector([0, 1j]), "???"),  # S
]

for label, sv_in, sv_target, gate_guess in transformations:
    # YOUR CODE HERE: build a circuit, apply your guessed gate, check
    # Hint: compute the dot product ⟨target|gate_applied⟩ — should be 1.0
    print(f"{label}:  gate = {gate_guess}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Verify H² = I

Apply H twice to $|+\rangle$. The result should be $|0\rangle$. Verify analytically and by simulation.

Then verify $X^2 = I$ and $Z^2 = I$ as well.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — verify that H² = I, X² = I, Z² = I
for gate_name, n_reps in [("h", 2), ("x", 2), ("z", 2), ("h", 4)]:
    qc = QuantumCircuit(1, 1)
    for _ in range(n_reps):
        getattr(qc, gate_name)(0)
    sv = Statevector(qc)
    print(f"{gate_name.upper()}^{n_reps}|0⟩ = {np.round(sv.data, 4)}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Prove and demonstrate that **any single-qubit gate can be decomposed** into Ry and Rz rotations:

$$U(\theta, \phi, \lambda) = R_z(\phi) R_y(\theta) R_z(\lambda)$$

This is the ZYZ decomposition. For a specific target state $|\psi\rangle = \cos(30°)|0\rangle + i\sin(30°)|1\rangle$:
1. Find the required $\theta$, $\phi$, $\lambda$ values
2. Build the decomposed circuit
3. Verify the statevector matches the target
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — ZYZ decomposition
# YOUR CODE HERE

# Target state
theta_state = np.radians(60)  # Bloch theta (note: twice the coefficient angle)
phi_state   = np.pi / 2       # relative phase

alpha = np.cos(theta_state / 2)
beta  = np.exp(1j * phi_state) * np.sin(theta_state / 2)
target_sv = Statevector([alpha, beta])
print(f"Target: {np.round(target_sv.data, 4)}")

# Build with Ry + Rz
qc_decomp = QuantumCircuit(1)
# YOUR CODE HERE: qc_decomp.rz(...), qc_decomp.ry(...), qc_decomp.rz(...)

result_sv = Statevector(qc_decomp)
print(f"Result: {np.round(result_sv.data, 4)}")

from qiskit.quantum_info import state_fidelity
fidelity = state_fidelity(target_sv, result_sv)
print(f"Fidelity: {fidelity:.6f}  (should be 1.0)")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Qiskit Textbook** — "Single-Qubit Gates" section with interactive Bloch sphere
2. **Nielsen & Chuang**, Section 4.2 — Single-qubit gates and their decompositions
3. **IBM Quantum Circuit Composer** — Visual gate builder at quantum.ibm.com
4. **Qiskit Gate Library** — `qiskit.circuit.library` full list of standard gates
5. **Bloch sphere rotation intuition** — 3Blue1Brown "Quaternions and 3D rotations" (analogy)
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "S2_quantum_gates.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
