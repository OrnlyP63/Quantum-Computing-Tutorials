#!/usr/bin/env python3
"""generate_nb.py — Module F2: Why Qiskit?"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# F2 — Why Qiskit? The Quantum SDK Tour
**Track:** Foundation (All Audiences) | **Difficulty:** ⭐☆☆☆☆ | **Est. Time:** 25 min

| | |
|---|---|
| **Prerequisites** | Python basics, pip familiarity |
| **Qiskit Modules** | `qiskit`, `qiskit_aer` |
| **Companion Video** | Foundation Module F2 |

---
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Describe the **Qiskit ecosystem** and which package serves which purpose
2. Verify a working Qiskit installation and diagnose common setup issues
3. Build and run the canonical **"Hello Qubit"** circuit
4. Read a Qiskit circuit diagram and histogram output
5. Understand the simulation→hardware workflow pipeline
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Qiskit Ecosystem Overview

Qiskit is IBM's open-source SDK for quantum computing. It is organized into **focused packages**:

| Package | Purpose | Key Class |
|---|---|---|
| `qiskit` (Terra) | Circuit building, transpilation, quantum info | `QuantumCircuit`, `transpile` |
| `qiskit_aer` | High-performance local simulators | `AerSimulator` |
| `qiskit_ibm_runtime` | Access to real IBM Quantum hardware | `QiskitRuntimeService` |
| `qiskit_machine_learning` | Quantum ML primitives | `VQC`, `QNNCircuit` |
| `qiskit.pulse` | Pulse-level microwave control | `Schedule`, `Play` |
| `qiskit.visualization` | Circuit diagrams, Bloch spheres, histograms | `plot_histogram` |

### The Workflow

```
Design Circuit      Simulate Locally       Optimize (Transpile)     Run on Hardware
QuantumCircuit  →   AerSimulator       →   transpile(qc, backend) → IBM Quantum Cloud
```

Every notebook in this series follows this pipeline. You design once, test cheaply on a simulator, then optionally run on real quantum hardware.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 1 — Verify Installation"""))

cells.append(nbf.v4.new_code_cell(r"""# Environment verification — run this cell first
import sys
print(f"Python: {sys.version}")

packages = {}

try:
    import qiskit
    packages["qiskit"] = qiskit.__version__
except ImportError:
    packages["qiskit"] = "NOT INSTALLED"

try:
    import qiskit_aer
    packages["qiskit_aer"] = qiskit_aer.__version__
except ImportError:
    packages["qiskit_aer"] = "NOT INSTALLED"

try:
    import numpy as np
    packages["numpy"] = np.__version__
except ImportError:
    packages["numpy"] = "NOT INSTALLED"

try:
    import matplotlib
    packages["matplotlib"] = matplotlib.__version__
except ImportError:
    packages["matplotlib"] = "NOT INSTALLED"

print("\n=== Package Status ===")
for pkg, ver in packages.items():
    status = "✓" if ver != "NOT INSTALLED" else "✗"
    print(f"  {status}  {pkg:30s} {ver}")

missing = [p for p, v in packages.items() if v == "NOT INSTALLED"]
if missing:
    print(f"\nInstall missing: pip install {' '.join(missing)}")
else:
    print("\n✓ All dependencies present — you are ready to go!")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 2 — Hello Qubit

The canonical first quantum circuit: put a qubit in superposition with a **Hadamard gate** and measure it.

The math:
$$|0\rangle \xrightarrow{H} \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \xrightarrow{\text{measure}} \begin{cases} |0\rangle & \text{prob } 1/2 \\ |1\rangle & \text{prob } 1/2 \end{cases}$$
"""))

cells.append(nbf.v4.new_code_cell(r"""from qiskit import QuantumCircuit

# Build the simplest non-trivial quantum circuit
qc = QuantumCircuit(1, 1)  # 1 qubit, 1 classical bit
qc.h(0)                    # Hadamard: creates superposition
qc.measure(0, 0)           # Collapse: read the qubit into the classical register

print("Circuit built:")
print(qc.draw(output="text"))
"""))

cells.append(nbf.v4.new_code_cell(r"""from qiskit_aer import AerSimulator
from qiskit import transpile
import matplotlib.pyplot as plt

# Simulate with AerSimulator (statevector-based, noiseless)
sim = AerSimulator()
qc_t = transpile(qc, sim)
job = sim.run(qc_t, shots=4096)
counts = job.result().get_counts()

print("Raw counts:", counts)

# Visualize
fig, ax = plt.subplots(figsize=(7, 4))
outcomes = sorted(counts.keys())
values   = [counts.get(k, 0) for k in outcomes]
colors   = ["#2196F3" if k == "0" else "#FF5722" for k in outcomes]
bars = ax.bar(outcomes, values, color=colors, edgecolor="black", width=0.4)
ax.set_xlabel("Measurement Outcome", fontsize=13)
ax.set_ylabel("Count (out of 4096 shots)", fontsize=13)
ax.set_title("Hello Qubit: H gate on |0⟩ then Measure\nExpected: ~50/50 split", fontsize=13, fontweight="bold")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
            f"{int(bar.get_height())}\n({bar.get_height()/4096*100:.1f}%)",
            ha="center", fontsize=11)
ax.axhline(2048, ls="--", color="gray", label="Theoretical 50% (2048)")
ax.legend(fontsize=10)
ax.set_ylim(0, 2600)
plt.tight_layout()
plt.savefig("hello_qubit.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 3 — Inspect Statevector (Pre-Measurement)

Before measuring, we can inspect the exact quantum state using `Statevector`. This is only possible on a simulator — hardware collapses the state on every run.
"""))

