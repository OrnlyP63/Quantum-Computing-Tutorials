#!/usr/bin/env python3
"""generate_nb.py — Module DS5: Quantum Kernels for Classification"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# DS5 — Quantum Kernels for Classification
**Track:** Data Scientist | **Difficulty:** ⭐⭐⭐⭐☆ | **Est. Time:** 35 min

| | |
|---|---|
| **Prerequisites** | F1–F4, DS1–DS3; kernel methods, SVM |
| **Qiskit Modules** | `qiskit`, `qiskit_machine_learning.kernels` |
| **Companion Video** | Data Scientist Module DS5 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Review the **kernel trick** and SVM theory to set up the quantum analogy
2. Define the **quantum kernel**: $K(\mathbf{x}, \mathbf{x}') = |\langle \phi(\mathbf{x})|\phi(\mathbf{x}')\rangle|^2$
3. Compute the quantum kernel matrix using `FidelityQuantumKernel`
4. Plug the quantum kernel into sklearn's `SVC` as a custom kernel
5. Compare quantum kernel SVM vs classical RBF, polynomial, and linear kernels
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Kernel Methods Refresher

### The Kernel Trick

A kernel $K(\mathbf{x}, \mathbf{x}')$ implicitly computes the inner product in a (possibly infinite-dimensional) feature space $\mathcal{F}$:

$$K(\mathbf{x}, \mathbf{x}') = \langle \phi(\mathbf{x}), \phi(\mathbf{x}')\rangle_{\mathcal{F}}$$

The SVM finds a decision boundary in $\mathcal{F}$ without explicitly computing $\phi(\mathbf{x})$. This is powerful when $\mathcal{F}$ is very high (or infinite) dimensional.

### Classical Kernels

| Kernel | Formula | Feature Space Dimension |
|---|---|---|
| Linear | $\mathbf{x}^\top \mathbf{x}'$ | $n$ (input dim) |
| Polynomial | $(\mathbf{x}^\top \mathbf{x}' + c)^d$ | $O(n^d)$ |
| RBF (Gaussian) | $e^{-\|\mathbf{x}-\mathbf{x}'\|^2/(2\sigma^2)}$ | Infinite |

### Quantum Kernel

When the feature map $\phi(\mathbf{x}) = U(\mathbf{x})|0\rangle$ is a quantum circuit, the kernel becomes:

$$K(\mathbf{x}, \mathbf{x}') = |\langle 0|U^\dagger(\mathbf{x}) U(\mathbf{x}')|0\rangle|^2$$

This is the **overlap (fidelity)** between two quantum states — efficiently computable on a quantum computer via the **swap test** or **Hadamard test**.

The quantum feature space has dimension $2^n$ — exponentially large in the number of qubits $n$.

> **DS Bridge:** Quantum kernel = drop-in replacement for RBF kernel in sklearn's SVM pipeline. The quantum computer computes the inner product in a space classical computers can't efficiently access.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Classical Kernel Baseline"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import warnings; warnings.filterwarnings("ignore")

np.random.seed(42)

# Dataset (same as DS1-DS3)
X, y = make_moons(n_samples=150, noise=0.1, random_state=42)
X = MinMaxScaler(feature_range=(0, np.pi)).fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Classical kernel comparison
classical_kernels = {
    "Linear": SVC(kernel="linear", C=1.0),
    "Polynomial (d=2)": SVC(kernel="poly", degree=2, C=1.0),
    "Polynomial (d=3)": SVC(kernel="poly", degree=3, C=1.0),
    "RBF (σ=0.5)": SVC(kernel="rbf", gamma=2.0, C=1.0),
    "RBF (σ=1.0)": SVC(kernel="rbf", gamma=0.5, C=1.0),
}

classical_results = {}
print(f"{'Kernel':25s} {'Train Acc':>12s} {'Test Acc':>12s}")
print("-" * 52)
for name, clf in classical_kernels.items():
    clf.fit(X_train, y_train)
    tr_acc = accuracy_score(y_train, clf.predict(X_train))
    te_acc = accuracy_score(y_test,  clf.predict(X_test))
    classical_results[name] = te_acc
    print(f"{name:25s} {tr_acc:>12.4f} {te_acc:>12.4f}")

BEST_CLASSICAL = max(classical_results.values())
print(f"\nBest classical test accuracy: {BEST_CLASSICAL:.4f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Quantum Kernel via Statevector Fidelity"""))

