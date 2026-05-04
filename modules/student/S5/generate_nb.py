#!/usr/bin/env python3
"""generate_nb.py — Module S5: Quantum Computing in the Real World"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# S5 — Quantum Computing in the Real World
**Track:** Student | **Difficulty:** ⭐⭐☆☆☆ | **Est. Time:** 15 min

| | |
|---|---|
| **Prerequisites** | F1–F4, S1–S4 |
| **Qiskit Modules** | `qiskit`, `qiskit_aer` |
| **Companion Video** | Student Module S5 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Map quantum techniques (superposition, interference, entanglement) to **real applications**
2. Understand the concept of **quantum advantage** and what problems it applies to
3. Identify the **three application domains** most likely to achieve quantum advantage first
4. Run small demonstrations that hint at how full quantum algorithms work
5. Honestly assess where quantum is **not** advantageous today
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Concept Summary

### Three Quantum Application Domains

**1. Optimization** — Finding the best solution among exponentially many options
- Classical: check each option (O(N) to O(2ⁿ))
- Quantum: Grover's O(√N), QAOA for combinatorial problems
- Example: drug delivery route optimization, supply chain

**2. Simulation** — Modeling quantum systems (molecules, materials)
- Classical: exponential memory needed for quantum chemistry
- Quantum: natural representation — 1 qubit per physical qubit
- Example: simulating catalyst molecules for green hydrogen production

**3. Cryptography** — Security protocols
- Quantum threat: Shor's algorithm breaks RSA in polynomial time
- Quantum defense: QKD (quantum key distribution) — provably secure
- Example: IBM and NSA preparing for post-quantum cryptography

### Quantum Advantage — The Honest Picture

Quantum advantage means: **quantum beats the best classical algorithm on the same task**.

Today (2024–2025):
- ✓ Quantum chemistry simulations (small molecules, early advantage)
- ✓ Quantum random number generation
- ✗ General machine learning (classical still wins)
- ✗ Optimization in practice (NISQ noise is too high)
- ✗ Breaking encryption (needs millions of error-corrected qubits)

> **Analogy:** A supercar on a race track vs in city traffic — the car's potential is clear, but you need the right conditions to realize it.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Application 1 — Grover Search: Finding One in a Million"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

sim = AerSimulator()

# Demonstrate Grover's advantage: classical O(N) vs quantum O(√N)
n_list = [2**k for k in range(2, 16)]  # database sizes

classical_queries = np.array(n_list, dtype=float)          # O(N/2) average
quantum_queries   = np.sqrt(np.array(n_list, dtype=float)) # O(√N)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Linear scale
ax = axes[0]
ax.plot(n_list, classical_queries / 1e3, "b-o", lw=2, ms=5, label="Classical: O(N)")
ax.plot(n_list, quantum_queries / 1e3, "r-s", lw=2, ms=5, label="Grover's: O(√N)")
ax.set_xlabel("Database Size N"); ax.set_ylabel("Queries needed (thousands)")
ax.set_title("Classical vs Grover's Search\n(linear scale)", fontsize=12, fontweight="bold")
ax.legend(); ax.grid(True, alpha=0.3)

# Log-log scale
ax2 = axes[1]
ax2.loglog(n_list, classical_queries, "b-o", lw=2, ms=5, label="Classical: O(N)")
ax2.loglog(n_list, quantum_queries, "r-s", lw=2, ms=5, label="Grover's: O(√N)")
ax2.set_xlabel("Database Size N"); ax2.set_ylabel("Queries needed")
ax2.set_title("Classical vs Grover's Search\n(log-log scale — slope difference is the speedup)",
              fontsize=12, fontweight="bold")
ax2.legend(); ax2.grid(True, which="both", alpha=0.3)

# Annotate speedup at N=10^6
n_demo = 1e6
speedup = np.sqrt(n_demo)
ax2.annotate(f"N=10⁶: Speedup = {speedup:.0f}×",
             xy=(n_demo, speedup), fontsize=10, color="darkred",
             xytext=(n_demo/10, speedup*5),
             arrowprops=dict(arrowstyle="->", color="darkred"))

plt.suptitle("Grover's Algorithm: Quadratic Quantum Speedup for Unstructured Search",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("grover_scaling.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Application 2 — Quantum Chemistry: Molecular Energy"""))