cells.append(nbf.v4.new_code_cell(r"""from qiskit.quantum_info import Statevector
import numpy as np

# Circuit WITHOUT measurement to inspect statevector
qc_no_meas = QuantumCircuit(1)
qc_no_meas.h(0)

sv = Statevector(qc_no_meas)
print("Statevector after H|0⟩:")
print(sv)
print()
print("Amplitudes (complex):")
for i, amp in enumerate(sv.data):
    print(f"  |{i}⟩: {amp:.4f}  →  prob = {abs(amp)**2:.4f}")

print()
print(f"Normalization check: Σ|αᵢ|² = {sum(abs(a)**2 for a in sv.data):.6f}")

# Show that measurement probabilities come from Born rule
probs = sv.probabilities_dict()
print("\nBorn rule probabilities:", probs)
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 4 — The Qiskit Workflow Diagram"""))

cells.append(nbf.v4.new_code_cell(r"""import matplotlib.pyplot as plt
import matplotlib.patches as FancyBboxPatch

fig, ax = plt.subplots(figsize=(14, 4))
ax.set_xlim(0, 14); ax.set_ylim(0, 4); ax.axis("off")

steps = [
    ("Design\nQuantumCircuit", 1.1, "#E3F2FD", "#1565C0"),
    ("Test\nAerSimulator\n(local, fast)", 3.9, "#E8F5E9", "#2E7D32"),
    ("Optimize\ntranspile()\n(for backend)", 6.7, "#FFF8E1", "#E65100"),
    ("Submit\nIBM Quantum\n(real hardware)", 9.5, "#FCE4EC", "#B71C1C"),
    ("Analyze\nResults\n+ Visualize", 12.3, "#F3E5F5", "#6A1B9A"),
]

for i, (label, x, facecolor, edgecolor) in enumerate(steps):
    box = plt.Rectangle((x - 1.0, 0.7), 2.0, 2.6, linewidth=2,
                         edgecolor=edgecolor, facecolor=facecolor, zorder=2)
    ax.add_patch(box)
    ax.text(x, 2.0, label, ha="center", va="center",
            fontsize=10, fontweight="bold", color=edgecolor, zorder=3)
    if i < len(steps) - 1:
        ax.annotate("", xy=(x + 1.15, 2.0), xytext=(x + 0.95, 2.0),
                    arrowprops=dict(arrowstyle="->", lw=2, color="black"))
        ax.annotate("", xy=(steps[i+1][1] - 1.05, 2.0), xytext=(x + 1.0, 2.0),
                    arrowprops=dict(arrowstyle="->", lw=2, color="black"))

ax.text(7, 0.3, "This notebook covers: Design → Test → Analyze",
        ha="center", fontsize=11, style="italic", color="#555")
ax.set_title("Qiskit Quantum Computing Workflow", fontsize=14, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig("qiskit_workflow.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Circuit Modification

Modify the Hello Qubit circuit to start from $|1\rangle$ instead of $|0\rangle$. Apply an X gate first, then H.

**Predict** the outcome distribution before running.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE
qc_ex1 = QuantumCircuit(1, 1)
# Apply X gate to flip |0⟩ → |1⟩
# YOUR CODE HERE
# Apply H gate
# YOUR CODE HERE
# Measure
# YOUR CODE HERE

# Simulate and plot
# YOUR CODE HERE
print("Predicted: still ~50/50 because H|1⟩ = (|0⟩ - |1⟩)/√2 — same probabilities, different phase!")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Shot Statistics

Run the Hello Qubit circuit with 100, 1000, 10000 shots. Plot how the measured 0-probability converges to 0.5 as shots increase.

This demonstrates the **law of large numbers** in quantum measurement.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE
shot_counts = [100, 500, 1000, 5000, 10000]
p0_measured = []

for shots in shot_counts:
    # YOUR CODE HERE: run qc with `shots` shots, compute P(0)
    pass

# YOUR CODE HERE: plot convergence
plt.figure(figsize=(8, 4))
# plt.plot(shot_counts, p0_measured, 'o-', ...)
# plt.axhline(0.5, ...)
plt.xlabel("Number of Shots"); plt.ylabel("Measured P(|0⟩)")
plt.title("Shot Count vs Measurement Precision")
plt.grid(True, alpha=0.3)
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Build a 2-qubit circuit that creates the state $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$ — **uniform superposition over all 4 basis states**.

Hint: apply H to both qubits independently. Then:
1. Verify using `Statevector` that all amplitudes are $\frac{1}{2}$
2. Simulate with 8192 shots — each of the 4 outcomes should appear ~25% of the time
3. Explain why this is NOT entanglement (product state vs entangled state)
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — YOUR CODE HERE
qc_challenge = QuantumCircuit(2, 2)
# YOUR CODE HERE

sv = Statevector(qc_challenge)
print("Statevector:", sv)
# Simulate and plot histogram
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Qiskit Documentation** — [https://docs.quantum.ibm.com](https://docs.quantum.ibm.com) — Start with "Getting Started"
2. **Qiskit GitHub** — [https://github.com/Qiskit/qiskit](https://github.com/Qiskit/qiskit) — Source code and issue tracker
3. **IBM Quantum Platform** — [https://quantum.ibm.com](https://quantum.ibm.com) — Free account for real hardware access
4. **Qiskit Textbook** — [https://learning.quantum.ibm.com](https://learning.quantum.ibm.com) — Official IBM learning resource
5. **Qiskit Migration Guide (0.x → 1.x)** — Important if working with older tutorials
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "F2_why_qiskit.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
