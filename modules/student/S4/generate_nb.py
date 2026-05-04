#!/usr/bin/env python3
"""generate_nb.py — Module S4: Your First Quantum Circuit"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# S4 — Your First Quantum Circuit
**Track:** Student | **Difficulty:** ⭐⭐⭐☆☆ | **Est. Time:** 30 min

| | |
|---|---|
| **Prerequisites** | F1–F4, S1–S3 |
| **Qiskit Modules** | `qiskit`, `qiskit_aer`, `qiskit.visualization` |
| **Companion Video** | Student Module S4 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Build a **3-qubit circuit** from scratch using multiple gate types
2. Read and interpret a Qiskit **circuit diagram** left-to-right
3. Predict measurement outcomes **before running** and verify the predictions
4. Modify a circuit and observe how output distributions change
5. Understand circuits as ordered sequences of operations on a register
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Concept Summary

### Circuit Anatomy

A quantum circuit consists of:
- **Quantum register:** $n$ qubits, initialized to $|0\rangle^{\otimes n}$
- **Gates:** Unitary operations applied to one or more qubits, read **left to right**
- **Classical register:** $m$ bits that store measurement results
- **Barriers:** Visual separators (no physical effect)

### The Recipe Analogy

A circuit is like a recipe:
- **Ingredients** = qubits (each starts fresh as $|0\rangle$)
- **Steps** = gates (applied in sequence, left to right)
- **Dish** = final quantum state → measured to get classical results

### GHZ State — 3-Qubit Entanglement

The **Greenberger–Horne–Zeilinger (GHZ) state** is the 3-qubit generalization of the Bell state:

$$|\text{GHZ}\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$$

Created by: H on $q_0$, then CNOT($q_0 \to q_1$), then CNOT($q_1 \to q_2$).

All three qubits are correlated: measuring any one qubit determines the other two.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 1 — Build and Draw a 3-Qubit Circuit"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

# Build a 3-qubit circuit step by step
qc = QuantumCircuit(3, 3, name="GHZ State")

# Step 1: Create superposition on qubit 0
qc.h(0)
qc.barrier()  # visual separator

# Step 2: Spread entanglement with CNOT gates
qc.cx(0, 1)
qc.cx(1, 2)
qc.barrier()

# Step 3: Measure all qubits
qc.measure([0, 1, 2], [0, 1, 2])

print("3-Qubit GHZ Circuit:")
print(qc.draw(output="text"))
print(f"\nCircuit depth: {qc.depth()}")
print(f"Gate count: {qc.count_ops()}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 2 — Predict Before Running

**Think first:** What outcomes do you expect from the GHZ state?

The GHZ state is $\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$. After measurement:
- $P(000) = 0.5$
- $P(111) = 0.5$
- All other outcomes: 0

Now run and verify.
"""))

cells.append(nbf.v4.new_code_cell(r"""sim = AerSimulator()

# ---- PREDICT ----
print("PREDICTION:")
print("  P(000) ≈ 0.50")
print("  P(111) ≈ 0.50")
print("  P(001), P(010), ... ≈ 0.00")
print()

# ---- RUN ----
job = sim.run(transpile(qc, sim), shots=4096)
counts = job.result().get_counts()
total = sum(counts.values())

print("ACTUAL RESULTS:")
all_outcomes = [f"{i:03b}" for i in range(8)]
for o in all_outcomes:
    count = counts.get(o, 0)
    pct   = count / total * 100
    bar   = "█" * int(pct / 2)
    marker = " ← EXPECTED" if o in ["000", "111"] else ""
    print(f"  {o}: {count:5d} ({pct:5.1f}%) {bar}{marker}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 3 — Visualize the Results"""))

cells.append(nbf.v4.new_code_cell(r"""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram
ax = axes[0]
all_outcomes = [f"{i:03b}" for i in range(8)]
vals = [counts.get(o, 0) for o in all_outcomes]
colors = ["#4CAF50" if o in ["000","111"] else "#FFCDD2" for o in all_outcomes]
bars = ax.bar(all_outcomes, vals, color=colors, edgecolor="black", width=0.6)
for bar in bars:
    if bar.get_height() > 10:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                f"{bar.get_height()/total*100:.1f}%", ha="center", fontsize=11)
ax.set_xlabel("Measurement Outcome (q₂q₁q₀)"); ax.set_ylabel("Count")
ax.set_title("GHZ State: Only |000⟩ and |111⟩\nare Possible Outcomes", fontsize=12, fontweight="bold")
ax.set_ylim(0, total * 0.7)

# Circuit contribution diagram
ax2 = axes[1]
ax2.axis("off")
circuit_steps = [
    ("Initial", "|000⟩", "#E3F2FD"),
    ("After H(q₀)", r"$\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$", "#E8F5E9"),
    ("After CNOT(q₀→q₁)", r"$\frac{1}{\sqrt{2}}(|000\rangle + |110\rangle)$", "#FFF9C4"),
    ("After CNOT(q₁→q₂)", r"$\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$", "#FCE4EC"),
    ("Measured", "P(000)=0.5, P(111)=0.5", "#F3E5F5"),
]
for i, (step, state, color) in enumerate(circuit_steps):
    y = 0.85 - i * 0.17
    rect = plt.Rectangle((0.02, y-0.07), 0.95, 0.13, transform=ax2.transAxes,
                          facecolor=color, edgecolor="gray", linewidth=1)
    ax2.add_patch(rect)
    ax2.text(0.08, y, step + ":", transform=ax2.transAxes,
             fontsize=10, fontweight="bold", va="center")
    ax2.text(0.38, y, state, transform=ax2.transAxes,
             fontsize=10, va="center")
    if i < len(circuit_steps) - 1:
        ax2.annotate("", xy=(0.5, y - 0.04), xytext=(0.5, y - 0.07),
                     xycoords="axes fraction", textcoords="axes fraction",
                     arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
ax2.set_title("State Evolution Through GHZ Circuit", fontsize=12, fontweight="bold")

plt.suptitle("First 3-Qubit Circuit: GHZ State", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("ghz_circuit.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 4 — Modify and Observe Changes"""))

