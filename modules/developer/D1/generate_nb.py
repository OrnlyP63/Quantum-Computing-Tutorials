#!/usr/bin/env python3
"""generate_nb.py — Module D1: Quantum Computing for Python Developers"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# D1 — Quantum Computing for Python Developers
**Track:** Developer | **Difficulty:** ⭐⭐☆☆☆ | **Est. Time:** 25 min

| | |
|---|---|
| **Prerequisites** | F1–F4; Python proficiency; data structures |
| **Qiskit Modules** | `qiskit`, `qiskit_aer`, `qiskit.quantum_info` |
| **Companion Video** | Developer Module D1 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Map **classical programming constructs** to quantum equivalents (variables→qubits, functions→gates)
2. Build a 10-line Qiskit circuit, draw it, simulate it, and parse the histogram
3. Understand the Qiskit **object model**: `QuantumCircuit`, `QuantumRegister`, `ClassicalRegister`
4. Read circuit metadata: depth, gate count, qubit connectivity
5. Use `Statevector` as a **debugging tool** (analogous to `print()` in classical debugging)
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Classical → Quantum Bridge

| Classical Concept | Quantum Equivalent | Qiskit Object |
|---|---|---|
| Variable (`int`, `bool`) | Qubit state $\|\psi\rangle$ | `QuantumRegister` qubit |
| Array/List | Quantum register | `QuantumRegister(n)` |
| Function | Quantum gate | `gate(qubit)` method |
| Output/Return | Measurement result | `ClassicalRegister` + `.measure()` |
| Program | Quantum circuit | `QuantumCircuit` |
| `if/else` | Conditional gate | `if_test()` context manager |
| Subprocess | Sub-circuit | `QuantumCircuit.compose()` |
| API endpoint | Backend | `AerSimulator` / IBM backend |

### Paradigm Shift

Classical: **deterministic** computation on bits. Run → get same answer every time.

Quantum: **probabilistic** computation on superpositions. Run many times → probability distribution over answers. Extract information via Born rule.

This is not a bug — it is the feature. The trick is designing circuits so the **correct answer has high probability**.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 First Circuit in 10 Lines"""))

cells.append(nbf.v4.new_code_cell(r"""from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
import numpy as np

# Line 1: Create registers (like declaring variables)
qr = QuantumRegister(2, name="q")   # 2 qubits, named "q"
cr = ClassicalRegister(2, name="c") # 2 classical bits for readout

# Line 2: Create circuit (like defining a function)
qc = QuantumCircuit(qr, cr, name="Developer Hello")

# Lines 3–5: Apply gates (like function calls)
qc.h(qr[0])        # Hadamard on q[0]
qc.cx(qr[0], qr[1])  # CNOT: q[0] → q[1]

# Line 6: Measure (like return statement)
qc.measure(qr, cr)

# Line 7: Instantiate backend (like connecting to an API)
sim = AerSimulator()

# Lines 8–10: Run, get counts, inspect
job   = sim.run(transpile(qc, sim), shots=4096)
counts = job.result().get_counts()

print("Circuit:")
print(qc.draw(output="text"))
print(f"\nResult: {counts}")
print(f"Depth: {qc.depth()}, Gates: {qc.count_ops()}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Debugging with Statevector (The Quantum `print()`"""))

cells.append(nbf.v4.new_code_cell(r"""# In classical code you use print() to inspect variable state mid-execution
# In quantum, you use Statevector to inspect the quantum state (without measurement)

qc_debug = QuantumCircuit(2, name="Debug Demo")
qc_debug.h(0)
qc_debug.cx(0, 1)

# "Print" the intermediate quantum state — only possible on simulator
sv = Statevector(qc_debug)

print("=== Quantum State Inspector (Statevector Debug) ===")
print(f"State dimension: {len(sv)}")
print(f"Number of qubits: {sv.num_qubits}")
print()

basis = ["|00⟩", "|01⟩", "|10⟩", "|11⟩"]
for b, amp in zip(basis, sv.data):
    prob = abs(amp)**2
    bar  = "█" * int(prob * 40)
    print(f"  {b}: amp = {amp:>8.4f}  |amp|² = {prob:.4f}  {bar}")

print(f"\nEntanglement: {'Entangled' if not sv.is_valid() else 'Valid state'}")
from qiskit.quantum_info import entropy
ent = entropy(sv)
print(f"Von Neumann entropy (qubit 0): not directly computed here — use partial_trace")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Circuit Anatomy — Developer Perspective"""))