cells.append(nbf.v4.new_code_cell(r"""from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector

# Feature map circuit (same as DS2 ZZFeatureMap)
def build_feature_map(x: np.ndarray, reps: int = 2) -> QuantumCircuit:
    '''Build a parameterized feature map circuit for data point x.'''
    n = len(x)
    qc = QuantumCircuit(n, name="FeatureMap")
    for _ in range(reps):
        qc.h(range(n))
        for i in range(n):
            qc.rz(2 * x[i], i)
        if n > 1:
            for i in range(n - 1):
                phi_ij = 2 * (np.pi - x[i]) * (np.pi - x[i+1])
                qc.cx(i, i+1)
                qc.rz(phi_ij, i+1)
                qc.cx(i, i+1)
    return qc

def quantum_kernel_entry(x1: np.ndarray, x2: np.ndarray, reps: int = 2) -> float:
    '''
    Compute K(x1, x2) = |⟨φ(x1)|φ(x2)⟩|²
    = |⟨0|U†(x1) U(x2)|0⟩|²
    '''
    qc1 = build_feature_map(x1, reps)
    qc2 = build_feature_map(x2, reps)

    sv1 = Statevector(qc1)
    sv2 = Statevector(qc2)

    # Fidelity = |⟨ψ₁|ψ₂⟩|²
    overlap = np.abs(sv1.data.conj() @ sv2.data)**2
    return overlap

def compute_kernel_matrix(X1: np.ndarray, X2: np.ndarray, reps: int = 2) -> np.ndarray:
    '''Compute the full kernel matrix K[i,j] = K(X1[i], X2[j]).'''
    n1, n2 = len(X1), len(X2)
    K = np.zeros((n1, n2))
    for i in range(n1):
        for j in range(n2):
            K[i, j] = quantum_kernel_entry(X1[i], X2[j], reps)
    return K

# Test on small subset first
print("Computing quantum kernel matrix (small subset)...")
n_small = 20  # Keep small to be fast
X_train_s = X_train[:n_small]
y_train_s = y_train[:n_small]
X_test_s  = X_test[:10]
y_test_s  = y_test[:10]

K_train = compute_kernel_matrix(X_train_s, X_train_s)
K_test  = compute_kernel_matrix(X_test_s, X_train_s)

print(f"Kernel matrix shape: {K_train.shape}")
print(f"K[0,0] = {K_train[0,0]:.4f} (should be 1.0 — self-fidelity)")
print(f"K range: [{K_train.min():.4f}, {K_train.max():.4f}]")
print(f"Kernel matrix is positive semi-definite: {np.all(np.linalg.eigvalsh(K_train) >= -1e-10)}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Quantum SVM with Custom Kernel"""))

