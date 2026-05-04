#!/usr/bin/env python3
"""generate_nb.py — Module D3: Building Complex Circuits"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# D3 — Building Complex Circuits
**Track:** Developer | **Difficulty:** ⭐⭐⭐☆☆ | **Est. Time:** 35 min

| | |
|---|---|
| **Prerequisites** | F1–F4, D1, D2 |
| **Qiskit Modules** | `qiskit`, `qiskit.circuit.library`, `qiskit_aer` |
| **Companion Video** | Developer Module D3 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Use `QuantumRegister` and `ClassicalRegister` for **named, multi-register** circuits
2. Build **modular sub-circuits** and compose them with `.compose()` and `.append()`
3. Create **parameterized circuits** using `ParameterVector` and bind parameters at runtime
4. Add **barriers** for readability and to prevent transpiler optimizations across sections
5. Use **conditional gates** (`if_test`) based on mid-circuit measurement results
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Circuit Composition Philosophy

In software engineering, you decompose programs into functions. In quantum computing:

- **Sub-circuits** = reusable quantum subroutines (gates defined by circuits)
- **`.compose()`** = function composition (chain circuits end-to-end)
- **`.append()`** = call a gate instruction on specific qubits
- **Parameterized circuits** = function templates with free parameters (like function arguments)
- **Barriers** = `#pragma` directives — prevent transpiler from merging across boundaries

### The Module Pattern

```python
# Define a reusable quantum subroutine
def make_bell_prep(name="bell") -> QuantumCircuit:
    qc = QuantumCircuit(2, name=name)
    qc.h(0); qc.cx(0, 1)
    return qc

# Use it in a larger circuit
main = QuantumCircuit(4)
main.append(make_bell_prep().to_gate(), [0, 1])
main.append(make_bell_prep().to_gate(), [2, 3])
```

This mirrors Python's function/module system exactly.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Multi-Register Circuits"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

sim = AerSimulator()

# Named registers for clarity — like named function arguments
alice = QuantumRegister(2, name="alice")
bob   = QuantumRegister(2, name="bob")
c_a   = ClassicalRegister(2, name="c_alice")
c_b   = ClassicalRegister(2, name="c_bob")

qc = QuantumCircuit(alice, bob, c_a, c_b, name="Multi-Register Demo")

# Create Bell pairs within each party
qc.h(alice[0]);     qc.cx(alice[0], alice[1])
qc.h(bob[0]);       qc.cx(bob[0],   bob[1])
qc.barrier(label="Bell pairs created")

# Cross-party entanglement
qc.cx(alice[0], bob[0])
qc.barrier(label="Cross-party entanglement")

# Measure each register separately
qc.measure(alice, c_a)
qc.measure(bob,   c_b)

print("Multi-Register Circuit:")
print(qc.draw(output="text"))
print(f"\nRegisters: {qc.qregs}")
print(f"Classical registers: {qc.cregs}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Modular Sub-Circuits"""))

cells.append(nbf.v4.new_code_cell(r"""# Pattern: define subroutines as small circuits, compose into larger ones

def make_qft_rotation(n: int, k: int) -> QuantumCircuit:
    '''QFT rotation block for qubit k in an n-qubit QFT.'''
    qc = QuantumCircuit(n, name=f"QFT_rot_{k}")
    qc.h(k)
    for j in range(k + 1, n):
        qc.cp(np.pi / 2**(j - k), j, k)  # controlled phase
    return qc

def make_qft(n: int) -> QuantumCircuit:
    '''Build n-qubit QFT as composition of rotation sub-circuits.'''
    qc = QuantumCircuit(n, name=f"QFT-{n}")
    for k in range(n):
        rot = make_qft_rotation(n, k)
        qc.compose(rot, inplace=True)
        qc.barrier()
    # Bit reversal (swap qubits)
    for i in range(n // 2):
        qc.swap(i, n - 1 - i)
    return qc

# Build and inspect 4-qubit QFT
qft4 = make_qft(4)
print("4-qubit QFT circuit:")
print(qft4.draw(output="text"))
print(f"\nDepth: {qft4.depth()}, Gate count: {dict(qft4.count_ops())}")

# Convert to a gate and use in a larger circuit
qft_gate = qft4.to_gate(label="QFT₄")
main = QuantumCircuit(6)
main.append(qft_gate, [0, 1, 2, 3])  # QFT on first 4 qubits
main.h(4); main.cx(4, 5)            # Bell pair on remaining 2
print(f"\nComposed circuit depth: {main.decompose().depth()}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Parameterized Circuits"""))