cells.append(nbf.v4.new_code_cell(r"""# Inspect circuit metadata — like reading code documentation
qc_full = QuantumCircuit(3, 3, name="Circuit Metadata Demo")
qc_full.h(0); qc_full.h(1)
qc_full.cx(0, 2); qc_full.cx(1, 2)
qc_full.t(0); qc_full.s(1)
qc_full.measure([0,1,2],[0,1,2])

print("=== Circuit Metadata ===")
print(f"Name:         {qc_full.name}")
print(f"Qubits:       {qc_full.num_qubits}")
print(f"Clbits:       {qc_full.num_clbits}")
print(f"Depth:        {qc_full.depth()}")
print(f"Gate count:   {dict(qc_full.count_ops())}")
print(f"Instructions: {[(instr.operation.name, [qr.index for qr in instr.qubits]) for instr in qc_full.data[:6]]}")

print("\nCircuit:")
print(qc_full.draw(output="text"))

# Transpile and inspect backend-native circuit
from qiskit import transpile
qc_t = transpile(qc_full, sim, optimization_level=1)
print(f"\nAfter transpile (opt_level=1):")
print(f"  Depth: {qc_t.depth()}")
print(f"  Gates: {dict(qc_t.count_ops())}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Qiskit Object Model — Class Hierarchy"""))

