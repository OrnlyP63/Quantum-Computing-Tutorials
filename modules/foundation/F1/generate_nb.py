#!/usr/bin/env python3
"""generate_nb.py — Module F1: What is Quantum Computing?"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# F1 — What is Quantum Computing?
**Track:** Foundation (All Audiences) | **Difficulty:** ⭐☆☆☆☆ | **Est. Time:** 30 min

| | |
|---|---|
| **Prerequisites** | None — pure curiosity required |
| **Qiskit Modules** | None (visualization only) |
| **Companion Video** | Foundation Module F1 |

---
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

By the end of this notebook you will be able to:

1. Distinguish between **classical bits** and **quantum qubits** using precise language
2. Explain **superposition**, **entanglement**, and **interference** with concrete analogies
3. Interpret a quantum state vector $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ and the normalization constraint
4. Visualize wave interference as the engine behind quantum speedup
5. Map each concept to a real-world quantum computing application
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Concept Summary

### 1. Classical Bits vs Qubits

A classical bit is an *either/or* entity: $b \in \{0, 1\}$. A qubit lives in a **complex vector space** — a 2D Hilbert space $\mathcal{H} = \mathbb{C}^2$. Its state is a unit vector:

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle, \quad \alpha,\beta \in \mathbb{C}, \quad |\alpha|^2 + |\beta|^2 = 1$$

$|\alpha|^2$ is the probability of measuring $|0\rangle$; $|\beta|^2$ of measuring $|1\rangle$. The **Bloch sphere** parameterises this geometrically:

$$|\psi\rangle = \cos\!\frac{\theta}{2}|0\rangle + e^{i\phi}\sin\!\frac{\theta}{2}|1\rangle, \quad \theta \in [0,\pi],\; \phi \in [0, 2\pi)$$

### 2. Superposition

*Before measurement* the qubit simultaneously encodes both outcomes with complex amplitudes. The Hadamard gate produces the canonical equal superposition:

$$H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$$

> **Analogy:** A coin spinning in the air is *not* heads or tails — it is a superposition. Catching it (measuring) collapses it to one outcome.

### 3. Interference

Amplitudes are **complex numbers**, so they add like waves: constructive interference amplifies desired outcomes, destructive interference suppresses wrong ones. This is the core mechanism behind *every* quantum speedup.

$$P(\text{outcome}) = \left|\sum_{\text{paths}} \text{amplitude}\right|^2$$

### 4. Entanglement

Two qubits are entangled when their joint state *cannot* be written as a product $|\psi_A\rangle \otimes |\psi_B\rangle$. The Bell state is:

$$|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$$

Measuring qubit A instantly determines qubit B's state — regardless of distance. Einstein called it "spooky action at a distance."
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Visualization 1 — Classical Bit vs Qubit Probability Space"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# --- Classical bit: discrete probability ---
ax = axes[0]
ax.bar([0, 1], [0.6, 0.4], color=["#2196F3", "#FF5722"], width=0.5, edgecolor="black")
ax.set_xticks([0, 1])
ax.set_xticklabels(["|0⟩", "|1⟩"], fontsize=14)
ax.set_ylabel("Probability", fontsize=12)
ax.set_title("Classical Bit\n(deterministic or random, no phase)", fontsize=13, fontweight="bold")
ax.set_ylim(0, 1.1)
ax.axhline(0.5, ls="--", color="gray", alpha=0.5)
for bar in ax.patches:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
            f"{bar.get_height():.1f}", ha="center", fontsize=12)

# --- Qubit: amplitude in complex plane ---
ax2 = axes[1]
theta = np.pi / 3  # 60 degrees
alpha = np.cos(theta / 2)
beta  = np.sin(theta / 2)
phi   = np.pi / 4  # global relative phase

ax2.bar([0, 1], [alpha**2, beta**2], color=["#4CAF50", "#9C27B0"], width=0.5,
        edgecolor="black", label="Probability $|\\cdot|^2$")
ax2.bar([0, 1], [alpha, beta * np.cos(phi)],
        color=["#81C784", "#CE93D8"], width=0.3, alpha=0.6, label="Real amplitude Re(·)")
ax2.set_xticks([0, 1])
ax2.set_xticklabels(["|0⟩", "|1⟩"], fontsize=14)
ax2.set_ylabel("Value", fontsize=12)
ax2.set_title("Qubit State $|\\psi\\rangle = \\alpha|0\\rangle + e^{i\\phi}\\beta|1\\rangle$\n"
              "(amplitude has phase — enables interference)", fontsize=12, fontweight="bold")
ax2.set_ylim(-0.2, 1.1)
ax2.legend(fontsize=10)
ax2.axhline(0, color="black", lw=0.8)
ax2.text(0.5, -0.18,
         f"Norm check: |α|² + |β|² = {alpha**2 + beta**2:.3f}",
         ha="center", fontsize=11, color="darkgreen")

plt.suptitle("Classical Bit vs Qubit: The Key Difference is the Amplitude",
             fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("bit_vs_qubit.png", dpi=120, bbox_inches="tight")
plt.show()
print("Key insight: the qubit carries PHASE information that enables constructive/destructive interference.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Visualization 2 — Wave Interference: The Engine of Quantum Speedup"""))

