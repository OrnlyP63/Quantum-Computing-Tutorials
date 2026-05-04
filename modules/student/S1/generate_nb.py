#!/usr/bin/env python3
"""generate_nb.py — Module S1: Bits, Qubits & Superposition"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# S1 — Bits, Qubits & Superposition
**Track:** Student | **Difficulty:** ⭐⭐☆☆☆ | **Est. Time:** 20 min

| | |
|---|---|
| **Prerequisites** | F1–F4; basic algebra |
| **Qiskit Modules** | `qiskit`, `qiskit_aer`, `qiskit.quantum_info` |
| **Companion Video** | Student Module S1 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Initialize a qubit in $|0\rangle$ and $|1\rangle$ and verify using `Statevector`
2. Apply the **Hadamard gate** and observe the resulting superposition
3. Explain why the measurement outcome is **random** (but the state is not)
4. Run 1000 measurements and interpret the resulting **probability histogram**
5. Distinguish between "superposition" (structured) and "randomness" (unstructured)
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Concept Summary

### Classical Bit vs Qubit

A classical bit stores either 0 or 1. A qubit stores a **superposition**:

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$$

where $\alpha$ and $\beta$ are **complex amplitudes** satisfying $|\alpha|^2 + |\beta|^2 = 1$.

### The Hadamard Gate

The most important single-qubit gate — it creates **equal superposition**:

$$H = \frac{1}{\sqrt{2}}\begin{pmatrix}1 & 1\\ 1 & -1\end{pmatrix}$$

$$H|0\rangle = \frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle$$

$$H|1\rangle = \frac{1}{\sqrt{2}}|0\rangle - \frac{1}{\sqrt{2}}|1\rangle$$

> **Analogy:** A coin spinning in the air is neither heads nor tails — it is in superposition. The moment it lands (measurement), it becomes one or the other with definite probabilities.

### Why Superposition Is Not Just Randomness

A truly random coin flip is **classically uncertain** — we just don't know which side. A qubit in superposition is **quantum coherent** — both outcomes coexist, and they can *interfere* with each other. The coin analogy breaks down here: two superpositions can cancel each other out (destructive interference), which a classical random variable cannot do.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 1 — Initialize and Inspect Qubit States"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# |0⟩ — computational basis ground state
qc0 = QuantumCircuit(1)
sv0 = Statevector(qc0)
print(f"|0⟩ statevector: {sv0.data}")
print(f"  P(0) = {abs(sv0.data[0])**2:.3f},  P(1) = {abs(sv0.data[1])**2:.3f}")

# |1⟩ — apply X (bit flip) gate
qc1 = QuantumCircuit(1)
qc1.x(0)
sv1 = Statevector(qc1)
print(f"\n|1⟩ statevector (after X): {sv1.data}")
print(f"  P(0) = {abs(sv1.data[0])**2:.3f},  P(1) = {abs(sv1.data[1])**2:.3f}")

# |+⟩ — apply H gate: superposition
qc_plus = QuantumCircuit(1)
qc_plus.h(0)
sv_plus = Statevector(qc_plus)
print(f"\n|+⟩ statevector (after H): {sv_plus.data}")
print(f"  P(0) = {abs(sv_plus.data[0])**2:.3f},  P(1) = {abs(sv_plus.data[1])**2:.3f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 2 — Visualize States on the Bloch Sphere"""))

cells.append(nbf.v4.new_code_cell(r"""from mpl_toolkits.mplot3d import Axes3D
from qiskit.quantum_info import DensityMatrix

def bloch_vec(sv):
    dm = DensityMatrix(sv).data
    return np.array([2*dm[0,1].real, 2*dm[0,1].imag, (dm[0,0]-dm[1,1]).real])

def draw_bloch(ax, title):
    u = np.linspace(0, 2*np.pi, 40)
    v = np.linspace(0, np.pi, 40)
    ax.plot_surface(np.outer(np.cos(u), np.sin(v)),
                    np.outer(np.sin(u), np.sin(v)),
                    np.outer(np.ones(40), np.cos(v)),
                    alpha=0.05, color="steelblue")
    ax.plot_wireframe(np.outer(np.cos(u), np.sin(v)),
                      np.outer(np.sin(u), np.sin(v)),
                      np.outer(np.ones(40), np.cos(v)),
                      alpha=0.07, color="navy", lw=0.4)
    for (d, l) in [([0,0,1.3],"|0⟩"), ([0,0,-1.3],"|1⟩"),
                   ([1.3,0,0],"|+⟩"), ([-1.3,0,0],"|−⟩")]:
        ax.text(*d, l, fontsize=8, ha="center")
    ax.set_xlim(-1.4,1.4); ax.set_ylim(-1.4,1.4); ax.set_zlim(-1.4,1.4)
    ax.set_title(title, fontsize=10, fontweight="bold")

fig = plt.figure(figsize=(15, 5))
for i, (sv, title, color) in enumerate([
        (sv0,    "|0⟩  (north pole)",   "blue"),
        (sv1,    "|1⟩  (south pole)",   "red"),
        (sv_plus,"|+⟩  (equator, east)","green"),
]):
    ax = fig.add_subplot(1, 3, i+1, projection="3d")
    draw_bloch(ax, title)
    bv = bloch_vec(sv)
    ax.quiver(0,0,0,*bv, arrow_length_ratio=0.12, color=color, lw=3)
    ax.scatter(*bv, s=80, color=color, zorder=5)

plt.suptitle("Three Key Qubit States on the Bloch Sphere", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("bloch_S1.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 3 — Measure the Superposition: The Coin Landing"""))

