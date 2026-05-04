#!/usr/bin/env python3
"""generate_nb.py — Module D5: Grover's Search Algorithm"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# D5 — Grover's Search Algorithm
**Track:** Developer | **Difficulty:** ⭐⭐⭐⭐☆ | **Est. Time:** 40 min

| | |
|---|---|
| **Prerequisites** | F1–F4, D1–D4 |
| **Qiskit Modules** | `qiskit`, `qiskit_aer`, `qiskit.circuit.library` |
| **Companion Video** | Developer Module D5 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. State Grover's search problem and its $O(\sqrt{N})$ quantum speedup over $O(N)$ classical
2. Implement the **Grover oracle** and **diffusion operator** (Grover diffuser)
3. Visualize **amplitude amplification** after each iteration
4. Determine the **optimal number of iterations**: $\lfloor\pi\sqrt{N}/4\rfloor$
5. Run a 3-qubit search and confirm the marked state is found with near-certainty
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Algorithm Overview

**Problem:** $N = 2^n$ items, exactly $M$ are "marked" (satisfying a predicate). Find one.

**Classical lower bound:** $O(N/M)$ expected queries (random search).

**Grover's algorithm:** $O(\sqrt{N/M})$ queries — quadratic speedup.

### The Two Operations

**1. Oracle $O_f$** (phase oracle): marks the target state by flipping its sign:
$$O_f|x\rangle = (-1)^{f(x)}|x\rangle$$

**2. Diffusion Operator $D$** (Grover diffuser): reflects about the uniform superposition:
$$D = 2|\psi\rangle\langle\psi| - I, \quad |\psi\rangle = H^{\otimes n}|0\rangle^{\otimes n}$$

### Iteration = Reflection + Reflection = Rotation

Each Grover iteration rotates the state toward the marked state by an angle $2\theta$, where:
$$\sin(\theta) = \sqrt{M/N}$$

Optimal iterations: $k^* = \left\lfloor \frac{\pi}{4\theta} \right\rfloor \approx \frac{\pi}{4}\sqrt{\frac{N}{M}}$

After $k^*$ iterations, the marked state has probability $\approx 1 - M/N \approx 1$ (for $M \ll N$).

> **Dev Bridge:** Think of Grover's as a probabilistic binary search where amplitude amplification replaces bisection, and guaranteed $O(\sqrt{N})$ replaces average $O(N/2)$.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 The Grover Oracle"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

sim = AerSimulator()

def grover_oracle(n: int, target: int) -> QuantumCircuit:
    '''
    Phase oracle for Grover's: flips the phase of |target⟩.
    Implemented using a multi-controlled-Z gate on the target bitstring.
    '''
    qc = QuantumCircuit(n, name=f"Oracle|{target:0{n}b}⟩")
    # Convert target to binary and flip qubits that should be 0
    # Multi-controlled Z (all controls must be |1⟩)
    target_bits = format(target, f"0{n}b")

    # Flip qubits that are '0' in target (to make them '1' for the MCZ)
    for i, bit in enumerate(reversed(target_bits)):
        if bit == "0":
            qc.x(i)

    # Multi-controlled-Z: flip phase when all qubits are |1⟩
    if n == 1:
        qc.z(0)
    elif n == 2:
        qc.cz(0, 1)
    else:
        # Use H + multi-controlled-X + H trick
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)  # multi-controlled X
        qc.h(n - 1)

    # Unflip the qubits
    for i, bit in enumerate(reversed(target_bits)):
        if bit == "0":
            qc.x(i)

    return qc

# Test oracle on |101⟩ (= 5 in 3 qubits)
n_test = 3
target_test = 5  # binary: 101
oracle = grover_oracle(n_test, target_test)
print(f"Oracle for |{target_test:0{n_test}b}⟩ = |{target_test}⟩:")
print(oracle.draw(output="text"))

# Verify: oracle should flip phase of |101⟩ only
sv_before = Statevector(QuantumCircuit(n_test))
# Apply H to all to create uniform superposition
qc_test = QuantumCircuit(n_test)
for i in range(n_test): qc_test.h(i)
sv_uniform = Statevector(qc_test)

qc_test.compose(oracle, inplace=True)
sv_after = Statevector(qc_test)

print(f"\nUniform superposition → oracle → :")
basis = [f"|{i:03b}⟩" for i in range(8)]
for b, a_bef, a_aft in zip(basis, sv_uniform.data, sv_after.data):
    phase_flip = "← FLIPPED" if not np.isclose(a_bef, a_aft) else ""
    print(f"  {b}: {a_bef:.4f} → {a_aft:.4f}  {phase_flip}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 The Grover Diffuser"""))