cells.append(nbf.v4.new_code_cell(r"""fig, axes = plt.subplots(1, 3, figsize=(16, 5))

x = np.linspace(0, 4 * np.pi, 500)
wave1 = np.sin(x)
wave2 = np.sin(x)           # in phase
wave3 = np.sin(x + np.pi)   # out of phase (destructive)

for i, (w2, title, color, label) in enumerate([
    (wave2,  "Constructive Interference\n(same phase)", "#2196F3",
     "Amplified: $2\\sin(x)$"),
    (wave3,  "Destructive Interference\n(opposite phase)", "#F44336",
     "Cancelled: $\\approx 0$"),
    (np.sin(x + np.pi/3), "Partial Interference\n(phase shift $\\pi/3$)", "#4CAF50",
     "Partial"),
]):
    ax = axes[i]
    ax.plot(x, wave1, "b--", alpha=0.5, lw=1.5, label="Wave 1")
    ax.plot(x, w2, "r--", alpha=0.5, lw=1.5, label="Wave 2")
    ax.plot(x, wave1 + w2, color=color, lw=3, label=label)
    ax.fill_between(x, wave1 + w2, alpha=0.2, color=color)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.set_ylim(-2.5, 2.5)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("Position / Time", fontsize=10)

plt.suptitle("Interference: Quantum Algorithms Amplify Correct Answers and Cancel Wrong Ones",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("interference.png", dpi=120, bbox_inches="tight")
plt.show()
print("This is WHY quantum is powerful: not just parallelism, but INTERFERENCE-GUIDED search.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Visualization 3 — The Bloch Sphere: One Qubit's Complete Universe"""))