cells.append(nbf.v4.new_code_cell(r"""from qiskit_aer import AerSimulator
from qiskit import transpile

sim = AerSimulator()

# Apply H then measure
qc_measure = QuantumCircuit(1, 1)
qc_measure.h(0)
qc_measure.measure(0, 0)

print("Circuit:")
print(qc_measure.draw(output="text"))

# Run with increasing shot counts
shot_list = [10, 100, 1000, 10000]
fig, axes = plt.subplots(1, 4, figsize=(16, 4))

for ax, shots in zip(axes, shot_list):
    job = sim.run(transpile(qc_measure, sim), shots=shots)
    counts = job.result().get_counts()
    labels = ["0", "1"]
    vals = [counts.get(l, 0) for l in labels]
    bars = ax.bar(labels, vals, color=["#2196F3", "#FF5722"], edgecolor="black", width=0.5)
    for bar in bars:
        pct = bar.get_height() / shots * 100
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + shots*0.01,
                f"{pct:.1f}%", ha="center", fontsize=11)
    ax.set_title(f"{shots:,} shots", fontsize=12, fontweight="bold")
    ax.set_ylabel("Count"); ax.set_ylim(0, shots * 0.7)
    ax.axhline(shots / 2, ls="--", color="gray", lw=1, label="50%")

plt.suptitle("H|0⟩ Measured: Convergence to 50/50 as Shots Increase\n"
             "More shots → closer to the theoretical prediction",
             fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("superposition_convergence.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 4 — Superposition vs Classical Randomness"""))

