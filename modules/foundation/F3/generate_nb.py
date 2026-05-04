#!/usr/bin/env python3
"""generate_nb.py — Module F3: Qubits, States & Measurement"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# F3 — Qubits, States & Measurement
**Track:** Foundation (All Audiences) | **Difficulty:** ⭐⭐☆☆☆ | **Est. Time:** 35 min

| | |
|---|---|
| **Prerequisites** | F1, F2; complex numbers at a high school level |
| **Qiskit Modules** | `qiskit.quantum_info.Statevector`, `qiskit.visualization` |
| **Companion Video** | Foundation Module F3 |

---
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Represent a qubit state as a **complex vector** in Hilbert space $\mathbb{C}^2$
2. Use the **Born rule** to compute measurement probabilities from amplitudes
3. Understand **state collapse** and why quantum measurement is irreversible
4. Navigate the **Bloch sphere** and map gates to geometric rotations
5. Distinguish **pure states**, **mixed states**, and what decoherence does to each
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Concept Summary

### Hilbert Space Representation

A qubit lives in $\mathcal{H} = \mathbb{C}^2$. The computational basis:

$$|0\rangle = \begin{pmatrix}1\\0\end{pmatrix}, \quad |1\rangle = \begin{pmatrix}0\\1\end{pmatrix}$$

A general pure state:

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle = \begin{pmatrix}\alpha\\\beta\end{pmatrix}, \quad \alpha,\beta \in \mathbb{C}, \quad \langle\psi|\psi\rangle = |\alpha|^2 + |\beta|^2 = 1$$

### Born Rule

The probability of obtaining outcome $m$ when measuring in basis $\{|m\rangle\}$:

$$P(m) = |\langle m|\psi\rangle|^2$$

### State Collapse (Projection Postulate)

Immediately after measuring outcome $m$, the state **collapses**:

$$|\psi\rangle \xrightarrow{\text{measure } m} \frac{M_m|\psi\rangle}{\sqrt{\langle\psi|M_m^\dagger M_m|\psi\rangle}}$$

For standard computational-basis measurement: $|\psi\rangle \to |m\rangle$. The pre-measurement state is **permanently destroyed**.

### Density Matrix (Mixed States)

A mixed state $\rho$ (statistical ensemble, or post-decoherence qubit):

$$\rho = \sum_i p_i |\psi_i\rangle\langle\psi_i|, \quad \text{Tr}(\rho) = 1$$

Pure state: $\rho^2 = \rho$, i.e., $\text{Tr}(\rho^2) = 1$. Mixed state: $\text{Tr}(\rho^2) < 1$.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Statevector Arithmetic with Qiskit"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, state_fidelity
import matplotlib.pyplot as plt

# ---- Define key states manually ----
ket_0 = Statevector([1, 0])
ket_1 = Statevector([0, 1])
ket_plus  = Statevector([1/np.sqrt(2),  1/np.sqrt(2)])
ket_minus = Statevector([1/np.sqrt(2), -1/np.sqrt(2)])
ket_i     = Statevector([1/np.sqrt(2),  1j/np.sqrt(2)])

states = {"|0⟩": ket_0, "|1⟩": ket_1,
          "|+⟩": ket_plus, "|−⟩": ket_minus, "|i⟩": ket_i}

print(f"{'State':6s}  {'α':>10s}  {'β':>10s}  {'P(0)':>6s}  {'P(1)':>6s}  {'Pure?':>6s}")
print("-" * 55)
for name, sv in states.items():
    a, b = sv.data
    pure = np.isclose(np.trace(DensityMatrix(sv).data @ DensityMatrix(sv).data), 1.0)
    print(f"{name:6s}  {a:>10.4f}  {b:>10.4f}  {abs(a)**2:>6.3f}  {abs(b)**2:>6.3f}  {'Yes':>6s}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Visualizing State Collapse"""))