cells.append(nbf.v4.new_code_cell(r"""fig = plt.figure(figsize=(10, 9))
ax = fig.add_subplot(111, projection="3d")

# Draw Bloch sphere surface (wireframe)
u = np.linspace(0, 2 * np.pi, 40)
v = np.linspace(0, np.pi, 40)
xs = np.outer(np.cos(u), np.sin(v))
ys = np.outer(np.sin(u), np.sin(v))
zs = np.outer(np.ones_like(u), np.cos(v))
ax.plot_surface(xs, ys, zs, alpha=0.05, color="cyan")
ax.plot_wireframe(xs, ys, zs, alpha=0.08, color="blue", linewidth=0.5)

# Axes and labels
for dx, dy, dz, label in [
    (0, 0, 1.3, "|0⟩ (North Pole)"),
    (0, 0, -1.4, "|1⟩ (South Pole)"),
    (1.3, 0, 0, "|+⟩"),
    (-1.3, 0, 0, "|−⟩"),
    (0, 1.3, 0, "|i⟩"),
    (0, -1.3, 0, "|−i⟩"),
]:
    ax.text(dx, dy, dz, label, fontsize=9, ha="center", color="black")

# Draw axes
for start, end, color in [
    ([0,0,-1.2],[0,0,1.2],"black"),
    ([-1.2,0,0],[1.2,0,0],"black"),
    ([0,-1.2,0],[0,1.2,0],"black"),
]:
    ax.quiver(*start, *(np.array(end)-np.array(start)),
              arrow_length_ratio=0.1, color=color, linewidth=1)

# Plot sample states
states = {
    "|0⟩":  (0, 0, 1),
    "|1⟩":  (0, 0, -1),
    "|+⟩ = H|0⟩": (1, 0, 0),
    "θ=π/3 φ=π/4": (np.sin(np.pi/3)*np.cos(np.pi/4),
                     np.sin(np.pi/3)*np.sin(np.pi/4),
                     np.cos(np.pi/3)),
}
colors = ["blue", "red", "green", "purple"]
for (label, (bx, by, bz)), c in zip(states.items(), colors):
    ax.quiver(0, 0, 0, bx, by, bz, arrow_length_ratio=0.1,
              color=c, linewidth=2.5, label=label)
    ax.scatter([bx], [by], [bz], color=c, s=60, zorder=5)

ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_zlim(-1.5, 1.5)
ax.set_xlabel("X (Re)"); ax.set_ylabel("Y (Im)"); ax.set_zlabel("Z")
ax.set_title("Bloch Sphere: Every Pure Qubit State is a Point on the Unit Sphere\n"
             r"$|\psi\rangle = \cos(\theta/2)|0\rangle + e^{i\phi}\sin(\theta/2)|1\rangle$",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=9, loc="upper left")
plt.tight_layout()
plt.savefig("bloch_sphere.png", dpi=120, bbox_inches="tight")
plt.show()
print("Insight: Classical bit = only north or south pole. Qubit = ANY point on the sphere.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Visualization 4 — Entanglement Correlation"""))

