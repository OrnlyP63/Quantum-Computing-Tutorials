#!/usr/bin/env python3
"""generate_nb.py — Module DS1: Quantum vs Classical ML — The Big Picture"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# DS1 — Quantum vs Classical ML: The Big Picture
**Track:** Data Scientist | **Difficulty:** ⭐⭐☆☆☆ | **Est. Time:** 20 min

| | |
|---|---|
| **Prerequisites** | F1–F4; sklearn, numpy, basic ML experience |
| **Qiskit Modules** | `qiskit`, `qiskit_aer` |
| **Companion Video** | Data Scientist Module DS1 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Map the components of a **classical neural network** to a **variational quantum circuit (VQC)**
2. Establish a **classical sklearn baseline** on the dataset used throughout this track
3. Understand the concept of **quantum feature maps** as data embedding layers
4. Identify where quantum ML may provide advantage (and where it cannot)
5. Describe **barren plateaus** — the core training challenge in quantum ML
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Concept Summary

### The Quantum ML Hypothesis

A VQC computes:

$$f(\mathbf{x}; \boldsymbol{\theta}) = \langle 0 | U^\dagger(\mathbf{x}) V^\dagger(\boldsymbol{\theta}) \hat{O} V(\boldsymbol{\theta}) U(\mathbf{x}) | 0 \rangle$$

Where:
- $U(\mathbf{x})$ = **feature map** — encodes classical data $\mathbf{x}$ into a quantum state
- $V(\boldsymbol{\theta})$ = **ansatz** — parameterized circuit (trainable "weights" $\boldsymbol{\theta}$)
- $\hat{O}$ = **observable** — measurement operator (analogous to output layer)

### Analogy Table

| Classical Neural Net | Variational Quantum Circuit |
|---|---|
| Input layer (normalization) | Feature map $U(\mathbf{x})$ |
| Hidden layers | Ansatz $V(\boldsymbol{\theta})$ |
| Weight matrix $W$ | Rotation angle $\theta_i$ |
| Activation function | Measurement + Born rule |
| Backpropagation | Parameter shift rule |
| Loss function | $\langle\hat{O}\rangle$ expectation value |

### Honest Assessment

- **Potential advantage:** Quantum feature spaces are exponentially large — could represent kernel functions classical computers can't tractably evaluate
- **Current reality:** NISQ devices have too much noise for large-scale QML
- **Best use case:** Quantum-enhanced kernel methods (DS5) on structured data where the quantum kernel has a provably non-classical structure
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Dataset and Classical Baseline"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
import warnings; warnings.filterwarnings("ignore")

np.random.seed(42)

# We'll use this dataset for ALL DS modules — establish the baseline here
# The "moons" dataset: non-linearly separable, good for demonstrating kernels

N_SAMPLES = 200
DATASET_NAME = "Two Moons"

X, y = make_moons(n_samples=N_SAMPLES, noise=0.1, random_state=42)

# Scale to [0, 2π] — needed for angle encoding in quantum circuits
scaler = MinMaxScaler(feature_range=(0, 2 * np.pi))
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

print(f"Dataset: {DATASET_NAME}")
print(f"Total samples: {N_SAMPLES}")
print(f"Training: {len(X_train)}, Test: {len(X_test)}")
print(f"Features: {X.shape[1]}, Classes: {len(np.unique(y))}")
print(f"Feature range after scaling: [{X_scaled.min():.3f}, {X_scaled.max():.3f}]")
"""))