cells.append(nbf.v4.new_code_cell(r"""from qiskit.circuit import ParameterVector, Parameter

# Parameterized circuit = circuit template with free angle parameters
# This is the core building block of variational quantum algorithms (VQE, VQC)

n_qubits = 3
n_layers = 2
theta = ParameterVector("θ", n_qubits * n_layers)  # 6 parameters

def build_hardware_efficient_ansatz(n: int, layers: int, params: ParameterVector) -> QuantumCircuit:
    '''Hardware-efficient ansatz: alternating Ry rotations and CNOT entanglers.'''
    qc = QuantumCircuit(n, name="HE-Ansatz")
    idx = 0
    for layer in range(layers):
        # Rotation layer
        for q in range(n):
            qc.ry(params[idx], q)
            idx += 1
        # Entanglement layer (linear coupling)
        for q in range(n - 1):
            qc.cx(q, q + 1)
        if layer < layers - 1:
            qc.barrier()
    return qc

ansatz = build_hardware_efficient_ansatz(n_qubits, n_layers, theta)
print("Parameterized Ansatz:")
print(ansatz.draw(output="text"))
print(f"\nFree parameters: {ansatz.parameters}")

# Bind parameters to specific values
import numpy as np
param_values = np.random.uniform(0, 2*np.pi, len(theta))
bound_circuit = ansatz.assign_parameters(dict(zip(theta, param_values)))

sv = Statevector(bound_circuit)
print(f"\nAfter binding {len(theta)} parameters:")
print(f"  Sample statevector norm: {np.linalg.norm(sv.data):.6f}")
print(f"  First 4 amplitudes: {np.round(sv.data[:4], 4)}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Conditional Gates (Mid-Circuit Measurement)"""))

cells.append(nbf.v4.new_code_cell(r"""# Conditional gates: apply gate B only if classical bit = 1
# Core of quantum teleportation and error correction

qc_cond = QuantumCircuit(2, 2, name="Conditional Gate Demo")

# Step 1: Put qubit 0 in superposition, measure
qc_cond.h(0)
qc_cond.measure(0, 0)

# Step 2: Conditionally apply X to qubit 1 based on measurement of qubit 0
with qc_cond.if_test((qc_cond.clbits[0], 1)):
    qc_cond.x(1)

# Measure qubit 1
qc_cond.measure(1, 1)

print("Conditional Gate Circuit:")
print(qc_cond.draw(output="text"))

# Simulate — qubit 1 should mirror qubit 0
job = sim.run(transpile(qc_cond, sim), shots=4096)
counts = job.result().get_counts()
print(f"\nCounts: {counts}")
total = sum(counts.values())
print("Expected: only 00 and 11 (classical teleportation of 0 or 1 via conditional X)")
for k, v in sorted(counts.items()):
    print(f"  {k}: {v} ({v/total*100:.1f}%)")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Circuit Composition Patterns"""))