cells.append(nbf.v4.new_code_cell(r"""from qiskit_aer import AerSimulator
from qiskit import transpile

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# --- Scenario 1: Measure H|0⟩ ---
qc1 = QuantumCircuit(1, 1)
qc1.h(0)
qc1.measure(0, 0)

# --- Scenario 2: Measure H|0⟩ TWICE (simulate re-measurement) ---
qc2 = QuantumCircuit(1, 2)
qc2.h(0)
qc2.measure(0, 0)   # first measurement → collapses to |0⟩ or |1⟩
# After collapse, second H on collapsed state would give H|0⟩ or H|1⟩
# Both H|0⟩ and H|1⟩ measured: still 50/50 (because H|0⟩ and H|1⟩ differ by phase only)

# --- Scenario 3: Measure in X basis (Hadamard + measure) ---
qc3 = QuantumCircuit(1, 1)
qc3.h(0)   # prepare |+⟩
qc3.h(0)   # rotate back to computational basis = measure in X basis
qc3.measure(0, 0)  # |+⟩ measured in X basis → always 0

sim = AerSimulator()
shots = 4096

for ax, qc, title in zip(axes,
    [qc1, qc2, qc3],
    ["H|0⟩ measured in Z-basis\n(50/50 random)",
     "H|0⟩ then H again, measured\n(= measure |+⟩ in X-basis → always 0)",
     "|+⟩ rotated back and measured\n(deterministic: always '0')"]):
    job = sim.run(transpile(qc, sim), shots=shots)
    counts = job.result().get_counts()
    keys = sorted(counts.keys())
    vals = [counts.get(k, 0) for k in keys]
    colors = ["#2196F3" if "0" in k else "#FF5722" for k in keys]
    bars = ax.bar(keys, vals, color=colors, edgecolor="black", width=0.5)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                f"{bar.get_height()/shots*100:.1f}%", ha="center", fontsize=12)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_ylabel("Count"); ax.set_ylim(0, shots * 0.65)

plt.suptitle("Measurement Basis Determines Randomness vs Determinism",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("state_collapse.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Bloch Sphere Map — All Standard States"""))

cells.append(nbf.v4.new_code_cell(r"""from mpl_toolkits.mplot3d import Axes3D

def bloch_vector(sv):
    '''Compute Bloch vector (x,y,z) from a 2-component Statevector.'''
    dm = DensityMatrix(sv).data
    x = 2 * dm[0, 1].real
    y = 2 * dm[0, 1].imag
    z = (dm[0, 0] - dm[1, 1]).real
    return np.array([x, y, z])

fig = plt.figure(figsize=(9, 8))
ax = fig.add_subplot(111, projection="3d")

# Draw sphere
u = np.linspace(0, 2*np.pi, 50)
v = np.linspace(0, np.pi, 50)
xs = np.outer(np.cos(u), np.sin(v))
ys = np.outer(np.sin(u), np.sin(v))
zs = np.outer(np.ones_like(u), np.cos(v))
ax.plot_surface(xs, ys, zs, alpha=0.04, color="steelblue")
ax.plot_wireframe(xs, ys, zs, alpha=0.07, color="navy", linewidth=0.4)

# Draw great circles
for angle in [0, np.pi/2]:
    t = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(t), np.sin(t)*np.cos(angle), np.sin(t)*np.sin(angle),
            "gray", alpha=0.3, lw=0.8)
ax.plot(np.cos(u), np.sin(u), np.zeros_like(u), "gray", alpha=0.3, lw=0.8)

# Axes
for d, lbl in [([0,0,1.4], "|0⟩"), ([0,0,-1.4], "|1⟩"),
               ([1.4,0,0],  "|+⟩"), ([-1.4,0,0], "|−⟩"),
               ([0,1.4,0],  "|i⟩"), ([0,-1.4,0], "|−i⟩")]:
    ax.text(*d, lbl, fontsize=9, ha="center")

# Plot states
palette = ["#2196F3","#F44336","#4CAF50","#FF9800","#9C27B0","#00BCD4"]
for (name, sv), color in zip(states.items(), palette):
    bv = bloch_vector(sv)
    ax.quiver(0,0,0,*bv, arrow_length_ratio=0.12, color=color, lw=2.5, label=name)
    ax.scatter(*bv, s=60, color=color, zorder=5)

ax.set_xlim(-1.5,1.5); ax.set_ylim(-1.5,1.5); ax.set_zlim(-1.5,1.5)
ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
ax.set_title("Bloch Sphere — Six Eigenstates of Pauli Operators\n"
             "$\\hat{X}$ eigenstates: $|\\pm\\rangle$   "
             "$\\hat{Y}$ eigenstates: $|\\pm i\\rangle$   "
             "$\\hat{Z}$ eigenstates: $|0\\rangle,|1\\rangle$", fontsize=11, fontweight="bold")
ax.legend(fontsize=9, loc="upper left")
plt.tight_layout()
plt.savefig("bloch_states.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Pure vs Mixed States — Density Matrix Purity"""))

