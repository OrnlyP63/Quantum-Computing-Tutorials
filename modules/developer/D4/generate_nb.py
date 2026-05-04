#!/usr/bin/env python3
"""generate_nb.py — Module D4: Deutsch-Jozsa Algorithm"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# D4 — Deutsch-Jozsa Algorithm
**Track:** Developer | **Difficulty:** ⭐⭐⭐⭐☆ | **Est. Time:** 35 min

| | |
|---|---|
| **Prerequisites** | F1–F4, D1–D3; quantum gates as matrices |
| **Qiskit Modules** | `qiskit`, `qiskit_aer`, `qiskit.quantum_info` |
| **Companion Video** | Developer Module D4 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. State the **Deutsch-Jozsa problem** and explain why classical algorithms need $O(2^{n-1}+1)$ queries
2. Build **constant** and **balanced oracles** as quantum circuits
3. Implement the full **Deutsch-Jozsa circuit** using the phase kickback trick
4. Verify that the algorithm gives a **deterministic answer in 1 query** for any $n$
5. Explain why this is the **first provable quantum speedup** over classical computation
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 The Problem

Given a function $f: \{0,1\}^n \to \{0,1\}$ promised to be either:
- **Constant**: $f(x) = 0$ for all $x$, or $f(x) = 1$ for all $x$
- **Balanced**: exactly half of all inputs map to 0, the other half to 1

**Determine which.**

### Classical Lower Bound

In the worst case, you must query $f$ at $2^{n-1}+1$ points to be certain. Classical deterministic algorithms need exponential queries.

### Quantum Solution: 1 Query

The Deutsch-Jozsa algorithm answers this with **exactly 1 query** to the oracle. The circuit:

$$|0\rangle^{\otimes n}|1\rangle \xrightarrow{H^{\otimes n+1}} |\Psi_1\rangle \xrightarrow{U_f} |\Psi_2\rangle \xrightarrow{H^{\otimes n}} |\Psi_3\rangle$$

**Measurement:** If all $n$ qubits in $|0\rangle^{\otimes n}$ → **constant**. Otherwise → **balanced**.

### The Math

After the full circuit, the query register state is:

$$|\Psi_3\rangle = \frac{1}{2^n}\sum_{x,y}(-1)^{f(x) \oplus (x \cdot y)}|y\rangle$$

For **constant** $f$: all amplitudes at $|0\rangle^{\otimes n}$ constructively interfere → measure $|0\rangle^{\otimes n}$.

For **balanced** $f$: amplitude at $|0\rangle^{\otimes n}$ cancels to exactly 0 → measure anything but $|0\rangle^{\otimes n}$.

> **Dev Bridge:** The oracle is a black-box function. The algorithm is a single API call that answers a global property with local (1 query) cost.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Oracle Construction"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

sim = AerSimulator()

def constant_oracle(n: int, constant_value: int = 0) -> QuantumCircuit:
    '''
    Constant oracle: f(x) = constant_value for all x.
    - constant_value=0: do nothing (|y⟩ → |y⟩)
    - constant_value=1: flip ancilla (|y⟩ → |y⊕1⟩)
    '''
    qc = QuantumCircuit(n + 1, name=f"Oracle_const_{constant_value}")
    if constant_value == 1:
        qc.x(n)   # flip the ancilla qubit
    return qc

def balanced_oracle_parity(n: int) -> QuantumCircuit:
    '''
    Balanced oracle: f(x) = parity(x) = x₀ XOR x₁ XOR ... XOR x_{n-1}.
    Balanced because exactly half of n-bit strings have even parity.
    Uses phase kickback: CNOT each input qubit to the ancilla.
    '''
    qc = QuantumCircuit(n + 1, name="Oracle_balanced_parity")
    for i in range(n):
        qc.cx(i, n)  # XOR each input bit into ancilla
    return qc

def balanced_oracle_half(n: int) -> QuantumCircuit:
    '''
    Balanced oracle: f(x) = 1 for the first half of inputs (x ≥ 2^(n-1)).
    Implemented by marking on the most significant bit.
    '''
    qc = QuantumCircuit(n + 1, name="Oracle_balanced_half")
    qc.cx(n-1, n)  # flip ancilla if MSB = 1
    return qc

n = 3  # 3-qubit query register
oracles = {
    "Constant 0": constant_oracle(n, 0),
    "Constant 1": constant_oracle(n, 1),
    "Balanced (parity)": balanced_oracle_parity(n),
    "Balanced (MSB)":    balanced_oracle_half(n),
}

for name, oracle in oracles.items():
    print(f"\n{name}:")
    print(oracle.draw(output="text"))
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 The Deutsch-Jozsa Circuit"""))