cells.append(nbf.v4.new_code_cell(r"""# Three composition methods compared

# Method 1: .compose() — chain circuits sequentially on the same qubits
qc_prep = QuantumCircuit(2, name="prep")
qc_prep.h(0); qc_prep.h(1)

qc_entangle = QuantumCircuit(2, name="entangle")
qc_entangle.cx(0, 1)

qc_composed = qc_prep.compose(qc_entangle)
print("Method 1 — compose():")
print(qc_composed.draw(output="text"))

# Method 2: .append() — insert a sub-circuit gate at specific qubit positions
qc_main = QuantumCircuit(4)
bell_gate = QuantumCircuit(2, name="Bell").h(0).cx(0,1).to_gate(label="Bell")
qc_main.append(bell_gate, [0, 1])
qc_main.append(bell_gate, [2, 3])
print("\nMethod 2 — append() sub-circuit gate:")
print(qc_main.draw(output="text"))

# Method 3: tensor product (circuits acting on disjoint qubit sets)
qc_a = QuantumCircuit(2, name="A")
qc_a.h(0); qc_a.cx(0,1)

qc_b = QuantumCircuit(2, name="B")
qc_b.x(0); qc_b.h(1)

# tensor: combine two circuits acting on separate qubits
qc_tensor = qc_a.tensor(qc_b)  # B on lower qubits, A on upper
print(f"\nMethod 3 — tensor(): combined {qc_a.num_qubits}+{qc_b.num_qubits} qubit circuit")
print(qc_tensor.draw(output="text"))

fig, axes = plt.subplots(1, 3, figsize=(15, 3))
for ax, (title, qc) in zip(axes, [
    ("compose()", qc_composed),
    ("append()", qc_main),
    ("tensor()", qc_tensor),
]):
    ax.axis("off")
    ax.text(0.1, 0.5, str(qc.draw(output="text")), transform=ax.transAxes,
            fontfamily="monospace", fontsize=7, va="center")
    ax.set_title(title, fontsize=12, fontweight="bold")

plt.suptitle("Three Circuit Composition Patterns", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("circuit_composition.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Build a Modular Adder

Implement a **quantum half adder** that computes the sum and carry of two qubits $a$ and $b$:

| $a$ | $b$ | Sum = $a \oplus b$ | Carry = $a \cdot b$ |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 0 |
| 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 1 |

Use CNOT (XOR) for sum and Toffoli (AND) for carry.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — quantum half adder

def quantum_half_adder(a_val: int, b_val: int) -> tuple:
    '''Compute quantum half adder for classical inputs a and b.'''
    qc = QuantumCircuit(3, 2)  # q0=a, q1=b, q2=carry; c0=sum, c1=carry
    if a_val: qc.x(0)
    if b_val: qc.x(1)

    # YOUR CODE HERE:
    # Sum = a XOR b → CNOT(a, sum_output) — but we need a dedicated qubit
    # Carry = a AND b → Toffoli(a, b, carry)
    # For this 3-qubit version: q2 = carry, store sum back in q0 or q1

    # Hint: CNOT(0, 1) computes b := a XOR b (sum)
    # Toffoli(0, original_a_qubit, 2) computes carry (need to copy a first!)

    # Simple approach:
    qc.ccx(0, 1, 2)   # carry = a AND b (Toffoli)
    qc.cx(0, 1)        # sum = a XOR b   (CNOT)
    qc.measure([1, 2], [0, 1])  # c[0]=sum, c[1]=carry
    return qc

print(f"{'a':2s} {'b':2s} {'Sum':5s} {'Carry':6s}")
print("-" * 20)
for a, b in [(0,0),(0,1),(1,0),(1,1)]:
    qc_add = quantum_half_adder(a, b)
    job = sim.run(transpile(qc_add, sim), shots=100)
    result = max(job.result().get_counts(), key=job.result().get_counts().get)
    c_sum, c_carry = result[1], result[0]  # little-endian
    print(f"{a:2d} {b:2d}   {c_sum:2s}    {c_carry:2s}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Parameterized Bell State

Create a parameterized version of the Bell state where the entanglement angle is adjustable:

$$|\psi(\theta)\rangle = \cos(\theta/2)|00\rangle + \sin(\theta/2)|11\rangle$$

Show how the correlations change as $\theta$ goes from 0 to $\pi$.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — parameterized Bell state
theta_param = Parameter("θ")

qc_param_bell = QuantumCircuit(2, 2)
# YOUR CODE HERE: use Ry(theta) instead of H, then CNOT

# Bind and simulate for various theta values
theta_values = np.linspace(0, np.pi, 9)
p_00_list = []; p_11_list = []

for t in theta_values:
    bound = qc_param_bell.assign_parameters({theta_param: t})
    bound.measure([0,1],[0,1])
    # YOUR CODE HERE: simulate and collect P(00) and P(11)
    p_00_list.append(np.cos(t/2)**2)  # placeholder
    p_11_list.append(np.sin(t/2)**2)  # placeholder

plt.figure(figsize=(8, 4))
plt.plot(theta_values, p_00_list, "b-o", label="P(|00⟩)")
plt.plot(theta_values, p_11_list, "r-s", label="P(|11⟩)")
plt.xlabel("θ"); plt.ylabel("Probability")
plt.title("Parameterized Bell State: P(|00⟩) + P(|11⟩) = 1 always")
plt.legend(); plt.grid(True, alpha=0.3)
plt.xticks([0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi],
           ["0", "π/4", "π/2", "3π/4", "π"])
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Implement **quantum phase estimation (QPE)** for a 3-qubit controlled-$U$ gate.

QPE estimates the eigenphase $\phi$ of $U|\psi\rangle = e^{2\pi i\phi}|\psi\rangle$ using:
1. $n$ counting qubits in superposition
2. Controlled-$U^{2^k}$ operations ($k = 0, 1, \ldots, n-1$)
3. Inverse QFT
4. Measurement → binary approximation to $\phi$

Test with $U = T$ gate (which has eigenvalue $e^{i\pi/4}$, so $\phi = 1/8$).
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Quantum Phase Estimation for T gate
# T gate eigenvalue: e^{iπ/4} → phase φ = 1/8 (since T|1⟩ = e^{iπ/4}|1⟩)

n_count = 3   # precision qubits (2^3 = 8 precision levels)
n_eigen = 1   # eigenstate qubit

def build_qpe(n_count, U_gate, eigenstate_prep):
    '''QPE circuit: n_count counting qubits + 1 eigenstate qubit.'''
    qc = QuantumCircuit(n_count + n_eigen, n_count, name="QPE")

    # Step 1: Prepare eigenstate
    eigenstate_prep(qc, n_count)

    # Step 2: H on all counting qubits
    for i in range(n_count):
        qc.h(i)

    # Step 3: Controlled-U^(2^k) for each counting qubit
    # YOUR CODE HERE: apply controlled T^(2^k) using cp gate

    # Step 4: Inverse QFT on counting qubits
    # YOUR CODE HERE: apply QFT inverse

    # Step 5: Measure counting qubits
    qc.measure(range(n_count), range(n_count))
    return qc

# For T gate: eigenstate is |1⟩ (T|1⟩ = e^{iπ/4}|1⟩)
def prep_eigenstate(qc, n_count):
    qc.x(n_count)  # prepare |1⟩ as eigenstate

# YOUR CODE HERE: build and run QPE
print("Challenge: Implement build_qpe() and verify φ ≈ 1/8 (binary: 001)")
print("Expected measurement: '001' with high probability (φ = 1/8 = 0.001 in binary)")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Qiskit Docs: Parameterized Circuits** — `qiskit.circuit.ParameterVector`
2. **Qiskit Docs: Circuit Composition** — `.compose()`, `.append()`, `.tensor()`
3. **Nielsen & Chuang**, Section 5.2 — Quantum phase estimation
4. **Qiskit Circuit Library** — `qiskit.circuit.library` — hundreds of pre-built circuits
5. **"Quantum Computation and Quantum Information"** — Appendix A — circuit diagram conventions
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D3_complex_circuits.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