cells.append(nbf.v4.new_code_cell(r"""def grover_diffuser(n: int) -> QuantumCircuit:
    '''
    Grover diffuser: D = 2|ψ⟩⟨ψ| - I
    = H^⊗n (2|0⟩⟨0| - I) H^⊗n
    = H^⊗n X^⊗n (multi-controlled-Z) X^⊗n H^⊗n
    '''
    qc = QuantumCircuit(n, name="Diffuser")
    qc.h(range(n))          # H^⊗n
    qc.x(range(n))          # X^⊗n (flip all)

    # Multi-controlled-Z: phase flip on |1⟩^⊗n (= |0⟩^⊗n before X)
    if n == 1:
        qc.z(0)
    elif n == 2:
        qc.cz(0, 1)
    else:
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)

    qc.x(range(n))          # X^⊗n (unflip)
    qc.h(range(n))          # H^⊗n
    return qc

diffuser = grover_diffuser(3)
print("Grover Diffuser (3 qubits):")
print(diffuser.draw(output="text"))

from qiskit.quantum_info import Operator
D = Operator(diffuser).data
print(f"\nDiffuser matrix (magnitude):")
print(np.round(np.abs(D.real), 3))
print(f"\nUnitary? {np.allclose(D.conj().T @ D, np.eye(8))}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Full Grover's Algorithm"""))

cells.append(nbf.v4.new_code_cell(r"""def grovers_algorithm(n: int, target: int, n_iterations: int) -> QuantumCircuit:
    '''
    Full Grover's circuit for n qubits, searching for |target⟩.
    '''
    oracle   = grover_oracle(n, target)
    diffuser = grover_diffuser(n)

    qc = QuantumCircuit(n, n, name=f"Grover n={n} target={target} iter={n_iterations}")

    # Step 1: Uniform superposition
    qc.h(range(n))
    qc.barrier()

    # Step 2: Grover iterations
    for _ in range(n_iterations):
        qc.compose(oracle, inplace=True)    # Phase oracle
        qc.compose(diffuser, inplace=True)  # Diffuser
        qc.barrier()

    # Step 3: Measure
    qc.measure(range(n), range(n))
    return qc

# Optimal iterations: floor(π/4 * √N)
n = 3
N = 2**n
target = 5  # |101⟩

n_iters_optimal = int(np.floor(np.pi / 4 * np.sqrt(N)))
print(f"n={n}, N={N}, target=|{target:03b}⟩={target}")
print(f"Optimal iterations: π/4 × √{N} ≈ {n_iters_optimal}")

# Run with 1, 2, 3 iterations and compare
fig, axes = plt.subplots(1, 4, figsize=(18, 4))
for ax, n_iter in zip(axes, [1, 2, 3, n_iters_optimal]):
    qc_grover = grovers_algorithm(n, target, n_iter)
    job = sim.run(transpile(qc_grover, sim), shots=2048)
    counts = job.result().get_counts()
    total  = sum(counts.values())

    all_out = [f"{i:03b}" for i in range(N)]
    vals    = [counts.get(o, 0) / total for o in all_out]
    colors  = ["#4CAF50" if o == f"{target:03b}" else "#90A4AE" for o in all_out]
    bars = ax.bar(all_out, vals, color=colors, edgecolor="black", width=0.7)

    target_pct = counts.get(f"{target:03b}", 0) / total * 100
    ax.set_title(f"Iteration {n_iter}\nP(|{target:03b}⟩) = {target_pct:.1f}%",
                 fontsize=11, fontweight="bold",
                 color="#2E7D32" if n_iter == n_iters_optimal else "black")
    ax.set_ylabel("Probability"); ax.set_ylim(0, 1.1)
    ax.tick_params(axis='x', rotation=45)

plt.suptitle(f"Grover's Algorithm: Amplitude Amplification of |{target:03b}⟩\n"
             f"Green = target state, Gray = other states",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("grover_iterations.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Amplitude Amplification — Geometric View"""))