cells.append(nbf.v4.new_code_cell(r"""# Compare density matrices of pure vs mixed states
import numpy as np

dm_pure = DensityMatrix(ket_plus)   # pure |+⟩
# Mixed state: 50% |0⟩, 50% |1⟩ (classical coin flip — NOT superposition)
dm_mixed = DensityMatrix(0.5 * DensityMatrix(ket_0).data
                         + 0.5 * DensityMatrix(ket_1).data)

def purity(dm):
    return np.trace(dm.data @ dm.data).real

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, dm, title in zip(axes, [dm_pure, dm_mixed],
                          ["Pure State |+⟩\nρ = |+⟩⟨+|",
                           "Mixed State (50% |0⟩ + 50% |1⟩)\nClassical uncertainty — NOT superposition"]):
    mat = np.abs(dm.data)
    im = ax.imshow(mat, cmap="Blues", vmin=0, vmax=0.6)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{dm.data[i,j]:.3f}", ha="center", va="center",
                    fontsize=13, color="black" if mat[i,j] < 0.4 else "white")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["|0⟩", "|1⟩"]); ax.set_yticklabels(["|0⟩", "|1⟩"])
    ax.set_title(f"{title}\nPurity Tr(ρ²) = {purity(dm):.3f}", fontsize=11, fontweight="bold")
    plt.colorbar(im, ax=ax, fraction=0.046)

plt.suptitle("Off-diagonal elements (coherences) are the signature of superposition",
             fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("density_matrix.png", dpi=120, bbox_inches="tight")
plt.show()

print("Key: mixed state has ZERO off-diagonal elements (no quantum coherence)")
print("Decoherence = environment destroying off-diagonal elements (quantum → classical)")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Born Rule Computation

For $|\psi\rangle = \frac{1}{\sqrt{3}}|0\rangle + \sqrt{\frac{2}{3}}|1\rangle$:
1. Verify normalization
2. Compute $P(|0\rangle)$ and $P(|1\rangle)$
3. Simulate the measurement 10000 times and compare empirical vs theoretical
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE
alpha = 1 / np.sqrt(3)
beta  = np.sqrt(2 / 3)

# Verify normalization
norm = None  # YOUR CODE HERE

# Theoretical probabilities
p0_theory = None  # YOUR CODE HERE
p1_theory = None  # YOUR CODE HERE

print(f"Normalization: {norm:.6f}")
print(f"P(|0⟩) theoretical: {p0_theory:.4f}")
print(f"P(|1⟩) theoretical: {p1_theory:.4f}")

# Simulate
qc_ex = QuantumCircuit(1, 1)
# YOUR CODE HERE: initialize to custom state and measure

# YOUR CODE HERE: run simulation and compare
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Density Matrix Purity

Compute the purity of the state after partial decoherence: start with $\rho = |+\rangle\langle+|$ and apply a **dephasing channel** with strength $p = 0.4$:

$$\mathcal{E}(\rho) = (1-p)\rho + p \cdot Z\rho Z^\dagger$$

Plot how purity decreases as $p$ goes from 0 to 1.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — dephasing channel sweep
Z = np.array([[1, 0], [0, -1]])
rho0 = DensityMatrix(ket_plus).data

p_values = np.linspace(0, 1, 100)
purities  = []

for p in p_values:
    rho_noisy = (1 - p) * rho0 + p * (Z @ rho0 @ Z.T.conj())
    purities.append(np.trace(rho_noisy @ rho_noisy).real)

plt.figure(figsize=(8, 4))
plt.plot(p_values, purities, lw=2.5, color="#2196F3")
plt.axhline(0.5, ls="--", color="red", label="Fully mixed state (purity = 0.5)")
plt.axhline(1.0, ls="--", color="green", label="Pure state (purity = 1.0)")
plt.xlabel("Dephasing strength p"); plt.ylabel("Purity Tr(ρ²)")
plt.title("Purity vs Dephasing: Decoherence Destroys Quantum Coherence")
plt.legend(); plt.grid(True, alpha=0.3)
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Implement **quantum state tomography** for a single qubit using only Z-basis measurements.

Process:
1. Prepare $|\psi\rangle = \cos(22.5°)|0\rangle + \sin(22.5°)|1\rangle$
2. Measure in Z, X, and Y bases (apply appropriate rotation before Z-measurement)
3. Reconstruct the density matrix from the three Pauli expectation values $\langle X\rangle, \langle Y\rangle, \langle Z\rangle$:

$$\rho = \frac{1}{2}\big(I + \langle X\rangle \cdot X + \langle Y\rangle \cdot Y + \langle Z\rangle \cdot Z\big)$$

4. Compare reconstructed $\rho$ to the true $|\psi\rangle\langle\psi|$
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Quantum State Tomography
# YOUR CODE HERE

theta = np.radians(45)  # 22.5° in Bloch sphere parametrization
alpha = np.cos(theta / 2)
beta  = np.sin(theta / 2)

print(f"Target state: {alpha:.4f}|0⟩ + {beta:.4f}|1⟩")

# Prepare the state
# YOUR CODE HERE: use qc.initialize([alpha, beta], 0)

# Measure in Z, X, Y bases
# YOUR CODE HERE

# Reconstruct density matrix
# YOUR CODE HERE

# Compare to truth
# YOUR CODE HERE
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Nielsen & Chuang**, Chapter 2 — Density matrices and quantum operations (the definitive reference)
2. **Qiskit Docs: Quantum Circuit** — [https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.QuantumCircuit](https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.QuantumCircuit)
3. **Preskill Notes Ch. 2** — Measurement theory and POVM formalism
4. **Wilde — Quantum Information Theory**, Ch. 3 — Density operators
5. **Bloch sphere visualization** — Use `plot_bloch_multivector` in Qiskit's visualization module
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "F3_qubits_states_measurement.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