cells.append(nbf.v4.new_code_cell(r"""# Visualize the dataset
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
for label, color, name in [(0, "#2196F3", "Class 0"), (1, "#FF5722", "Class 1")]:
    mask = y == label
    ax.scatter(X[mask, 0], X[mask, 1], c=color, s=40, label=name, alpha=0.8, edgecolor="black", lw=0.5)
ax.set_xlabel("Feature 1"); ax.set_ylabel("Feature 2")
ax.set_title(f"{DATASET_NAME} Dataset (raw)", fontsize=12, fontweight="bold")
ax.legend()

ax2 = axes[1]
for label, color, name in [(0, "#2196F3", "Class 0"), (1, "#FF5722", "Class 1")]:
    mask = y == label
    ax2.scatter(X_scaled[mask, 0], X_scaled[mask, 1], c=color, s=40, label=name, alpha=0.8,
                edgecolor="black", lw=0.5)
ax2.set_xlabel("x₁ (angle, radians)"); ax2.set_ylabel("x₂ (angle, radians)")
ax2.set_title(f"{DATASET_NAME} Dataset (scaled to [0, 2π])\nReady for angle encoding",
              fontsize=12, fontweight="bold")
ax2.legend()

plt.suptitle("Two Moons: A Non-Linearly Separable Binary Classification Task",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("dataset_moons.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Classical Baselines"""))

cells.append(nbf.v4.new_code_cell(r"""# Establish multiple classical baselines that QML results will be compared against

classifiers = {
    "SVM (RBF kernel)":       SVC(kernel="rbf", C=1.0, gamma="scale"),
    "SVM (Linear)":           SVC(kernel="linear", C=1.0),
    "MLP (2 layers, 16 u)":   MLPClassifier(hidden_layer_sizes=(16, 16), max_iter=500),
    "MLP (shallow, 4 units)": MLPClassifier(hidden_layer_sizes=(4,), max_iter=500),
}

results = {}
for name, clf in classifiers.items():
    clf.fit(X_train, y_train)
    train_acc = accuracy_score(y_train, clf.predict(X_train))
    test_acc  = accuracy_score(y_test,  clf.predict(X_test))
    results[name] = {"train": train_acc, "test": test_acc}
    print(f"{name:35s}  Train: {train_acc:.4f}  Test: {test_acc:.4f}")

# Save baseline for future reference
BASELINE_CLASSICAL = max(v["test"] for v in results.values())
print(f"\nBest classical test accuracy: {BASELINE_CLASSICAL:.4f}")
print("QML modules will compare against this baseline.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Decision Boundary Visualization"""))

cells.append(nbf.v4.new_code_cell(r"""fig, axes = plt.subplots(1, len(classifiers), figsize=(18, 4))

xx, yy = np.meshgrid(np.linspace(0, 2*np.pi, 80), np.linspace(0, 2*np.pi, 80))
grid = np.c_[xx.ravel(), yy.ravel()]

for ax, (name, clf) in zip(axes, classifiers.items()):
    Z = clf.predict(grid).reshape(xx.shape)
    ax.contourf(xx, yy, Z, alpha=0.3, cmap="RdBu_r")
    ax.contour(xx, yy, Z, colors="black", linewidths=0.5)
    for label, color in [(0, "#2196F3"), (1, "#FF5722")]:
        mask = y_test == label
        ax.scatter(X_test[mask, 0], X_test[mask, 1], c=color, s=30, alpha=0.8,
                   edgecolor="black", lw=0.5)
    acc = results[name]["test"]
    ax.set_title(f"{name}\nTest acc: {acc:.3f}", fontsize=9, fontweight="bold")
    ax.set_xlabel("x₁"); ax.set_ylabel("x₂")

plt.suptitle("Classical Decision Boundaries — Our Quantum Baselines to Beat",
             fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("classical_boundaries.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 VQC Architecture Preview"""))

