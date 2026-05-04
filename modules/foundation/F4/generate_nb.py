#!/usr/bin/env python3
"""generate_nb.py — Module F4: How to Use This Series"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# F4 — How to Use This Series
**Track:** Foundation (All Audiences) | **Difficulty:** ⭐☆☆☆☆ | **Est. Time:** 20 min

| | |
|---|---|
| **Prerequisites** | F1, F2, F3 completed |
| **Qiskit Modules** | All packages (environment verification) |
| **Companion Video** | Foundation Module F4 |

---
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Verify your **complete Qiskit environment** is properly configured
2. Understand the **track system** and select the right path for your background
3. Know the **notebook structure** so you can navigate any module efficiently
4. Run the **full pipeline**: circuit → simulation → visualization — end to end
5. Understand how to use the **IBM Quantum Platform** when you're ready for real hardware
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Track Selection Guide

```
Have you completed F1–F3? → YES → Read the guide below to pick your track
                          → NO  → Go back and complete Foundation modules first
```

| Your Background | Recommended Track | Start Module |
|---|---|---|
| Student / Curious beginner — algebra level | 🎓 **Student Track** | S1 |
| Python developer / Software engineer | 💻 **Developer Track** | D1 |
| Data scientist / ML practitioner | 📊 **Data Scientist Track** | DS1 |
| Electrical / Systems engineer | ⚙️ **Engineer Track** | E1 |

**Tracks are independent** — you can complete them in any order, or jump between them once you've done Foundation.

### What Each Track Assumes You Already Know

| Track | Math | Programming | Physics |
|---|---|---|---|
| Student | Basic algebra | None required | None required |
| Developer | Linear algebra helpful | Python fluency required | None required |
| Data Scientist | NumPy/linear algebra | sklearn/numpy required | None required |
| Engineer | Linear algebra, signals | Python required | Quantum mechanics helpful |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Full Environment Check — Run Every Cell"""))

cells.append(nbf.v4.new_code_cell(r"""import sys, importlib, subprocess
from datetime import datetime

print("=" * 60)
print("  QUANTUM COMPUTING SERIES — ENVIRONMENT CHECK")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
print(f"\nPython: {sys.version}")
print(f"Platform: {sys.platform}")

REQUIRED = {
    "qiskit":                 "1.0.0",
    "qiskit_aer":             "0.14.0",
    "numpy":                  "1.24.0",
    "matplotlib":             "3.7.0",
    "scipy":                  "1.10.0",
    "jupyter":                "1.0.0",
}

OPTIONAL = {
    "qiskit_ibm_runtime":     "0.20.0",
    "qiskit_machine_learning":"0.7.0",
    "torch":                  "2.0.0",
    "sklearn":                "1.3.0",
}

def check_pkg(name, min_ver):
    try:
        mod = importlib.import_module(name)
        ver = getattr(mod, "__version__", "unknown")
        return "✓", ver
    except ImportError:
        return "✗", "NOT INSTALLED"

print("\n--- Required Packages ---")
all_ok = True
for pkg, minv in REQUIRED.items():
    status, ver = check_pkg(pkg, minv)
    if status == "✗":
        all_ok = False
    print(f"  {status}  {pkg:35s} {ver}")

print("\n--- Optional Packages (needed for specific tracks) ---")
for pkg, minv in OPTIONAL.items():
    status, ver = check_pkg(pkg, minv)
    print(f"  {status}  {pkg:35s} {ver}")

print("\n" + "=" * 60)
if all_ok:
    print("  ✓  ALL REQUIRED PACKAGES PRESENT — READY TO GO!")
else:
    print("  ✗  SOME PACKAGES MISSING")
    print("     Run: pip install qiskit qiskit-aer matplotlib scipy jupyter")
print("=" * 60)
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Full Pipeline Smoke Test

This cell runs the **complete workflow** from circuit design to result visualization. If this passes, your environment is fully operational.
"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

print("Running full pipeline test...")

# ---- 1. Design a 2-qubit Bell state circuit ----
qc = QuantumCircuit(2, 2, name="Bell State Smoke Test")
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

# ---- 2. Simulate ----
sim = AerSimulator()
qc_t = transpile(qc, sim)
result = sim.run(qc_t, shots=4096).result()
counts = result.get_counts()

# ---- 3. Verify correctness ----
total = sum(counts.values())
p00 = counts.get("00", 0) / total
p11 = counts.get("11", 0) / total
p01 = counts.get("01", 0) / total
p10 = counts.get("10", 0) / total

print(f"\nCircuit: {qc.name}")
print(f"Counts: {counts}")
print(f"\nP(00) = {p00:.3f}  (expected ≈ 0.5)")
print(f"P(11) = {p11:.3f}  (expected ≈ 0.5)")
print(f"P(01) = {p01:.3f}  (expected ≈ 0.0)")
print(f"P(10) = {p10:.3f}  (expected ≈ 0.0)")

# ---- 4. Visualize ----
fig, axes = plt.subplots(1, 2, figsize=(13, 4))

# Circuit diagram
from qiskit.visualization import circuit_drawer
axes[0].axis("off")
axes[0].text(0.5, 0.5, str(qc.draw(output="text")),
             transform=axes[0].transAxes, fontfamily="monospace",
             fontsize=10, va="center", ha="center",
             bbox=dict(boxstyle="round", facecolor="#E8F5E9", alpha=0.8))
axes[0].set_title("Circuit: Bell State (H + CNOT)", fontsize=12, fontweight="bold")

# Histogram
outcomes = sorted(counts.keys())
vals = [counts.get(k, 0) for k in outcomes]
colors = ["#2196F3" if k in ["00", "11"] else "#FFCDD2" for k in outcomes]
bars = axes[1].bar(outcomes, vals, color=colors, edgecolor="black", width=0.5)
for bar in bars:
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                 f"{bar.get_height()/total*100:.1f}%", ha="center", fontsize=12)
axes[1].set_title("Measurement Histogram (4096 shots)", fontsize=12, fontweight="bold")
axes[1].set_ylabel("Count"); axes[1].set_ylim(0, total * 0.7)

plt.suptitle("✓ Full Pipeline Working: Design → Simulate → Visualize", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("smoke_test.png", dpi=120, bbox_inches="tight")
plt.show()

# ---- 5. Final verdict ----
passed = (abs(p00 - 0.5) < 0.05 and abs(p11 - 0.5) < 0.05
          and p01 < 0.05 and p10 < 0.05)
print(f"\n{'✓ SMOKE TEST PASSED' if passed else '✗ SMOKE TEST FAILED'}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Notebook Navigation Guide"""))

