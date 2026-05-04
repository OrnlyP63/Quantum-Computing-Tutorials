#!/usr/bin/env python3
"""generate_nb.py — Module S3: Entanglement — Qubits That Share a Secret"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# S3 — Entanglement: Qubits That Share a Secret
**Track:** Student | **Difficulty:** ⭐⭐☆☆☆ | **Est. Time:** 20 min

| | |
|---|---|
| **Prerequisites** | F1–F4, S1, S2 |
| **Qiskit Modules** | `qiskit`, `qiskit_aer`, `qiskit.quantum_info` |
| **Companion Video** | Student Module S3 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Build a **Bell state** using H + CNOT and verify its entanglement
2. Show that entangled qubit outcomes are **perfectly correlated**
3. Prove entanglement by demonstrating that the state **cannot** be written as a product
4. Run 1000 shots and observe that only $|00\rangle$ and $|11\rangle$ outcomes appear
5. Connect entanglement to real-world applications (quantum cryptography, teleportation)
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Concept Summary

### The CNOT Gate

The **controlled-NOT** is the fundamental 2-qubit gate:

$$\text{CNOT} = \begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&0&1\\0&0&1&0\end{pmatrix}$$

It flips the **target** qubit ($q_1$) if and only if the **control** qubit ($q_0$) is $|1\rangle$.

### Bell States

Applying H to $q_0$ then CNOT creates a **Bell state** — the maximally entangled 2-qubit state:

$$|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$$

The four Bell states form a complete orthonormal basis:

| State | Formula |
|---|---|
| $\|\Phi^+\rangle$ | $\frac{1}{\sqrt{2}}(\|00\rangle + \|11\rangle)$ |
| $\|\Phi^-\rangle$ | $\frac{1}{\sqrt{2}}(\|00\rangle - \|11\rangle)$ |
| $\|\Psi^+\rangle$ | $\frac{1}{\sqrt{2}}(\|01\rangle + \|10\rangle)$ |
| $\|\Psi^-\rangle$ | $\frac{1}{\sqrt{2}}(\|01\rangle - \|10\rangle)$ |

### Why Entanglement Cannot Be Classical

$|\Phi^+\rangle$ **cannot** be written as $|\psi_A\rangle \otimes |\psi_B\rangle$ for any single-qubit states $|\psi_A\rangle, |\psi_B\rangle$. This is what makes it non-classical — the state of each qubit individually is maximally uncertain, yet together they are perfectly correlated.

> **Analogy:** Magic dice — you and a friend each take one die from a pair. No matter how far apart you are, whenever you roll your die, your friend's die always shows the same number. Classical dice can't do this without pre-coordination.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Build the Bell State"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace

# Build |Φ+⟩ = (|00⟩ + |11⟩)/√2
qc_bell = QuantumCircuit(2, 2, name="Bell State |Φ+⟩")
qc_bell.h(0)      # |00⟩ → (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00⟩+|10⟩)/√2
qc_bell.cx(0, 1)  # CNOT: |00⟩→|00⟩, |10⟩→|11⟩  → (|00⟩+|11⟩)/√2

print("Bell State Circuit:")
print(qc_bell.draw(output="text"))

# Inspect the statevector
sv = Statevector(qc_bell)
print(f"\nStatevector amplitudes:")
basis = ["|00⟩", "|01⟩", "|10⟩", "|11⟩"]
for b, amp in zip(basis, sv.data):
    print(f"  {b}: {amp:.4f}  → P = {abs(amp)**2:.4f}")

print(f"\nNormalization: {sum(abs(a)**2 for a in sv.data):.6f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Prove Entanglement: The Partial Trace Test"""))

cells.append(nbf.v4.new_code_cell(r"""from qiskit.quantum_info import DensityMatrix, partial_trace

# Full 2-qubit density matrix
dm_full = DensityMatrix(qc_bell)
print("Full 2-qubit density matrix (|Φ+⟩⟨Φ+|):")
print(np.round(dm_full.data, 3))
print(f"Purity: {np.trace(dm_full.data @ dm_full.data).real:.4f}  (= 1 for pure state)")

# Reduced density matrix of qubit 0 (trace out qubit 1)
dm_A = partial_trace(dm_full, [1])
print("\nReduced density matrix of qubit A (after tracing out qubit B):")
print(np.round(dm_A.data, 3))
purity_A = np.trace(dm_A.data @ dm_A.data).real
print(f"Purity of qubit A alone: {purity_A:.4f}  (= 0.5 → maximally MIXED)")

print("\n→ Each qubit individually is in a completely mixed state (50/50 uncertainty)")
print("→ But together they are in a PURE state — perfectly correlated")
print("→ This is the signature of entanglement: subsystem purity < 1")

# Compare with a separable (product) state
qc_sep = QuantumCircuit(2)
qc_sep.h(0)  # |+⟩|0⟩ — product state, NOT entangled
dm_sep = DensityMatrix(qc_sep)
dm_sep_A = partial_trace(dm_sep, [1])
print(f"\nFor product state |+⟩|0⟩ — qubit A purity: {np.trace(dm_sep_A.data @ dm_sep_A.data).real:.4f}  (= 1 → pure)")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Measure the Bell State — Perfect Correlations"""))