cells.append(nbf.v4.new_code_cell(r"""def deutsch_jozsa(n: int, oracle: QuantumCircuit) -> QuantumCircuit:
    '''
    Full Deutsch-Jozsa circuit for n query qubits.
    q[0..n-1] = query register (initialized to |0⟩)
    q[n]      = ancilla qubit (initialized to |1⟩ = X|0⟩)
    '''
    qc = QuantumCircuit(n + 1, n, name="Deutsch-Jozsa")

    # Step 1: Initialize ancilla in |−⟩ = H|1⟩ (phase kickback target)
    qc.x(n)    # |0⟩ → |1⟩
    qc.barrier()

    # Step 2: H on all n+1 qubits
    for i in range(n + 1):
        qc.h(i)
    qc.barrier()

    # Step 3: Oracle application
    qc.compose(oracle, inplace=True)
    qc.barrier()

    # Step 4: H on query register (undo superposition)
    for i in range(n):
        qc.h(i)
    qc.barrier()

    # Step 5: Measure query register only
    qc.measure(range(n), range(n))
    return qc

# Build and run for each oracle
n = 3
print("=" * 60)
for name, oracle in oracles.items():
    qc_dj = deutsch_jozsa(n, oracle)
    job   = sim.run(transpile(qc_dj, sim), shots=1024)
    counts = job.result().get_counts()

    # Determine result: all 0s → constant, otherwise → balanced
    zero_outcome = "0" * n
    is_constant  = zero_outcome in counts and counts[zero_outcome] == 1024
    verdict      = "CONSTANT" if is_constant else "BALANCED"
    expected     = "CONSTANT" if "Constant" in name else "BALANCED"
    match        = "✓" if verdict == expected else "✗"

    print(f"{match} {name:25s} → {verdict:8s}  counts={counts}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Visualize Amplitude Evolution"""))

cells.append(nbf.v4.new_code_cell(r"""# Track the state vector through each step of the algorithm

n = 2  # use n=2 for clarity (4 basis states)
oracle_name = "Balanced (parity)"
oracle = balanced_oracle_parity(n)

# Build circuit step by step without measurement
def dj_statevector(n, oracle):
    stages = {}

    # Stage 0: Initial |0..01⟩
    qc0 = QuantumCircuit(n + 1)
    stages["0. Initial |0...01⟩"] = Statevector(qc0)

    # After X on ancilla
    qc0.x(n)
    stages["1. X on ancilla → |0...0⟩|1⟩"] = Statevector(qc0)

    # After H on all
    for i in range(n+1): qc0.h(i)
    stages[f"2. H⊗(n+1) → uniform superpos"] = Statevector(qc0)

    # After oracle
    qc0.compose(oracle, inplace=True)
    stages["3. After oracle U_f"] = Statevector(qc0)

    # After H on query
    for i in range(n): qc0.h(i)
    stages["4. Final H⊗n on query"] = Statevector(qc0)

    return stages

stages = dj_statevector(n, oracle)
basis  = [f"|{i:0{n+1}b}⟩" for i in range(2**(n+1))]

fig, axes = plt.subplots(1, len(stages), figsize=(18, 5))
for ax, (stage_name, sv) in zip(axes, stages.items()):
    amps = sv.data
    probs = np.abs(amps)**2
    phases = np.angle(amps) / np.pi

    x = np.arange(len(basis))
    bars = ax.bar(x, probs, color=[plt.cm.RdYlGn(p) for p in probs], edgecolor="black", width=0.6)
    for bi, (b, ph, pr) in enumerate(zip(basis, phases, probs)):
        if pr > 0.01:
            ax.text(bi, pr + 0.02, f"{ph:.2f}π", ha="center", fontsize=7, rotation=45)
    ax.set_xticks(x); ax.set_xticklabels(basis, rotation=45, fontsize=7)
    ax.set_ylim(0, 0.7); ax.set_ylabel("Probability")
    ax.set_title(stage_name, fontsize=8, fontweight="bold")

plt.suptitle("Deutsch-Jozsa: Amplitude Evolution Through the Circuit (n=2, balanced oracle)\n"
             "Final state: query register always |00⟩=0 for constant, ≠|00⟩ for balanced",
             fontsize=11, fontweight="bold")
plt.tight_layout()
plt.savefig("dj_amplitude_evolution.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Classical vs Quantum Query Complexity"""))