cells.append(nbf.v4.new_code_cell(r"""# Theoretical amplitude at target state after k iterations
n = 3; N = 2**n

theta = np.arcsin(1 / np.sqrt(N))  # single marked state

k_max = 15
iterations = np.arange(0, k_max + 1)
amplitude_target = np.sin((2 * iterations + 1) * theta)
prob_target      = amplitude_target**2

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Panel 1: Probability vs iterations
ax = axes[0]
ax.plot(iterations, prob_target, "g-o", lw=2.5, ms=7, label="P(target state)")
ax.axhline(1/N, ls="--", color="gray", lw=1.5, label=f"Random guess (1/{N})")
ax.axvline(int(np.pi/(4*theta)), ls="--", color="red", lw=2,
           label=f"Optimal: k*={int(np.pi/(4*theta))}")
ax.set_xlabel("Number of Grover Iterations k")
ax.set_ylabel("Probability of finding target")
ax.set_title("Amplitude Amplification: Probability vs Iterations\n"
             "Too few OR too many iterations both fail — match k*", fontsize=11, fontweight="bold")
ax.legend(fontsize=10); ax.grid(True, alpha=0.3); ax.set_ylim(0, 1.1)
ax.fill_between(iterations, prob_target, alpha=0.2, color="green")

# Panel 2: Geometric circle picture
ax2 = axes[1]
theta_angles = [(2*k + 1) * theta for k in range(8)]

circle = plt.Circle((0, 0), 1, fill=False, color="navy", lw=1.5)
ax2.add_patch(circle)

# Axes
ax2.axhline(0, color="black", lw=0.8)
ax2.axvline(0, color="black", lw=0.8)
ax2.text(1.08, 0, "|target⟩", fontsize=10, va="center")
ax2.text(0, 1.08, "|perp⟩", fontsize=10, ha="center")

# Plot state vector at each iteration
colors = plt.cm.viridis(np.linspace(0, 1, len(theta_angles)))
for i, (angle, color) in enumerate(zip(theta_angles, colors)):
    x = np.cos(angle - np.pi/2)  # rotate to have |0⟩ at (0,1)
    y = np.sin(angle - np.pi/2)
    ax2.quiver(0, 0, np.sin(angle), np.cos(angle),
               angles="xy", scale_units="xy", scale=1,
               color=color, alpha=0.8, width=0.015,
               label=f"k={i}" if i < 4 else None)
    ax2.text(np.sin(angle)*1.12, np.cos(angle)*1.12, f"k={i}", fontsize=8, ha="center")

ax2.set_xlim(-1.3, 1.3); ax2.set_ylim(-1.3, 1.3)
ax2.set_aspect("equal")
ax2.set_title("Geometric View: Each Grover Step Rotates\nState Vector by 2θ Toward |target⟩",
              fontsize=11, fontweight="bold")
ax2.legend(fontsize=8, loc="lower left")

plt.suptitle("Grover's Algorithm: The Geometry of Amplitude Amplification",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("grover_geometry.png", dpi=120, bbox_inches="tight")
plt.show()

print(f"Optimal iterations: k* = {int(np.pi/(4*theta))}")
print(f"Max P(target) = {np.max(prob_target):.4f} at k = {np.argmax(prob_target)}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Multi-Target Search

Extend Grover's to search for **multiple marked states** simultaneously.

If there are $M$ marked states, the optimal iterations change to $\lfloor \pi/(4\arcsin(\sqrt{M/N})) \rfloor$.

Implement a 3-qubit search for 2 marked states and verify the probability is shared between them.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — multi-target Grover's

def multi_target_oracle(n: int, targets: list) -> QuantumCircuit:
    '''Oracle that marks multiple target states.'''
    qc = QuantumCircuit(n, name=f"Oracle{targets}")
    for target in targets:
        # YOUR CODE HERE: apply single-target oracle for each target
        # Hint: compose the single-target oracles
        oracle_t = grover_oracle(n, target)
        qc.compose(oracle_t, inplace=True)
    return qc

n = 3; N = 2**n
targets = [3, 5]  # |011⟩ and |101⟩
M = len(targets)

theta_M = np.arcsin(np.sqrt(M / N))
n_iters_M = int(np.floor(np.pi / (4 * theta_M)))
print(f"Targets: {[f'|{t:03b}⟩' for t in targets]}")
print(f"Optimal iterations for M={M}: {n_iters_M}")

multi_oracle = multi_target_oracle(n, targets)
diffuser     = grover_diffuser(n)

qc_multi = QuantumCircuit(n, n)
qc_multi.h(range(n))
for _ in range(n_iters_M):
    qc_multi.compose(multi_oracle, inplace=True)
    qc_multi.compose(diffuser, inplace=True)
qc_multi.measure(range(n), range(n))

# YOUR CODE HERE: run and show results
job = sim.run(transpile(qc_multi, sim), shots=2048)
counts = job.result().get_counts()
total = sum(counts.values())
print("\nResults:")
for outcome, count in sorted(counts.items(), key=lambda x: -x[1])[:6]:
    is_target = int(outcome, 2) in targets
    print(f"  |{outcome}⟩: {count} ({count/total*100:.1f}%) {'← TARGET' if is_target else ''}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Iteration Sweep

Run Grover's for $n=4$ qubits (N=16) with iterations from 1 to 10. Plot the success probability at each iteration and identify the optimal $k^*$.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — iteration sweep for n=4
n4 = 4; N4 = 2**n4; target4 = 7  # |0111⟩

success_probs = []
iter_range = list(range(1, 11))

for k in iter_range:
    qc_k = grovers_algorithm(n4, target4, k)
    job  = sim.run(transpile(qc_k, sim), shots=2000)
    counts_k = job.result().get_counts()
    p_target  = counts_k.get(f"{target4:04b}", 0) / 2000
    success_probs.append(p_target)

plt.figure(figsize=(9, 4))
plt.plot(iter_range, success_probs, "g-o", lw=2.5, ms=8)
plt.axhline(1/N4, ls="--", color="gray", label=f"Random baseline (1/{N4}={1/N4:.3f})")
plt.xlabel("Grover Iterations k"); plt.ylabel("P(target)")
plt.title(f"Grover's n={n4}: Success Probability vs Iterations\n(N={N4}, target=|{target4:04b}⟩)")
plt.legend(); plt.grid(True, alpha=0.3)
plt.xticks(iter_range)
optimal_theory = int(np.floor(np.pi/4 * np.sqrt(N4)))
plt.axvline(optimal_theory, ls="--", color="red", label=f"k*={optimal_theory} (theory)")
plt.legend()
plt.show()

print(f"Theoretical optimal: k* = {optimal_theory}")
print(f"Empirical optimal:   k* = {iter_range[np.argmax(success_probs)]}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Implement **Grover's algorithm with unknown number of solutions** using the amplitude estimation technique:

When you don't know $M$ (the number of marked items), you can use a modified Grover's that:
1. Start with $k=1$ iterations
2. If no marked item found, try $k = \lceil 6k/5 \rceil$ (increase by 20%)
3. Repeat until success

This achieves $O(\sqrt{N/M})$ queries even without knowing $M$.

Implement and verify on a 4-qubit example where you hide the number of targets.
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Grover's with Unknown M
def quantum_search_unknown_M(n: int, oracle_fn, max_retries: int = 20) -> tuple:
    '''
    Quantum search when M (# of marked items) is unknown.
    Returns: (found_state, total_queries)
    '''
    N = 2**n
    k = 1
    total_queries = 0

    for attempt in range(max_retries):
        # Run with k iterations
        # YOUR CODE HERE: build circuit, simulate, check if target found
        qc = QuantumCircuit(n, n)
        qc.h(range(n))
        for _ in range(k):
            oracle_qc = oracle_fn(n)
            qc.compose(oracle_qc, inplace=True)
            qc.compose(grover_diffuser(n), inplace=True)
            total_queries += 1
        qc.measure(range(n), range(n))

        job = sim.run(transpile(qc, sim), shots=1)
        result_state = list(job.result().get_counts().keys())[0]
        result_int   = int(result_state, 2)

        # Check if this is a valid answer (replace with actual oracle check)
        # For testing: oracle validates the answer
        print(f"  Attempt {attempt+1}, k={k}: got |{result_state}⟩", end="")
        if result_int in [3, 7, 11]:  # known targets for this test
            print(f" ← FOUND!")
            return result_int, total_queries
        else:
            print(f" (not target)")
            k = int(np.ceil(k * 6 / 5)) + 1  # grow k by ~20%

    return None, total_queries

print("Challenge: Implement the oracle check properly and test it.")
print("Expected: finds a target state within O(√N) total queries on average.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Grover (1996)** — "A fast quantum mechanical algorithm for database search" — original paper
2. **Nielsen & Chuang**, Chapter 6 — Quantum search algorithms (comprehensive analysis)
3. **Qiskit Textbook** — "Grover's Algorithm" with interactive oracle builder
4. **Boyer et al. (1998)** — "Tight bounds on quantum searching" — optimal iteration analysis
5. **Grover's in Qiskit** — `qiskit.circuit.library.GroverOperator` — production-ready implementation
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D5_grover_search.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