cells.append(nbf.v4.new_code_cell(r"""# Quantum chemistry memory scaling: why quantum simulation wins

# Classical: full configuration interaction (FCI) — exponential
# Quantum: VQE — polynomial circuit depth

n_electrons = np.arange(2, 30, 2)
n_basis     = n_electrons * 3  # rough approximation: 3 basis functions per electron

classical_memory = 2**n_basis          # FCI Hamiltonian dimensions
quantum_qubits   = n_basis.astype(float)  # 1 qubit per spin orbital

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
mask = classical_memory < 1e18
ax.semilogy(n_electrons[mask], classical_memory[mask], "b-o", lw=2, ms=6,
            label="Classical FCI memory (exponential)")
ax.set_xlabel("Number of Electrons"); ax.set_ylabel("Memory required (bytes)")
ax.set_title("Classical Quantum Chemistry:\nExponential Wall", fontsize=12, fontweight="bold")
ax.axhline(1e12, ls="--", color="red", label="Petabyte supercomputer limit")
ax.legend(); ax.grid(True, which="both", alpha=0.3)
ax.text(8, 1e13, "Current\nsupercomputers\ncan't go\nbeyond here",
        fontsize=9, color="red", ha="center")

ax2 = axes[1]
molecules = {
    "H₂": (2, "Known\nexact"),
    "LiH": (4, "VQE\n2016"),
    "BeH₂": (6, "VQE\n2017"),
    "H₂O": (8, "~50 qubits"),
    "N₂": (14, "~100 qubits"),
    "Caffeine": (44, "~1000 qubits\n(fault-tolerant)"),
    "Penicillin": (120, "Millions of\nqubits needed"),
}
mols = list(molecules.keys())
qubits = [v[0]*3 for v in molecules.values()]
notes  = [v[1] for v in molecules.values()]
colors = ["#4CAF50"]*3 + ["#FFC107"]*2 + ["#FF5722"]*2

bars = ax2.barh(mols, qubits, color=colors, edgecolor="black")
for bar, note in zip(bars, notes):
    ax2.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
             note, va="center", fontsize=8)
ax2.set_xlabel("Approximate Qubits Needed"); ax2.set_xlim(0, 450)
ax2.set_title("Quantum Chemistry: Molecules vs Qubit Requirements\n"
              "Green = achievable today, Yellow = near-term, Red = fault-tolerant era",
              fontsize=11, fontweight="bold")

plt.suptitle("Quantum Chemistry: The Killer App for Quantum Computing",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("quantum_chemistry_scaling.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Application Map — Technique to Application"""))

cells.append(nbf.v4.new_code_cell(r"""# Application mapping table
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

applications = [
    ("Drug Discovery",       "Quantum Chemistry",  "Interference + Entanglement", "#E8F5E9", "#2E7D32"),
    ("Materials Science",    "Quantum Simulation", "Entanglement",                 "#E3F2FD", "#1565C0"),
    ("Supply Chain",         "Optimization",       "Grover's + QAOA",              "#FFF9C4", "#F57F17"),
    ("Finance",              "Monte Carlo",        "Amplitude Estimation",         "#FFF9C4", "#F57F17"),
    ("Machine Learning",     "QML",                "Feature Maps + Interference",  "#F3E5F5", "#6A1B9A"),
    ("Cryptography",         "QKD + Shor's",       "Entanglement + Superposition", "#FCE4EC", "#B71C1C"),
    ("Climate Modeling",     "Simulation",         "Quantum Advantage (future)",   "#E0F7FA", "#006064"),
]

fig, ax = plt.subplots(figsize=(14, 7))
ax.axis("off")

headers = ["Application Domain", "Quantum Approach", "Key Quantum Resource", "Timeline"]
timelines = ["5–10 years", "5–10 years", "3–7 years", "3–7 years", "7+ years", "Now + 10 years", "10+ years"]

for i, (app, approach, resource, facecolor, edgecolor) in enumerate(applications):
    y = 0.93 - i * 0.125
    # Row background
    rect = plt.Rectangle((0, y-0.055), 1, 0.11,
                          transform=ax.transAxes, facecolor=facecolor,
                          edgecolor=edgecolor, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(0.01, y, app,      transform=ax.transAxes, fontsize=11, fontweight="bold", va="center")
    ax.text(0.27, y, approach, transform=ax.transAxes, fontsize=10, va="center")
    ax.text(0.52, y, resource, transform=ax.transAxes, fontsize=10, va="center", style="italic")
    ax.text(0.80, y, timelines[i], transform=ax.transAxes, fontsize=10, va="center",
            color=edgecolor, fontweight="bold")

# Header
for x, header in zip([0.01, 0.27, 0.52, 0.80], headers):
    ax.text(x, 0.97, header, transform=ax.transAxes, fontsize=12,
            fontweight="bold", color="black", va="center")

ax.axhline(0.945, color="black", lw=1.5, transform=ax.transAxes)
ax.set_title("Quantum Computing Application Map: Where Advantage Is Expected",
             fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig("application_map.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 The Honest Scorecard: Where Are We Today?"""))