cells.append(nbf.v4.new_code_cell(r"""# Print the series content map
SERIES_MAP = {
    "Foundation": {
        "F1": ("What is Quantum Computing?", "⭐", "No code — pure concepts"),
        "F2": ("Why Qiskit?",                "⭐", "First circuit"),
        "F3": ("Qubits, States & Measurement","⭐⭐", "Statevector + Bloch sphere"),
        "F4": ("How to Use This Series",      "⭐", "Environment check"),
    },
    "Student Track": {
        "S1": ("Bits, Qubits & Superposition", "⭐⭐", "H gate, measurement"),
        "S2": ("Quantum Gates",                 "⭐⭐", "X, H, Z on Bloch sphere"),
        "S3": ("Entanglement",                  "⭐⭐", "Bell states"),
        "S4": ("Your First Quantum Circuit",    "⭐⭐⭐", "Multi-gate circuit"),
        "S5": ("Quantum in the Real World",     "⭐⭐", "Applications survey"),
    },
    "Developer Track": {
        "D1": ("Quantum for Python Devs",       "⭐⭐", "Full Qiskit API"),
        "D2": ("Gates as Matrix Ops",           "⭐⭐⭐", "Unitary matrices"),
        "D3": ("Complex Circuits",              "⭐⭐⭐", "Registers, composition"),
        "D4": ("Deutsch-Jozsa Algorithm",       "⭐⭐⭐⭐", "Oracle problem"),
        "D5": ("Grover's Search",               "⭐⭐⭐⭐", "Amplitude amplification"),
        "D6": ("IBM Quantum Hardware",          "⭐⭐⭐", "Real backend jobs"),
    },
    "Data Scientist Track": {
        "DS1": ("QML Big Picture",              "⭐⭐", "VQC vs classical NN"),
        "DS2": ("Data Encoding",                "⭐⭐⭐", "Feature maps"),
        "DS3": ("VQC",                          "⭐⭐⭐⭐", "Training loop"),
        "DS4": ("Quantum Neural Networks",      "⭐⭐⭐⭐", "SamplerQNN + PyTorch"),
        "DS5": ("Quantum Kernels",              "⭐⭐⭐⭐", "SVM with FidelityKernel"),
        "DS6": ("Benchmarking",                 "⭐⭐⭐", "VQC vs classical metrics"),
    },
    "Engineer Track": {
        "E1": ("Hardware Architectures",        "⭐⭐⭐", "Coupling maps"),
        "E2": ("Noise & Decoherence",           "⭐⭐⭐⭐", "Noise models"),
        "E3": ("Transpilation",                 "⭐⭐⭐⭐", "Optimization levels"),
        "E4": ("Pulse-Level Programming",       "⭐⭐⭐⭐⭐", "Qiskit Pulse"),
        "E5": ("Error Mitigation",              "⭐⭐⭐⭐", "ZNE"),
        "E6": ("Quantum Error Correction",      "⭐⭐⭐⭐⭐", "Repetition code"),
    },
}

print("=" * 70)
print("  QUANTUM COMPUTING WITH QISKIT — COMPLETE COURSE MAP")
print("=" * 70)
for track, modules in SERIES_MAP.items():
    print(f"\n  {'─'*50}")
    print(f"  {track.upper()}")
    print(f"  {'─'*50}")
    for code, (title, diff, focus) in modules.items():
        print(f"  [{code:4s}] {diff:6s} {title:40s} ({focus})")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 How Each Notebook Is Structured

Every notebook in this series follows a consistent 7-section layout. Understanding this structure lets you navigate any module efficiently:

```
┌────────────────────────────────────────────────────────────────┐
│  📌 HEADER          — Track | Module | Title | Difficulty      │
│  🎯 OBJECTIVES      — 4–5 measurable "you will be able to..."  │
│  📖 CONCEPTS        — Theory + LaTeX math (read before coding) │
│  💻 GUIDED CODE     — Annotated cells, run in order            │
│  🧪 EXERCISES       — # YOUR CODE HERE cells                   │
│  🏆 CHALLENGE       — Open-ended, no solution provided         │
│  📚 FURTHER READING — 5 curated links                          │
└────────────────────────────────────────────────────────────────┘
```

**How to work through a notebook:**
1. Read the header and objectives to set expectations
2. Read the concept summary *before* running any code
3. Run guided cells in order — don't skip ahead
4. Predict the output before running each visualization cell
5. Complete exercises before looking at the challenge
6. For challenges: spend 15 minutes trying independently first
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercise — Track Self-Assessment

Complete this self-assessment to confirm your track choice.
"""))