cells.append(nbf.v4.new_code_cell(r"""# Demonstrate: quantum superposition and classical randomness have the SAME statistics
# but DIFFERENT physics (interference distinguishes them)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
n_shots = 5000

# Classical random coin
np.random.seed(42)
classical = np.random.choice([0, 1], size=n_shots)
c_counts = {0: np.sum(classical == 0), 1: np.sum(classical == 1)}

# Quantum superposition
qc_q = QuantumCircuit(1, 1)
qc_q.h(0)
qc_q.measure(0, 0)
job = sim.run(transpile(qc_q, sim), shots=n_shots)
q_counts = job.result().get_counts()
q_vals   = {0: q_counts.get("0", 0), 1: q_counts.get("1", 0)}

for ax, vals, title, color in [
    (axes[0], c_counts, "Classical Random Coin Flip\n(statistical uncertainty)",  "#FF9800"),
    (axes[1], q_vals,   "Quantum Superposition H|0⟩\n(quantum coherence + Born rule)", "#4CAF50"),
]:
    keys = sorted(vals.keys())
    bars = ax.bar([str(k) for k in keys], [vals[k] for k in keys],
                  color=color, edgecolor="black", width=0.5)
    for bar in bars:
        pct = bar.get_height() / n_shots * 100
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f"{pct:.1f}%", ha="center", fontsize=13)
    ax.set_xlabel("Outcome"); ax.set_ylabel("Count")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_ylim(0, n_shots * 0.7)

plt.suptitle("Statistics look identical — the difference is PHYSICAL (interference ability)\n"
             "Apply H twice to a superposition: deterministic. Apply H twice to classical random: still random.",
             fontsize=11, fontweight="bold")
plt.tight_layout()
plt.savefig("quantum_vs_classical_random.png", dpi=120, bbox_inches="tight")
plt.show()

# Prove it: H applied TWICE to a quantum state returns to |0⟩
qc_hh = QuantumCircuit(1, 1)
qc_hh.h(0)   # |0⟩ → |+⟩
qc_hh.h(0)   # |+⟩ → |0⟩ (reversible!)
qc_hh.measure(0, 0)
job2 = sim.run(transpile(qc_hh, sim), shots=n_shots)
counts2 = job2.result().get_counts()
print("H applied twice (H²|0⟩ = |0⟩):", counts2)
print("→ Quantum is reversible and coherent. Classical randomness is not.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Predict and Verify

For each starting state and gate below, **predict** the probability of measuring 0 and 1, then verify by simulation.

| Initial State | Gate | P(0) predicted | P(1) predicted |
|---|---|---|---|
| $\|0\rangle$ | None | ? | ? |
| $\|1\rangle$ | None | ? | ? |
| $\|0\rangle$ | H | ? | ? |
| $\|1\rangle$ | H | ? | ? |
| $\|0\rangle$ | X then H | ? | ? |
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — fill in predictions then simulate each

experiments = [
    ("no gate",    lambda qc: None),
    ("X gate",     lambda qc: qc.x(0)),
    ("H gate",     lambda qc: qc.h(0)),
    ("X then H",   lambda qc: (qc.x(0), qc.h(0))),
    ("H then X",   lambda qc: (qc.h(0), qc.x(0))),
]

print(f"{'Experiment':15s} {'P(0)':>8s} {'P(1)':>8s}")
print("-" * 35)
for name, gate_fn in experiments:
    qc = QuantumCircuit(1, 1)
    gate_fn(qc)
    qc.measure(0, 0)
    job = sim.run(transpile(qc, sim), shots=4096)
    counts = job.result().get_counts()
    total = sum(counts.values())
    p0 = counts.get("0", 0) / total
    p1 = counts.get("1", 0) / total
    print(f"{name:15s} {p0:>8.3f} {p1:>8.3f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Custom Superposition

Create a state with $P(|0\rangle) = 0.75$ and $P(|1\rangle) = 0.25$ using the **rotation gate** $R_y(\theta)$:

$$R_y(\theta) = \begin{pmatrix}\cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2)\end{pmatrix}$$

Find $\theta$ such that $\cos^2(\theta/2) = 0.75$.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE
# Step 1: compute the required theta
target_p0 = 0.75
theta = None  # YOUR CODE HERE: theta = 2 * arccos(sqrt(target_p0))

print(f"Required Ry angle: {theta:.4f} radians = {np.degrees(theta):.2f}°")

# Step 2: build the circuit
qc_ry = QuantumCircuit(1, 1)
# YOUR CODE HERE: qc_ry.ry(theta, 0)
qc_ry.measure(0, 0)

# Step 3: simulate and verify
job = sim.run(transpile(qc_ry, sim), shots=8192)
counts = job.result().get_counts()
p0_measured = counts.get("0", 0) / 8192
p1_measured = counts.get("1", 0) / 8192
print(f"P(0) target: {target_p0:.3f}, measured: {p0_measured:.3f}")
print(f"P(1) target: {1-target_p0:.3f}, measured: {p1_measured:.3f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Create a visual demonstration of the **double-slit thought experiment** using quantum circuits:

1. Prepare 3 paths: $|0\rangle$, $|+\rangle = H|0\rangle$, $|-\rangle = HX|0\rangle$
2. For each, apply H again, then measure
3. Show that:
   - $H(H|0\rangle) = |0\rangle$ → **always 0** (constructive interference)
   - $H(H|1\rangle) = |1\rangle$ → **always 1** (constructive interference)
4. Plot a bar chart that illustrates constructive vs destructive interference
5. Write a 2-sentence explanation of how this relates to the double-slit experiment

This is the core idea behind ALL quantum algorithms.
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Double slit analogy via quantum interference
# YOUR CODE HERE
circuits_labels = [
    ("H then H on |0⟩", lambda qc: (qc.h(0), qc.h(0))),
    ("H then H on |1⟩", lambda qc: (qc.x(0), qc.h(0), qc.h(0))),
    ("X then H on |0⟩", lambda qc: (qc.x(0), qc.h(0))),
]

print("Interference effects in H²|ψ⟩:")
for label, gate_fn in circuits_labels:
    qc = QuantumCircuit(1, 1)
    gate_fn(qc)
    qc.measure(0, 0)
    # YOUR CODE HERE: simulate and print
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Qiskit Textbook** — [https://learning.quantum.ibm.com](https://learning.quantum.ibm.com) — "Quantum States and Qubits"
2. **Nielsen & Chuang**, Section 1.2 — Quantum bits (accessible introduction)
3. **Scott Aaronson** — "Quantum Computing Since Democritus" — Lecture 9
4. **IBM Research** — "What is superposition?" video series
5. **Qiskit Docs: Statevector** — [https://docs.quantum.ibm.com/api/qiskit/qiskit.quantum_info.Statevector](https://docs.quantum.ibm.com/api/qiskit/qiskit.quantum_info.Statevector)
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "S1_bits_qubits_superposition.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