cells.append(nbf.v4.new_code_cell(r"""import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Visualize the Qiskit object hierarchy
fig, ax = plt.subplots(figsize=(14, 6))
ax.axis("off")

hierarchy = [
    # (label, x_center, y, width, color)
    ("QuantumCircuit", 7, 5.2, 3.5, "#E3F2FD", "#1565C0"),
    ("QuantumRegister", 3, 3.8, 2.8, "#E8F5E9", "#2E7D32"),
    ("ClassicalRegister", 7, 3.8, 2.8, "#FFF9C4", "#F57F17"),
    ("Gate / Instruction", 11, 3.8, 2.8, "#FCE4EC", "#B71C1C"),
    ("Qubit", 2, 2.4, 2.0, "#C8E6C9", "#388E3C"),
    ("Clbit", 7, 2.4, 2.0, "#FFF176", "#FBC02D"),
    ("Unitary (matrix)", 11, 2.4, 2.0, "#FFCDD2", "#D32F2F"),
    ("AerSimulator / IBMBackend", 7, 0.8, 3.5, "#F3E5F5", "#6A1B9A"),
]

for label, x, y, w, fc, ec in hierarchy:
    rect = plt.Rectangle((x - w/2, y - 0.4), w, 0.8, linewidth=2,
                         edgecolor=ec, facecolor=fc, transform=ax.transData)
    ax.add_patch(rect)
    ax.text(x, y, label, ha="center", va="center", fontsize=10,
            fontweight="bold", color=ec)

# Arrows
arrows = [(7,4.8,7,4.2), (7,3.4,7,1.2), (3,3.4,2,2.8), (7,3.4,7,2.8), (11,3.4,11,2.8)]
for x1,y1,x2,y2 in arrows:
    ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))

ax.set_xlim(0,14); ax.set_ylim(0,6)
ax.set_title("Qiskit 1.x Object Model — Key Classes and Relationships",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("qiskit_object_model.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Parse Results Programmatically

Write a function that takes a `counts` dictionary and returns:
- The most probable outcome
- Its probability
- Whether the result is consistent with a Bell state (only 00 and 11 allowed)
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE

def analyze_counts(counts: dict) -> dict:
    '''
    Analyze measurement counts from a quantum circuit.
    Returns: most probable outcome, its probability, Bell state check.
    '''
    total = sum(counts.values())
    # YOUR CODE HERE
    most_probable = None  # max(counts, key=counts.get)
    prob_most = None      # counts[most_probable] / total

    # Bell state: only "00" and "11" should appear
    is_bell = None  # all(k in ["00","11"] for k in counts.keys())

    return {
        "most_probable": most_probable,
        "probability":   prob_most,
        "is_bell_state": is_bell,
        "entropy_bits":  None,  # -sum(p*log2(p) for p in probs if p>0)
    }

# Test with Bell state counts
test_counts = {"00": 2048, "11": 2048}
result = analyze_counts(test_counts)
print("Bell state analysis:", result)

# Test with non-Bell counts
test_counts2 = {"00": 1000, "01": 500, "10": 300, "11": 1200}
result2 = analyze_counts(test_counts2)
print("Mixed state analysis:", result2)
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Circuit Factory

Write a function `make_ghz(n)` that creates an $n$-qubit GHZ state circuit.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE

def make_ghz(n: int) -> QuantumCircuit:
    '''Create an n-qubit GHZ state circuit.'''
    qc = QuantumCircuit(n, n, name=f"GHZ-{n}")
    # YOUR CODE HERE
    # H on qubit 0
    # CNOT chain: 0→1, 1→2, ..., (n-2)→(n-1)
    # Measure all
    return qc

# Test for n = 2, 3, 4, 5
for n in [2, 3, 4, 5]:
    qc_ghz = make_ghz(n)
    job = sim.run(transpile(qc_ghz, sim), shots=1000)
    counts_g = job.result().get_counts()
    all_zeros = "0" * n
    all_ones  = "1" * n
    p_ghz = (counts_g.get(all_zeros, 0) + counts_g.get(all_ones, 0)) / 1000
    print(f"GHZ-{n}: P(|{'0'*n}⟩ + |{'1'*n}⟩) = {p_ghz:.3f}  (expected ~1.0)")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Build a **quantum random number generator** (QRNG) API in Python:

```python
def quantum_random_int(min_val: int, max_val: int, shots: int = 1) -> list[int]:
    '''Generate quantum random integers in [min_val, max_val] using superposition.'''
    ...
```

Requirements:
1. Determine how many qubits are needed to represent the range
2. Put all qubits in superposition (H gate on each)
3. Measure to get a random bitstring
4. Convert to an integer in the desired range
5. Return a list of `shots` random integers
6. Verify the distribution is uniform with a chi-square test
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Quantum Random Number Generator
from scipy import stats
import numpy as np

def quantum_random_int(min_val: int, max_val: int, shots: int = 100) -> list:
    '''YOUR CODE HERE'''
    n_values = max_val - min_val + 1
    n_bits   = int(np.ceil(np.log2(n_values)))
    # YOUR CODE HERE: build circuit, simulate, convert bitstrings to integers
    return []

# Test
samples = quantum_random_int(0, 7, shots=1000)
print(f"Generated {len(samples)} samples")
print(f"Range: [{min(samples)}, {max(samples)}]")

# Chi-square uniformity test
# YOUR CODE HERE
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Qiskit API Docs** — `QuantumCircuit` class: [https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.QuantumCircuit](https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.QuantumCircuit)
2. **Qiskit 1.x Migration Guide** — If you've used Qiskit before version 1.0
3. **IBM Quantum: Getting Started** — [https://quantum.ibm.com](https://quantum.ibm.com)
4. **Qiskit Patterns** — IBM's best-practice workflow guide for quantum programs
5. **"Programming Quantum Computers"** — Johnston, Harrigan & Gimeno-Segovia (O'Reilly)
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1_quantum_for_python_devs.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