cells.append(nbf.v4.new_code_cell(r"""from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector

# Show what a VQC looks like — we'll implement it fully in DS3
n_qubits = 2
n_layers = 2

# Feature map: encode data into the circuit
x_params = ParameterVector("x", n_qubits)    # data parameters
theta_params = ParameterVector("θ", n_qubits * n_layers)  # trainable parameters

qc_vqc = QuantumCircuit(n_qubits, name="VQC Preview")

# Feature map layer
for i in range(n_qubits):
    qc_vqc.ry(x_params[i], i)   # encode x[i] as angle
qc_vqc.cx(0, 1)
qc_vqc.barrier(label="Feature Map U(x)")

# Ansatz layers
idx = 0
for layer in range(n_layers):
    for i in range(n_qubits):
        qc_vqc.ry(theta_params[idx], i)
        idx += 1
    qc_vqc.cx(0, 1)
    if layer < n_layers - 1:
        qc_vqc.barrier()
qc_vqc.barrier(label="Ansatz V(θ)")

print("VQC Architecture (will be trained in DS3):")
print(qc_vqc.draw(output="text"))
print(f"\nData parameters (fixed at inference): {list(x_params)}")
print(f"Trainable parameters (optimized): {list(theta_params)}")
print(f"\nTotal trainable parameters: {len(theta_params)}")
print(f"Analogous to: {n_qubits * n_layers}-parameter neural network")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 The Barren Plateau Problem"""))