cells.append(nbf.v4.new_code_cell(r"""# Realistic assessment of current quantum computing status
status_data = {
    "Quantum Key Distribution (QKD)":   ("Deployed", 1.0, "#4CAF50"),
    "Quantum Random Numbers":            ("Deployed", 1.0, "#4CAF50"),
    "Small Molecule VQE (H₂, LiH)":     ("Early advantage", 0.7, "#8BC34A"),
    "Quantum Error Correction (concepts)":("Demonstrated", 0.6, "#CDDC39"),
    "Grover's (3-5 qubits)":             ("Demonstrated", 0.55, "#CDDC39"),
    "NISQ Optimization (QAOA)":          ("Research stage", 0.35, "#FFC107"),
    "Quantum ML (practical advantage)":  ("Unproven", 0.2, "#FF9800"),
    "Shor's (large RSA keys)":           ("Far future", 0.05, "#F44336"),
    "Drug molecule simulation":          ("Far future", 0.05, "#F44336"),
}

fig, ax = plt.subplots(figsize=(12, 7))
labels = list(status_data.keys())
readiness = [v[1] for v in status_data.values()]
colors    = [v[2] for v in status_data.values()]
statuses  = [v[0] for v in status_data.values()]

bars = ax.barh(labels, readiness, color=colors, edgecolor="black", height=0.6)
ax.axvline(0.5, ls="--", color="navy", lw=1.5, label="Practical threshold")
for bar, status in zip(bars, statuses):
    ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
            status, va="center", fontsize=9, fontweight="bold")
ax.set_xlabel("Technology Readiness Level (0 = theoretical, 1 = deployed)")
ax.set_title("Honest Quantum Readiness Assessment — 2024/2025\n"
             "Red = far future | Orange = research | Yellow = demonstrated | Green = deployed",
             fontsize=12, fontweight="bold")
ax.set_xlim(0, 1.4)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("quantum_readiness.png", dpi=120, bbox_inches="tight")
plt.show()

print("Key takeaway: Quantum is real and progressing, but hype outpaces reality.")
print("Focus on domains where the physics gives a genuine structural advantage.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Application Matching

Match each quantum algorithm to the application domain where it provides the most advantage.

```
Algorithms:              Applications:
A. Shor's algorithm      1. Searching a database
B. Grover's algorithm    2. Breaking encryption
C. VQE                   3. Simulating molecules
D. QKD                   4. Secure communication
E. QAOA                  5. Combinatorial optimization
```
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — fill in your answers
answers = {
    "Shor's algorithm":    "???",  # application number
    "Grover's algorithm":  "???",
    "VQE":                 "???",
    "QKD":                 "???",
    "QAOA":                "???",
}

correct = {
    "Shor's algorithm":    "2",
    "Grover's algorithm":  "1",
    "VQE":                 "3",
    "QKD":                 "4",
    "QAOA":                "5",
}

score = sum(1 for alg in answers if answers[alg] == correct[alg])
print(f"Score: {score}/5")
for alg, ans in answers.items():
    check = "✓" if ans == correct[alg] else f"✗ (correct: {correct[alg]})"
    print(f"  {check}  {alg} → application {ans}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Quantum Speedup Analysis

For a database with $N = 10^{12}$ entries (1 trillion):
1. How many queries does classical search need (average)?
2. How many does Grover's need?
3. If each query takes 1 nanosecond, how long does each take?
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE
N = 10**12
ns_per_second = 1e9  # 1 ns = 1e-9 seconds

# Classical (average case: N/2 queries)
classical_queries = None  # YOUR CODE HERE
classical_time_s  = None  # YOUR CODE HERE

# Grover's (O(√N) queries)
grover_queries = None  # YOUR CODE HERE
grover_time_s  = None  # YOUR CODE HERE

print(f"Database size: N = {N:.2e}")
print(f"\nClassical search:")
print(f"  Queries needed: {classical_queries:.2e}")
print(f"  Time: {classical_time_s:.2f} seconds")
print(f"\nGrover's search:")
print(f"  Queries needed: {grover_queries:.2e}")
print(f"  Time: {grover_time_s:.4f} seconds")
print(f"\nSpeedup: {classical_time_s/grover_time_s:.1f}×")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Research and present a case study for **one specific real-world quantum computing project** in 2024:

1. Company/Research group
2. Problem being solved
3. Quantum technique used
4. Number of qubits used
5. Result achieved vs classical baseline
6. Timeline to practical advantage

Present as a formatted output from a Python dictionary.
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Fill in a real quantum project case study
# Research a recent project from IBM, Google, IonQ, Quantinuum, or a university

case_study = {
    "project_name":     "YOUR ANSWER HERE",
    "organization":     "YOUR ANSWER HERE",
    "problem":          "YOUR ANSWER HERE",
    "quantum_technique":"YOUR ANSWER HERE",
    "qubits_used":      0,  # number
    "result":           "YOUR ANSWER HERE",
    "classical_baseline":"YOUR ANSWER HERE",
    "year":             2024,
    "timeline_to_practical": "YOUR ANSWER HERE",
}

print("=== Quantum Computing Case Study ===")
for key, value in case_study.items():
    print(f"{key:30s}: {value}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **IBM Quantum Roadmap 2025** — ibm.com/quantum — Shows planned qubit milestones
2. **Nature: "Quantum advantage" papers** — Search for "quantum advantage 2024" on nature.com
3. **McKinsey Report** — "Quantum Technology Monitor" — Business application timelines
4. **arXiv:2409.xxxxx** — Recent VQE and quantum chemistry benchmarks
5. **NIST Post-Quantum Cryptography** — nist.gov/pqcrypto — Standards for quantum-safe encryption
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "S5_quantum_real_world.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