cells.append(nbf.v4.new_code_cell(r"""fig, ax = plt.subplots(figsize=(10, 5))

n_range = np.arange(1, 20)
classical_worst = 2**(n_range - 1) + 1
quantum_queries = np.ones_like(n_range)

ax.semilogy(n_range, classical_worst, "b-o", lw=2.5, ms=7, label="Classical worst case: $2^{n-1}+1$")
ax.semilogy(n_range, quantum_queries, "r-s", lw=2.5, ms=7, label="Quantum (Deutsch-Jozsa): 1")

ax.fill_between(n_range, quantum_queries, classical_worst,
                alpha=0.15, color="blue", label="Exponential quantum speedup")
ax.set_xlabel("Number of input bits $n$", fontsize=13)
ax.set_ylabel("Number of oracle queries (log scale)", fontsize=13)
ax.set_title("Deutsch-Jozsa: First Provable Exponential Quantum Speedup\n"
             "Quantum = 1 query always; Classical = $2^{n-1}+1$ worst case",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=11)
ax.grid(True, which="both", alpha=0.3)

# Annotate
for n_val in [5, 10, 15, 19]:
    c_val = 2**(n_val - 1) + 1
    ax.annotate(f"n={n_val}: {c_val:,}",
                xy=(n_val, c_val), xytext=(n_val - 2, c_val / 3),
                arrowprops=dict(arrowstyle="->", color="navy"),
                fontsize=9, color="navy")

plt.tight_layout()
plt.savefig("dj_complexity.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Oracle Analysis

Given these oracle circuits, determine (without running) whether each is constant or balanced. Then verify by running the Deutsch-Jozsa algorithm.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — analyze and run each mystery oracle

def mystery_oracle_1(n: int) -> QuantumCircuit:
    '''Unknown oracle — classify it.'''
    qc = QuantumCircuit(n + 1, name="Mystery 1")
    qc.x(0); qc.cx(0, n); qc.x(0)  # f(x) = NOT(x₀)
    return qc

def mystery_oracle_2(n: int) -> QuantumCircuit:
    '''Unknown oracle — classify it.'''
    qc = QuantumCircuit(n + 1, name="Mystery 2")
    # f(x) = 1 if x₀ AND x₁, else 0 — is this balanced?
    qc.ccx(0, 1, n)
    return qc

mystery_oracles = {
    "Mystery 1": mystery_oracle_1,
    "Mystery 2": mystery_oracle_2,
}

n = 3
for name, oracle_fn in mystery_oracles.items():
    # YOUR CODE HERE: run DJ and report result
    oracle = oracle_fn(n)
    qc_dj = deutsch_jozsa(n, oracle)
    job = sim.run(transpile(qc_dj, sim), shots=100)
    counts = job.result().get_counts()
    is_constant = "0" * n in counts and counts.get("0"*n, 0) > 90
    print(f"{name}: {'CONSTANT' if is_constant else 'BALANCED'}  — counts: {counts}")
    print(f"  (Verify manually: is the oracle truly {'constant' if is_constant else 'balanced'}?)")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — The Single-Bit Case (Deutsch Problem)

The original Deutsch problem is a special case with $n=1$:
- $f: \{0,1\} \to \{0,1\}$ is either constant ($f(0)=f(1)$) or balanced ($f(0) \neq f(1)$)
- Classically: need 2 queries; Quantum: need 1

Implement the Deutsch algorithm and verify all 4 possible functions.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — 4 single-bit function oracles and Deutsch algorithm

# The 4 possible functions f: {0,1} -> {0,1}
# f1: f(0)=0, f(1)=0 (constant 0)
# f2: f(0)=1, f(1)=1 (constant 1)
# f3: f(0)=0, f(1)=1 (balanced, identity)
# f4: f(0)=1, f(1)=0 (balanced, NOT)

def oracle_f1(): qc = QuantumCircuit(2, name="f1: const 0"); return qc
def oracle_f2(): qc = QuantumCircuit(2, name="f2: const 1"); qc.x(1); return qc
def oracle_f3(): qc = QuantumCircuit(2, name="f3: identity"); qc.cx(0,1); return qc
def oracle_f4(): qc = QuantumCircuit(2, name="f4: NOT"); qc.x(0); qc.cx(0,1); qc.x(0); return qc

functions = [("Constant 0", oracle_f1),
             ("Constant 1", oracle_f2),
             ("Balanced (id)", oracle_f3),
             ("Balanced (NOT)", oracle_f4)]

for fname, oracle_fn in functions:
    oracle = oracle_fn()
    qc_deutsch = deutsch_jozsa(1, oracle)
    job = sim.run(transpile(qc_deutsch, sim), shots=1000)
    counts = job.result().get_counts()
    is_const = "0" in counts and counts["0"] > 900
    print(f"{fname:20s}: {'CONSTANT' if is_const else 'BALANCED'}  {counts}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Design a **quantum oracle** for the following function and verify with Deutsch-Jozsa:

$$f(x_0, x_1, x_2) = x_0 \oplus x_1 \oplus x_2 \oplus (x_0 \cdot x_1)$$

1. Prove analytically whether this function is balanced or constant
2. Implement the oracle using CNOT and Toffoli gates
3. Run Deutsch-Jozsa to confirm
4. Count the classical queries needed vs the 1 quantum query
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Implement oracle for f(x) = x₀ ⊕ x₁ ⊕ x₂ ⊕ (x₀ AND x₁)

def custom_oracle(n: int = 3) -> QuantumCircuit:
    '''Oracle for f(x) = x0 XOR x1 XOR x2 XOR (x0 AND x1).'''
    qc = QuantumCircuit(n + 1, name="Custom Oracle")
    # YOUR CODE HERE
    # CNOT for each XOR term
    qc.cx(0, n)   # XOR x₀
    qc.cx(1, n)   # XOR x₁
    qc.cx(2, n)   # XOR x₂
    # Toffoli for the AND term
    qc.ccx(0, 1, n)   # XOR (x₀ AND x₁)
    return qc

# Step 1: Analytical proof
print("Analytical check: enumerate all 8 inputs")
count_0, count_1 = 0, 0
for x in range(8):
    x0 = (x >> 0) & 1; x1 = (x >> 1) & 1; x2 = (x >> 2) & 1
    f  = x0 ^ x1 ^ x2 ^ (x0 & x1)
    print(f"  x=({x0},{x1},{x2}) → f={f}")
    if f == 0: count_0 += 1
    else: count_1 += 1

print(f"\nf=0: {count_0} times,  f=1: {count_1} times → {'BALANCED' if count_0==count_1 else 'CONSTANT'}")

# Step 2: Verify with DJ
oracle = custom_oracle()
qc_dj  = deutsch_jozsa(3, oracle)
job = sim.run(transpile(qc_dj, sim), shots=100)
counts = job.result().get_counts()
is_const = "000" in counts and counts["000"] == 100
print(f"\nDeutsch-Jozsa result: {'CONSTANT' if is_const else 'BALANCED'}")
print(f"Counts: {counts}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Deutsch & Jozsa (1992)** — "Rapid solution of problems by quantum computation" — original paper
2. **Nielsen & Chuang**, Section 1.4.3 — Quantum algorithms and complexity
3. **Qiskit Textbook** — "Deutsch-Jozsa Algorithm" with interactive oracle builder
4. **Aaronson (2004)** — "Limitations of quantum advice" — deeper complexity theory
5. **Simon's Algorithm** — Next step: exponential speedup over probabilistic classical algorithms
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D4_deutsch_jozsa.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