cells.append(nbf.v4.new_code_cell(r"""# Plug quantum kernel into sklearn SVM

clf_qsvm = SVC(kernel="precomputed", C=1.0)
clf_qsvm.fit(K_train, y_train_s)

qsvm_train_acc = accuracy_score(y_train_s, clf_qsvm.predict(K_train))
qsvm_test_acc  = accuracy_score(y_test_s,  clf_qsvm.predict(K_test))

print("Quantum SVM Results (small subset):")
print(f"  Train accuracy: {qsvm_train_acc:.4f}")
print(f"  Test accuracy:  {qsvm_test_acc:.4f}")

# Visualize kernel matrix
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Quantum kernel matrix
im = axes[0].imshow(K_train, cmap="Blues", vmin=0, vmax=1)
plt.colorbar(im, ax=axes[0], fraction=0.046)
axes[0].set_title(f"Quantum Kernel Matrix\n({n_small}×{n_small} training samples)",
                  fontsize=11, fontweight="bold")
axes[0].set_xlabel("Sample j"); axes[0].set_ylabel("Sample i")

# Sort by class label to show block structure
sorted_idx = np.argsort(y_train_s)
K_sorted = K_train[np.ix_(sorted_idx, sorted_idx)]
im2 = axes[1].imshow(K_sorted, cmap="Blues", vmin=0, vmax=1)
plt.colorbar(im2, ax=axes[1], fraction=0.046)
axes[1].set_title("Quantum Kernel (sorted by class)\nBlock structure = class separation",
                  fontsize=11, fontweight="bold")

# Compute RBF kernel for comparison
from sklearn.metrics.pairwise import rbf_kernel
K_rbf = rbf_kernel(X_train_s, X_train_s, gamma=2.0)
K_rbf_sorted = K_rbf[np.ix_(sorted_idx, sorted_idx)]
im3 = axes[2].imshow(K_rbf_sorted, cmap="Reds", vmin=0, vmax=1)
plt.colorbar(im3, ax=axes[2], fraction=0.046)
axes[2].set_title("Classical RBF Kernel (sorted)\nFor comparison", fontsize=11, fontweight="bold")

plt.suptitle("Kernel Matrices: Quantum vs Classical RBF (sorted by class label)",
             fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("kernel_matrices.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Qiskit FidelityQuantumKernel"""))

cells.append(nbf.v4.new_code_cell(r"""try:
    from qiskit_machine_learning.kernels import FidelityQuantumKernel
    from qiskit.circuit.library import ZZFeatureMap
    HAS_QKERNEL = True
except ImportError:
    HAS_QKERNEL = False

if HAS_QKERNEL:
    # Use Qiskit's built-in quantum kernel implementation
    feature_map = ZZFeatureMap(feature_dimension=2, reps=2)

    qkernel = FidelityQuantumKernel(feature_map=feature_map)

    # Compute kernel matrices
    K_train_qk = qkernel.evaluate(X_train_s, X_train_s)
    K_test_qk  = qkernel.evaluate(X_test_s, X_train_s)

    clf_qk = SVC(kernel="precomputed", C=1.0)
    clf_qk.fit(K_train_qk, y_train_s)

    qk_train_acc = accuracy_score(y_train_s, clf_qk.predict(K_train_qk))
    qk_test_acc  = accuracy_score(y_test_s,  clf_qk.predict(K_test_qk))
    print(f"FidelityQuantumKernel (ZZFeatureMap) — Train: {qk_train_acc:.4f}, Test: {qk_test_acc:.4f}")

else:
    print("Using manual quantum kernel (FidelityQuantumKernel not available)")
    qk_test_acc = qsvm_test_acc
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Comprehensive Comparison"""))