cells.append(nbf.v4.new_code_cell(r"""from qiskit_aer import AerSimulator
from qiskit import transpile

sim = AerSimulator()

# Measure the Bell state
qc_meas = QuantumCircuit(2, 2)
qc_meas.h(0)
qc_meas.cx(0, 1)
qc_meas.measure([0, 1], [0, 1])

job = sim.run(transpile(qc_meas, sim), shots=4096)
counts = job.result().get_counts()

print("Measurement counts:", counts)

# Visualize
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Histogram of all outcomes
ax = axes[0]
all_outcomes = ["00", "01", "10", "11"]
vals = [counts.get(o, 0) for o in all_outcomes]
colors = ["#4CAF50" if o in ["00","11"] else "#FFCDD2" for o in all_outcomes]
bars = ax.bar(all_outcomes, vals, color=colors, edgecolor="black", width=0.5)
for bar in bars:
    pct = bar.get_height() / 4096 * 100
    if bar.get_height() > 0:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                f"{pct:.1f}%", ha="center", fontsize=12)
ax.set_title("Bell State Measurements\n4096 shots", fontsize=12, fontweight="bold")
ax.set_ylabel("Count"); ax.set_ylim(0, 3000)
ax.text(1.5, 2500, "01 and 10 NEVER\nappear — perfect\ncorrelation!",
        ha="center", fontsize=10, color="red",
        bbox=dict(boxstyle="round", facecolor="#FFCDD2"))

# Qubit A vs Qubit B correlation
ax2 = axes[1]
n_samples = 500
np.random.seed(42)
outcomes_A = np.random.choice([0, 1], size=n_samples, p=[0.5, 0.5])
outcomes_B = outcomes_A  # perfect correlation in |Φ+⟩
jitter = np.random.normal(0, 0.07, n_samples)
ax2.scatter(outcomes_A + jitter, outcomes_B + jitter,
            alpha=0.3, s=15, color="#9C27B0")
ax2.set_xticks([0,1]); ax2.set_yticks([0,1])
ax2.set_xticklabels(["0","1"]); ax2.set_yticklabels(["0","1"])
ax2.set_xlabel("Qubit A"); ax2.set_ylabel("Qubit B")
ax2.set_title("Perfect Correlation: When A=0, B=0\nWhen A=1, B=1", fontsize=11, fontweight="bold")
corr = np.corrcoef(outcomes_A, outcomes_B)[0,1]
ax2.text(0.5, 0.05, f"Pearson r = {corr:.3f}",
         transform=ax2.transAxes, ha="center", fontsize=12, color="purple",
         bbox=dict(boxstyle="round", facecolor="#F3E5F5"))

# Compare all four Bell states
ax3 = axes[2]
bell_circuits = {
    "|Φ+⟩": ([], []),          # H+CNOT
    "|Φ-⟩": ([("z",0)], []),    # Z on qubit 0 after
    "|Ψ+⟩": ([("x",1)], []),    # X on qubit 1
    "|Ψ-⟩": ([("x",1),("z",0)], []),
}

bell_names = list(bell_circuits.keys())
dominant_outcomes = []
for name, (pre_gates, _) in bell_circuits.items():
    qc_b = QuantumCircuit(2, 2)
    qc_b.h(0); qc_b.cx(0, 1)
    for gate, qubit in pre_gates:
        getattr(qc_b, gate)(qubit)
    qc_b.measure([0,1],[0,1])
    j = sim.run(transpile(qc_b, sim), shots=2048)
    c = j.result().get_counts()
    # Which outcomes dominate?
    dominant = max(c, key=c.get)
    dominant_outcomes.append(c.get(dominant, 0)/2048*100)
    print(f"{name}: {c}")

ax3.bar(bell_names, dominant_outcomes, color=["#2196F3","#F44336","#4CAF50","#FF9800"],
        edgecolor="black", width=0.5)
ax3.set_ylabel("Dominant outcome probability (%)"); ax3.set_ylim(0, 100)
ax3.set_title("All Four Bell States — Dominant Outcome %\n(each should be ~50%)", fontsize=11, fontweight="bold")

plt.suptitle("Entanglement: Perfect Correlations Without Classical Communication",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("bell_state.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Build All Four Bell States

The four Bell states are created by adding X and/or Z gates to the basic H+CNOT circuit. Build each one and verify by inspecting the statevector.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — build |Φ-⟩, |Ψ+⟩, |Ψ-⟩

bell_states = {
    "|Φ+⟩": [],                          # H then CNOT — already done
    "|Φ-⟩": [("z", 0)],                  # Z on qubit 0 before CNOT
    "|Ψ+⟩": [("x", 1)],                  # X on qubit 1 before CNOT
    "|Ψ-⟩": [("x", 1), ("z", 0)],        # X on q1, Z on q0
}

basis = ["|00⟩", "|01⟩", "|10⟩", "|11⟩"]
for name, pre_gates in bell_states.items():
    qc = QuantumCircuit(2)
    for gate, qubit in pre_gates:
        getattr(qc, gate)(qubit)
    qc.h(0)
    qc.cx(0, 1)
    sv = Statevector(qc)
    amps = " ".join(f"{a:+.3f}" for a in np.round(sv.data, 3))
    print(f"{name}: [{amps}]")
    # YOUR CODE HERE: verify the correct basis states are populated
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — CNOT Truth Table

Verify the CNOT gate truth table manually:

| Control | Target | Output Control | Output Target |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0 | 1 | 0 | 1 |
| 1 | 0 | 1 | 1 |
| 1 | 1 | 1 | 0 |
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — verify CNOT truth table
inputs = [(0,0), (0,1), (1,0), (1,1)]
print(f"{'Input':10s} {'Output':10s}")
print("-" * 25)
for ctrl, tgt in inputs:
    qc = QuantumCircuit(2, 2)
    if ctrl == 1: qc.x(0)
    if tgt  == 1: qc.x(1)
    qc.cx(0, 1)  # CNOT: control=q0, target=q1
    qc.measure([0, 1], [0, 1])
    job = sim.run(transpile(qc, sim), shots=100)
    result_state = max(job.result().get_counts(), key=job.result().get_counts().get)
    print(f"({ctrl},{tgt})      →    {result_state}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Implement a **quantum teleportation protocol** using the Bell state you've just learned.

Teleportation sends an unknown qubit state from Alice to Bob using:
1. A shared Bell pair
2. Two classical bits

Steps:
1. Prepare an unknown qubit $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ (Alice's qubit)
2. Create a Bell pair between Alice's second qubit and Bob's qubit
3. Alice performs a Bell measurement on her two qubits
4. Bob applies corrections based on Alice's 2 classical bits
5. Verify Bob's qubit matches the original state

This requires a 3-qubit circuit and classical conditioning (`if_test` in Qiskit 1.x).
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Quantum Teleportation
# YOUR CODE HERE

# Step 1: Alice's mystery qubit
alpha = 1/np.sqrt(3); beta = np.sqrt(2/3)
print(f"State to teleport: {alpha:.4f}|0⟩ + {beta:.4f}|1⟩")

# Step 2: Build the teleportation circuit
# q[0] = Alice's state to teleport
# q[1] = Alice's half of Bell pair
# q[2] = Bob's half of Bell pair
qc_tel = QuantumCircuit(3, 2)

# Initialize Alice's qubit to |ψ⟩
qc_tel.initialize([alpha, beta], 0)

# YOUR CODE HERE: create Bell pair on q[1] and q[2]
# YOUR CODE HERE: Alice's Bell measurement on q[0] and q[1]
# YOUR CODE HERE: classical corrections on q[2]

# Verify Bob's state
# YOUR CODE HERE
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Bell's 1964 paper** — "On the Einstein-Podolsky-Rosen paradox" (free on CERN Document Server)
2. **Qiskit Textbook** — "Entangled States" section
3. **Nielsen & Chuang**, Section 1.3 — Quantum entanglement
4. **Aspect experiment (1982)** — First experimental Bell inequality violation
5. **Quantum cryptography (BB84)** — Uses entanglement for provably secure communication
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "S3_entanglement.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