cells.append(nbf.v4.new_code_cell(r"""# Self-assessment quiz
questions = [
    ("Can you write a Python function that takes a list and returns its sorted version?",
     "developer", "data_scientist", "engineer"),
    ("Do you know what a dot product is?",
     "developer", "data_scientist", "engineer"),
    ("Have you ever trained a machine learning model?",
     "data_scientist",),
    ("Do you know what a Fourier transform is?",
     "engineer",),
    ("Are you comfortable with complex numbers?",
     "developer", "data_scientist", "engineer"),
]

track_scores = {"student": 0, "developer": 0, "data_scientist": 0, "engineer": 0}

print("Answer each question (y/n):\n")
for i, (q, *tracks) in enumerate(questions, 1):
    print(f"{i}. {q}")
    answer = input("   Your answer (y/n): ").strip().lower()
    if answer == "y":
        for t in tracks:
            track_scores[t] += 1
    print()

print("\nYour track alignment scores:")
for track, score in sorted(track_scores.items(), key=lambda x: -x[1]):
    bar = "█" * score + "░" * (5 - score)
    print(f"  {track:20s} [{bar}] {score}/5")

best = max(track_scores, key=track_scores.get)
print(f"\n→ Recommended track: {best.upper()}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge — Build Your Learning Plan

Create a personal learning schedule for this series. Fill in realistic dates and customize for your track.
"""))

cells.append(nbf.v4.new_code_cell(r"""from datetime import date, timedelta

# YOUR TRACK — modify this
MY_TRACK = "developer"  # Options: student, developer, data_scientist, engineer

TRACK_MODULES = {
    "student":        ["S1","S2","S3","S4","S5"],
    "developer":      ["D1","D2","D3","D4","D5","D6"],
    "data_scientist": ["DS1","DS2","DS3","DS4","DS5","DS6"],
    "engineer":       ["E1","E2","E3","E4","E5","E6"],
}

# Assume 2 modules per week
modules = ["F1","F2","F3","F4"] + TRACK_MODULES[MY_TRACK]
start   = date.today()

print(f"My Learning Plan — Track: {MY_TRACK.upper()}")
print(f"Start date: {start}")
print(f"{'─'*40}")

for i, mod in enumerate(modules):
    week = i // 2 + 1
    day  = start + timedelta(weeks=i // 2, days=(i % 2) * 3)
    print(f"  Week {week:2d} | {day} | {mod}")

end = start + timedelta(weeks=(len(modules)//2) + 1)
print(f"\nEstimated completion: {end}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Qiskit Learning** — [https://learning.quantum.ibm.com](https://learning.quantum.ibm.com) — Official IBM Quantum learning paths
2. **IBM Quantum Platform** — [https://quantum.ibm.com](https://quantum.ibm.com) — Free account, real hardware access
3. **Qiskit Community** — [https://qiskit.slack.com](https://qiskit.slack.com) — Active community Slack workspace
4. **Qiskit Tutorials on GitHub** — `Qiskit/qiskit-tutorials` — hundreds of example notebooks
5. **arXiv quant-ph** — [https://arxiv.org/list/quant-ph/recent](https://arxiv.org/list/quant-ph/recent) — Latest quantum computing research
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "F4_how_to_use_series.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