cells.append(nbf.v4.new_code_cell(r"""# Experiment: add gates after the GHZ state is created
# What happens if we apply X to qubit 1 before measuring?

modifications = {
    "Original GHZ":       [],
    "After X(q₀)":        [("x", 0)],
    "After Z(q₀)":        [("z", 0)],
    "After H(q₀)H(q₁)H(q₂)": [("h",0),("h",1),("h",2)],  # measure in X basis
}

fig, axes = plt.subplots(1, len(modifications), figsize=(18, 4))

for ax, (mod_name, extra_gates) in zip(axes, modifications.items()):
    qc_mod = QuantumCircuit(3, 3)
    qc_mod.h(0); qc_mod.cx(0,1); qc_mod.cx(1,2)
    for gate, qubit in extra_gates:
        getattr(qc_mod, gate)(qubit)
    qc_mod.measure([0,1,2],[0,1,2])

    job = sim.run(transpile(qc_mod, sim), shots=4096)
    counts_m = job.result().get_counts()
    total_m  = sum(counts_m.values())

    all_out = [f"{i:03b}" for i in range(8)]
    vals = [counts_m.get(o, 0)/total_m for o in all_out]
    colors = [f"#{int(v*200):02x}90{int((1-v)*200):02x}" for v in vals]
    ax.bar(all_out, vals, color=colors, edgecolor="black", width=0.6)
    ax.set_title(mod_name, fontsize=10, fontweight="bold")
    ax.set_xlabel("Outcome"); ax.set_ylabel("Probability")
    ax.set_ylim(0, 0.6); ax.tick_params(axis='x', rotation=45)

plt.suptitle("Modifying the GHZ Circuit: How Gate Choices Shape Outcomes",
             fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("ghz_modifications.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Predict and Run

For each circuit below, **write your prediction** in the comments, then run and check.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — predict then verify

circuits_to_predict = [
    ("H all qubits",    lambda qc: (qc.h(0), qc.h(1), qc.h(2))),
    ("H(0), CNOT(0,1), CNOT(0,2)", lambda qc: (qc.h(0), qc.cx(0,1), qc.cx(0,2))),
    ("X all, H all",   lambda qc: (qc.x(0), qc.x(1), qc.x(2), qc.h(0), qc.h(1), qc.h(2))),
]

for name, gate_fn in circuits_to_predict:
    qc = QuantumCircuit(3, 3)
    gate_fn(qc)
    sv = Statevector(qc)
    qc.measure([0,1,2],[0,1,2])
    job = sim.run(transpile(qc, sim), shots=4096)
    counts_t = job.result().get_counts()

    # YOUR CODE HERE: print top 4 outcomes and their probabilities
    top4 = sorted(counts_t.items(), key=lambda x: -x[1])[:4]
    print(f"\n{name}:")
    for outcome, count in top4:
        print(f"  {outcome}: {count/4096:.3f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Circuit Reading

Read this circuit description and draw it, then simulate it:

```
q0: ─H─────●─────────────M
            │
q1: ───X───X─────H───────M

q2: ─────────────────────M
```

What state does this circuit prepare?
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — build and simulate the circuit above
qc_ex = QuantumCircuit(3, 3)
# YOUR CODE HERE: add gates as described above
# ...
qc_ex.measure([0,1,2],[0,1,2])

# YOUR CODE HERE: run and print results
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Implement the **quantum Fourier transform (QFT)** for 3 qubits — a key subroutine in Shor's factoring algorithm.

The 3-qubit QFT circuit:
1. H on $q_0$, then controlled-$S$ ($q_1 \to q_0$), then controlled-$T$ ($q_2 \to q_0$)
2. H on $q_1$, then controlled-$S$ ($q_2 \to q_1$)
3. H on $q_2$
4. Swap $q_0$ and $q_2$

After constructing the QFT:
1. Apply QFT to $|000\rangle$ — what's the output state?
2. Apply QFT to $|100\rangle$ — verify it equals a uniform superposition with increasing phases
3. Show that QFT is its own inverse when reversed
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Quantum Fourier Transform (QFT)
# YOUR CODE HERE

def build_qft_3():
    qc = QuantumCircuit(3, name="QFT-3")
    # YOUR CODE HERE
    # q0
    qc.h(0)
    # controlled-S (Rz(pi/2)) from q1 to q0
    # controlled-T (Rz(pi/4)) from q2 to q0
    # q1
    # q2
    # swap q0 and q2
    return qc

qft = build_qft_3()
print("QFT Circuit:")
print(qft.draw(output="text"))

# Apply to |000⟩
sv = Statevector(qft)
print("\nQFT|000⟩ amplitudes:")
basis = [f"|{i:03b}⟩" for i in range(8)]
for b, amp in zip(basis, sv.data):
    print(f"  {b}: {amp:.4f}  mag={abs(amp):.4f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Qiskit Textbook** — "Quantum Circuits" chapter with interactive examples
2. **IBM Circuit Composer** — Drag-and-drop circuit builder at quantum.ibm.com
3. **Nielsen & Chuang**, Chapter 4 — Quantum circuits (comprehensive)
4. **GHZ paper** — Greenberger, Horne, Zeilinger (1989) — the original paper
5. **Quantum Circuit Diagrams** — Universal notation guide in the Qiskit docs
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "S4_first_quantum_circuit.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