cells.append(nbf.v4.new_code_cell(r"""# Compare all kernels on same dataset

# Classical SVM on full test set
classical_full = {
    name: accuracy_score(y_test, clf.predict(X_test))
    for name, clf in classical_kernels.items()
}

# Quantum kernel (on small subset — note this is not a fair comparison at small N)
quantum_result = {"Quantum Kernel (ZZFeatureMap)": qk_test_acc if HAS_QKERNEL else qsvm_test_acc}

all_results = {**classical_full, **quantum_result}

fig, ax = plt.subplots(figsize=(12, 5))
names  = list(all_results.keys())
values = list(all_results.values())
colors = ["#2196F3"] * len(classical_full) + ["#9C27B0"]

bars = ax.bar(names, values, color=colors, edgecolor="black", width=0.6)
ax.axhline(BEST_CLASSICAL, ls="--", color="navy", lw=2, label=f"Best classical: {BEST_CLASSICAL:.3f}")

for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
            f"{bar.get_height():.3f}", ha="center", fontsize=10)

ax.set_xlabel("Kernel Type"); ax.set_ylabel("Test Accuracy")
ax.set_title("Quantum Kernel SVM vs Classical Kernels\n"
             "Note: quantum result on small subset — needs full dataset for fair comparison",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=10); ax.set_ylim(0, 1.15)
ax.tick_params(axis="x", rotation=25)

# Color legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor="#2196F3", label="Classical"),
                   Patch(facecolor="#9C27B0", label="Quantum")]
ax.legend(handles=legend_elements, fontsize=10)

plt.tight_layout()
plt.savefig("kernel_comparison.png", dpi=120, bbox_inches="tight")
plt.show()

print("\nKey insight: Quantum kernels can express feature spaces of exponential dimension,")
print("but this does NOT guarantee better accuracy — the data must have quantum-compatible structure.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Kernel Matrix Analysis

For the quantum kernel matrix, compute:
1. Gram matrix rank (how many linearly independent dimensions does it span?)
2. Kernel alignment with the ideal kernel $K_{ideal}(i,j) = 1 \text{ if } y_i = y_j, \text{ else } 0$
3. Plot the eigenvalue spectrum — compare to RBF kernel
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — kernel analysis

K = K_train.copy()
y_labels = y_train_s.copy()

# 1. Rank
rank = np.linalg.matrix_rank(K, tol=1e-8)
print(f"Kernel matrix rank: {rank}/{n_small}")

# 2. Kernel alignment (how well-aligned is K with the ideal label kernel?)
K_ideal = (y_labels[:, None] == y_labels[None, :]).astype(float)
K_ideal = K_ideal / np.linalg.norm(K_ideal)
K_norm  = K / np.linalg.norm(K)
alignment = np.trace(K_norm @ K_ideal)
print(f"Kernel alignment with ideal: {alignment:.4f}  (1.0 = perfect)")

# 3. Eigenvalue spectrum
eigenvalues = sorted(np.linalg.eigvalsh(K), reverse=True)
print(f"\nTop 5 eigenvalues: {[f'{e:.4f}' for e in eigenvalues[:5]]}")

# YOUR CODE HERE: plot eigenvalue spectrum
plt.figure(figsize=(8, 4))
plt.semilogy(range(1, len(eigenvalues)+1), eigenvalues, "o-", lw=2, ms=6,
             color="#9C27B0", label="Quantum kernel")
# YOUR CODE HERE: overlay RBF eigenvalues
plt.xlabel("Index"); plt.ylabel("Eigenvalue (log scale)")
plt.title("Eigenvalue Spectrum of Quantum vs Classical Kernels")
plt.legend(); plt.grid(True, which="both", alpha=0.3)
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Feature Map Comparison

Compare 3 different feature maps as quantum kernels:
1. Angle encoding: $R_y(x_i)$ only
2. ZZ feature map (reps=1)
3. ZZ feature map (reps=2)

Hypothesis: more repetitions → more expressive kernel → better separation?
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — feature map comparison

feature_maps_to_compare = {
    "Angle encoding": 0,    # reps=0 means just Ry
    "ZZFeatureMap (reps=1)": 1,
    "ZZFeatureMap (reps=2)": 2,
}

print(f"{'Feature Map':30s} {'Train Acc':>12s} {'Test Acc':>12s} {'Alignment':>12s}")
print("-" * 70)

for fm_name, reps in feature_maps_to_compare.items():
    # YOUR CODE HERE: compute kernel matrices and run SVM
    # Use the compute_kernel_matrix function from earlier
    if reps == 0:
        def angle_only_kernel(x1, x2):
            '''Simple angle encoding kernel: product of cos((x1-x2)/2) terms.'''
            return np.prod(np.cos((x1 - x2) / 2)**2)
        K_fm = np.array([[angle_only_kernel(X_train_s[i], X_train_s[j])
                         for j in range(n_small)] for i in range(n_small)])
    else:
        K_fm = compute_kernel_matrix(X_train_s, X_train_s, reps=reps)

    K_fm_test = np.array([[quantum_kernel_entry(X_test_s[i], X_train_s[j], reps=max(reps,1))
                           for j in range(n_small)] for i in range(len(X_test_s))])

    clf_fm = SVC(kernel="precomputed", C=1.0)
    clf_fm.fit(K_fm, y_train_s)
    tr_a = accuracy_score(y_train_s, clf_fm.predict(K_fm))
    te_a = accuracy_score(y_test_s,  clf_fm.predict(K_fm_test))

    # Kernel alignment
    K_id = (y_train_s[:,None] == y_train_s[None,:]).astype(float)
    aln  = np.trace(K_fm/np.linalg.norm(K_fm) @ K_id/np.linalg.norm(K_id))
    print(f"{fm_name:30s} {tr_a:>12.4f} {te_a:>12.4f} {aln:>12.4f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Implement the **quantum kernel training (QKT)** algorithm — optimize the feature map parameters to maximize kernel-target alignment:

$$\mathcal{A}(K_\lambda, K_y) = \frac{\langle K_\lambda, K_y \rangle_F}{\|K_\lambda\|_F \cdot \|K_y\|_F}$$

1. Parameterize the feature map with trainable angle parameters $\lambda$
2. Use the alignment as the objective (maximize)
3. Optimize $\lambda$ using `scipy.optimize.minimize`
4. Show that the optimized kernel has higher alignment and better classification accuracy
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Quantum Kernel Training (QKT)
from scipy.optimize import minimize

# Parameterized feature map: add trainable scale parameters
def parameterized_feature_map(x: np.ndarray, lam: np.ndarray) -> QuantumCircuit:
    '''Feature map with trainable scale parameters λ.'''
    n = len(x)
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for i in range(n):
        qc.rz(lam[i] * x[i], i)   # scaled angle encoding
    for i in range(n - 1):
        qc.cx(i, i+1)
        qc.rz(lam[n + i] * (np.pi - x[i]) * (np.pi - x[i+1]), i+1)
        qc.cx(i, i+1)
    return qc

def compute_param_kernel(X1, X2, lam):
    n1, n2 = len(X1), len(X2)
    K = np.zeros((n1, n2))
    for i in range(n1):
        for j in range(n2):
            sv1 = Statevector(parameterized_feature_map(X1[i], lam))
            sv2 = Statevector(parameterized_feature_map(X2[j], lam))
            K[i,j] = abs(sv1.data.conj() @ sv2.data)**2
    return K

def kernel_alignment(lam, X, y):
    K = compute_param_kernel(X, X, lam)
    K_y = (y[:,None] == y[None,:]).astype(float)
    return -np.trace(K / np.linalg.norm(K) @ K_y / np.linalg.norm(K_y))

# YOUR CODE HERE: optimize lambda and show improvement
n_feat = 2
lam_init = np.ones(n_feat * 2)  # initial scale=1 for all terms

print("Challenge: Optimize lambda to maximize kernel-target alignment.")
print(f"Initial alignment: {-kernel_alignment(lam_init, X_train_s, y_train_s):.4f}")
print("Run: result = minimize(kernel_alignment, lam_init, args=(X_train_s, y_train_s), method='Nelder-Mead')")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Havlíček et al. (2019)** — "Supervised learning with quantum-enhanced feature spaces" — Nature 567
2. **Schuld & Killoran (2019)** — "Quantum machine learning in feature Hilbert spaces" — PRL 122
3. **Glick et al. (2022)** — "Covariant quantum kernels for data with group structure" — arXiv:2105.03406
4. **FidelityQuantumKernel** — Qiskit Machine Learning API reference
5. **Kernel methods in ML** — Schölkopf & Smola "Learning with Kernels" — the classical reference
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DS5_quantum_kernels.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