cells.append(nbf.v4.new_code_cell(r"""# Visualize barren plateaus — gradients vanish exponentially as circuit depth grows
# This is the core training challenge in quantum ML

from qiskit import transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

sim = AerSimulator()

def estimate_gradient_variance(n: int, depth: int, n_samples: int = 100) -> float:
    '''Estimate variance of parameter gradient for an n-qubit, depth-d random circuit.'''
    gradients = []
    for _ in range(n_samples):
        # Random parameterization
        thetas = np.random.uniform(0, 2*np.pi, n * depth)
        delta  = np.pi / 2  # parameter shift delta

        # Build random circuit
        def build_circuit(params):
            qc = QuantumCircuit(n)
            idx = 0
            for d in range(depth):
                for q in range(n):
                    qc.ry(params[idx], q); idx += 1
                for q in range(n - 1):
                    qc.cx(q, q + 1)
            return qc

        # Parameter shift rule: gradient = (E[+] - E[-]) / 2
        # Approximate with Statevector
        def expectation(params):
            qc = build_circuit(params)
            sv = Statevector(qc)
            # Observable: Z on qubit 0
            dm = np.array([[1,0],[0,-1]])
            # Partial expectation
            return sv.expectation_value(dm, qargs=[0]).real

        # Gradient w.r.t. first parameter
        thetas_plus  = thetas.copy(); thetas_plus[0]  += delta
        thetas_minus = thetas.copy(); thetas_minus[0] -= delta
        grad = (expectation(thetas_plus) - expectation(thetas_minus)) / 2
        gradients.append(grad)

    return np.var(gradients)

print("Estimating gradient variance (barren plateau analysis)...")
print("This demonstrates WHY training deep quantum circuits is hard.\n")

qubit_counts_bp = [2, 3, 4]
depth_bp        = 3
variance_by_n   = []

for n in qubit_counts_bp:
    var = estimate_gradient_variance(n, depth_bp, n_samples=50)
    variance_by_n.append(var)
    print(f"  n={n} qubits, depth={depth_bp}: Gradient variance = {var:.6f}")

print(f"\nObserve: variance decreases exponentially with n → gradients vanish for large n")

fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogy(qubit_counts_bp, variance_by_n, "r-o", lw=2.5, ms=10)
ax.set_xlabel("Number of Qubits n"); ax.set_ylabel("Gradient Variance (log scale)")
ax.set_title("Barren Plateau: Gradient Variance Vanishes with Circuit Size\n"
             "This is why quantum ML is hard to train at scale", fontsize=11, fontweight="bold")
ax.grid(True, which="both", alpha=0.3)
ax.text(0.6, 0.8, "Exponential decay\n~ exp(-n)", transform=ax.transAxes,
        fontsize=11, color="darkred",
        bbox=dict(boxstyle="round", facecolor="#FFCDD2", alpha=0.8))
plt.tight_layout()
plt.savefig("barren_plateau.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — VQC Parameter Count

For a VQC with $n$ qubits, $L$ layers, and $k$ rotations per qubit per layer:

1. Write a formula for the total number of trainable parameters
2. Compare to a classical MLP with the same parameter count
3. What circuit size would match a classical MLP with 100 parameters?
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE
def vqc_param_count(n_qubits: int, n_layers: int, rotations_per_qubit: int = 1) -> int:
    return None  # YOUR CODE HERE

def mlp_param_count(layers: list) -> int:
    '''Count parameters in a fully-connected MLP.'''
    total = 0
    for i in range(1, len(layers)):
        total += layers[i-1] * layers[i] + layers[i]  # weights + biases
    return total

# Compare
target_params = 100
print("VQC vs MLP parameter comparison:")
print(f"{'Config':40s} {'Params':>8s}")
print("-" * 50)

for n, L in [(2,5),(3,5),(4,5),(5,5),(2,10),(3,8)]:
    p = vqc_param_count(n, L)
    if p:
        print(f"VQC({n} qubits, {L} layers):              {p:>8d}")

print()
for hidden in [(8,), (16,), (32,), (8,8), (16,16)]:
    arch = [2] + list(hidden) + [1]  # input=2, output=1
    p = mlp_param_count(arch)
    print(f"MLP {arch}:                    {p:>8d}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Data Preparation

Prepare the Two Moons dataset for quantum ML:
1. Normalize features to $[-\pi, \pi]$ using a StandardScaler + clip
2. Sample 50 training and 20 test points (small batch — quantum circuits are slow)
3. Visualize both train and test splits
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — data preparation pipeline
from sklearn.preprocessing import StandardScaler

# Small batch for QML
N_SMALL = 70  # 50 train + 20 test

X_small, y_small = make_moons(n_samples=N_SMALL, noise=0.1, random_state=42)

# YOUR CODE HERE: scale to [-π, π]
scaler_q = StandardScaler()
X_q = scaler_q.fit_transform(X_small)
X_q = np.clip(X_q, -np.pi, np.pi)

X_train_q, X_test_q, y_train_q, y_test_q = train_test_split(
    X_q, y_small, test_size=20, random_state=42
)

print(f"Training samples: {len(X_train_q)}")
print(f"Test samples:     {len(X_test_q)}")
print(f"Feature range: [{X_q.min():.3f}, {X_q.max():.3f}]")

# YOUR CODE HERE: visualize train/test split
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Compare **two different feature scaling strategies** for quantum ML:
1. MinMaxScaler to $[0, 2\pi]$ (angle encoding range)
2. StandardScaler + clip to $[-\pi, \pi]$

For each scaling:
1. Train a classical SVM on the scaled data
2. Plot the decision boundary
3. Compute accuracy

Which scaling is better for **classical** ML? Which do you predict will be better for quantum? Why?
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Scaling strategy comparison
# YOUR CODE HERE

scaling_methods = {
    "MinMaxScaler [0, 2π]": MinMaxScaler(feature_range=(0, 2*np.pi)),
    "StandardScaler [-π, π]": None,  # YOUR CODE HERE
}

for name, scaler_method in scaling_methods.items():
    if scaler_method is None: continue
    X_s = scaler_method.fit_transform(X)
    X_tr_s, X_te_s, y_tr_s, y_te_s = train_test_split(X_s, y, test_size=0.2, random_state=42)
    clf = SVC(kernel="rbf"); clf.fit(X_tr_s, y_tr_s)
    acc = accuracy_score(y_te_s, clf.predict(X_te_s))
    print(f"{name}: SVM-RBF test accuracy = {acc:.4f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Schuld & Killoran (2022)** — "Quantum machine learning models" — arXiv:2202.01607
2. **Biamonte et al. (2017)** — "Quantum machine learning" — Nature 549 (seminal survey)
3. **McClean et al. (2018)** — "Barren plateaus in quantum neural network training landscapes"
4. **Qiskit Machine Learning Docs** — [https://qiskit-community.github.io/qiskit-machine-learning/](https://qiskit-community.github.io/qiskit-machine-learning/)
5. **Cerezo et al. (2021)** — "Variational quantum algorithms" — Nature Reviews Physics
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DS1_qml_big_picture.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