cells.append(nbf.v4.new_code_cell(r"""import random

# Simulate Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2 measurements
np.random.seed(42)
n_shots = 500
# Bell state: when measured, both qubits always agree (both 0 or both 1)
outcomes_A = np.random.randint(0, 2, n_shots)
outcomes_B = outcomes_A.copy()  # perfect correlation

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Panel 1: outcome distribution
ax = axes[0]
joint_counts = {"00": np.sum(outcomes_A == 0), "11": np.sum(outcomes_A == 1),
                "01": 0, "10": 0}
bars = ax.bar(joint_counts.keys(), joint_counts.values(),
              color=["#2196F3", "#4CAF50", "#F44336", "#FF9800"],
              edgecolor="black")
ax.set_title("Bell State $|\\Phi^+\\rangle$ Measurement\n500 shots", fontsize=12, fontweight="bold")
ax.set_ylabel("Count"); ax.set_xlabel("Joint Outcome")
for bar in bars:
    if bar.get_height() > 0:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{int(bar.get_height())}", ha="center", fontsize=11)

# Panel 2: correlation scatter
ax2 = axes[1]
jitter_A = outcomes_A + np.random.normal(0, 0.05, n_shots)
jitter_B = outcomes_B + np.random.normal(0, 0.05, n_shots)
ax2.scatter(jitter_A[:100], jitter_B[:100], alpha=0.3, s=20, color="#9C27B0")
ax2.set_xticks([0, 1]); ax2.set_yticks([0, 1])
ax2.set_xticklabels(["0", "1"]); ax2.set_yticklabels(["0", "1"])
ax2.set_xlabel("Qubit A outcome"); ax2.set_ylabel("Qubit B outcome")
ax2.set_title(f"Correlation: perfect\n(Pearson r = {np.corrcoef(outcomes_A, outcomes_B)[0,1]:.3f})",
              fontsize=12, fontweight="bold")
ax2.set_xlim(-0.3, 1.3); ax2.set_ylim(-0.3, 1.3)

# Panel 3: classical vs quantum correlation achievable
ax3 = axes[2]
categories = ["Max Classical\n(local hidden var)", "Bell Inequality\nBound (CHSH=2)",
               "Quantum\nViolation (CHSH≈2.83)"]
values = [2.0, 2.0, 2.83]
colors = ["#90A4AE", "#FFA726", "#EF5350"]
bars3 = ax3.bar(categories, values, color=colors, edgecolor="black", width=0.5)
ax3.axhline(2.0, ls="--", color="navy", lw=2, label="Classical limit")
ax3.axhline(2 * np.sqrt(2), ls="--", color="red", lw=2, label="Quantum max $2\\sqrt{2}$")
ax3.set_ylabel("CHSH Correlation Value"); ax3.set_ylim(0, 3.2)
ax3.set_title("Bell Inequality Violation\nProves Non-Classical Correlations", fontsize=12, fontweight="bold")
ax3.legend(fontsize=9)

plt.suptitle("Quantum Entanglement: Correlations That Cannot Exist Classically",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("entanglement.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — State Normalization

For the state $|\psi\rangle = \frac{3}{5}|0\rangle + \frac{4}{5}|1\rangle$:
- What is $P(\text{measure } |0\rangle)$?
- What is $P(\text{measure } |1\rangle)$?
- Is this a valid quantum state?
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE
# Compute alpha, beta, and verify normalization

alpha = 3/5
beta  = 4/5

# YOUR CODE HERE: compute probabilities and check normalization
p0 = None  # replace with |alpha|^2
p1 = None  # replace with |beta|^2
norm = None  # replace with p0 + p1

print(f"P(|0⟩) = {p0}")
print(f"P(|1⟩) = {p1}")
print(f"Normalization: {norm} (should be 1.0)")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Bloch Sphere Coordinates

For the state $|\psi\rangle = \cos(30°)|0\rangle + \sin(30°)|1\rangle$ (real amplitudes, $\phi = 0$):
- Compute the Bloch vector $(x, y, z)$
- Where on the Bloch sphere does this state lie?
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE
theta = np.radians(60)  # note: Bloch theta = 2 * angle_in_state_formula
phi   = 0.0

# YOUR CODE HERE: compute Bloch vector components
bx = None  # sin(theta)*cos(phi)
by = None  # sin(theta)*sin(phi)
bz = None  # cos(theta)

print(f"Bloch vector: ({bx:.4f}, {by:.4f}, {bz:.4f})")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Design a thought experiment showing that **classical parallelism** (e.g., running 1000 computers simultaneously) is fundamentally different from **quantum superposition**.

Key question: If a classical ensemble of computers all start in state 0 and fan out, they are *independent* — their results cannot interfere. Why is this the crucial distinction from quantum amplitude interference?

Write your answer as a short markdown explanation, then implement a numerical demonstration of the difference between classical ensemble averaging and quantum amplitude interference.
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Classical ensemble vs quantum interference
n = 1000

# Classical: independent random walkers, result = average of outcomes
np.random.seed(0)
classical_outcomes = np.random.choice([-1, 1], size=n)
classical_result = np.abs(np.mean(classical_outcomes))  # goes to 0 by CLT

# Quantum: all paths contribute COHERENTLY — amplitudes add first, THEN square
phases = np.exp(1j * np.zeros(n))  # all in-phase = constructive interference
quantum_amplitude = np.sum(phases) / n   # normalized
quantum_result = np.abs(quantum_amplitude)**2

print(f"Classical ensemble avg probability: {classical_result:.4f}  (noise ~1/√N)")
print(f"Quantum coherent probability:        {quantum_result:.4f}  (= 1 when all in phase)")
print()
print("The classical ensemble CANNOT produce constructive interference.")
print("Quantum: change phases → destructive interference suppresses wrong answers.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Nielsen & Chuang** — *Quantum Computation and Quantum Information*, Chapter 1 (the canonical reference)
2. **Qiskit Textbook** — [https://learning.quantum.ibm.com](https://learning.quantum.ibm.com) — Chapter 1: Quantum States and Qubits
3. **Preskill's Lecture Notes** — [http://theory.caltech.edu/~preskill/ph229/](http://theory.caltech.edu/~preskill/ph229/) — Chapter 1
4. **Scott Aaronson** — *Quantum Computing Since Democritus* — Chapter 9 (accessible and rigorous)
5. **IBM Research Blog** — "What is Quantum Computing?" for application-grounded intuition
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "F1_what_is_quantum_computing.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
