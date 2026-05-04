#!/usr/bin/env python3
"""generate_nb.py — Module DS3: Variational Quantum Circuits (VQC)"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# DS3 — Variational Quantum Circuits (VQC)
**Track:** Data Scientist | **Difficulty:** ⭐⭐⭐⭐☆ | **Est. Time:** 40 min

| | |
|---|---|
| **Prerequisites** | F1–F4, DS1, DS2; scipy.optimize, numpy |
| **Qiskit Modules** | `qiskit`, `qiskit_aer`, `qiskit.circuit.library` |
| **Companion Video** | Data Scientist Module DS3 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Build a VQC for binary classification using `RealAmplitudes` ansatz
2. Define a **cost function** based on expectation values of Pauli observables
3. Train the VQC using **COBYLA** and **gradient-free** optimization
4. Implement the **parameter shift rule** for gradient computation
5. Plot the **loss curve** and evaluate test accuracy
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Concept Summary

### VQC Training Loop

The VQC training loop mirrors classical ML:

```
1. Initialize θ randomly
2. For each epoch:
   a. Encode batch: x → U(x)|0⟩
   b. Apply ansatz: V(θ)U(x)|0⟩
   c. Measure: ⟨O⟩ = ⟨0|U†(x)V†(θ) O V(θ)U(x)|0⟩
   d. Compute loss: L(θ) = f(⟨O⟩, y_true)
   e. Update θ: θ ← θ - η ∇L(θ)   [or gradient-free step]
```

### Parameter Shift Rule (Quantum Gradient)

For a parameterized gate $G(\theta) = e^{-i\theta P/2}$ (where $P$ is a Pauli):

$$\frac{\partial\langle\hat{O}\rangle}{\partial\theta} = \frac{\langle\hat{O}\rangle|_{\theta+\pi/2} - \langle\hat{O}\rangle|_{\theta-\pi/2}}{2}$$

This is exact (not an approximation like finite differences) and computable on quantum hardware. It requires 2 additional circuit evaluations per parameter — analogous to backpropagation but fundamentally different in mechanism.

### Cost Function

For binary classification ($y \in \{0, 1\}$), measure $\langle Z_0 \rangle$:

$$L(\boldsymbol{\theta}) = \frac{1}{N}\sum_{i=1}^N \ell\big(y_i, \tfrac{1}{2}(1 - \langle Z_0\rangle_i)\big)$$

where $\langle Z_0\rangle_i \in [-1, 1]$ maps to probability via $(1 - \langle Z_0\rangle)/2 \in [0,1]$.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 VQC Architecture"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector, SparsePauliOp
from qiskit_aer import AerSimulator
from sklearn.datasets import make_moons
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

np.random.seed(42)
sim = AerSimulator()

# ---- Dataset ----
X, y = make_moons(n_samples=120, noise=0.1, random_state=42)
X = MinMaxScaler(feature_range=(0, np.pi)).fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

print(f"Training: {len(X_train)}, Test: {len(X_test)}")
print(f"Class balance (train): {np.mean(y_train==0):.2f}/{np.mean(y_train==1):.2f}")

# ---- VQC Architecture ----
N_QUBITS = 2
N_LAYERS = 3

x_params   = ParameterVector("x", N_QUBITS)       # data
theta_params = ParameterVector("θ", N_QUBITS * N_LAYERS)  # trainable

def build_vqc(x_data: np.ndarray = None) -> QuantumCircuit:
    '''Build VQC with angle encoding + RealAmplitudes-style ansatz.'''
    qc = QuantumCircuit(N_QUBITS, name="VQC")

    # Feature map: angle encoding
    for i in range(N_QUBITS):
        qc.ry(x_params[i], i)
    qc.cx(0, 1)
    qc.barrier()

    # Ansatz layers
    idx = 0
    for layer in range(N_LAYERS):
        for q in range(N_QUBITS):
            qc.ry(theta_params[idx], q)
            idx += 1
        if layer < N_LAYERS - 1:
            qc.cx(0, 1)

    return qc

vqc = build_vqc()
print("\nVQC Circuit:")
print(vqc.draw(output="text"))
print(f"\nTotal parameters: {len(theta_params)} (trainable)")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Expectation Value Computation"""))

cells.append(nbf.v4.new_code_cell(r"""def expectation_Z0(theta: np.ndarray, x: np.ndarray) -> float:
    '''Compute ⟨Z₀⟩ for a single data point x with parameters theta.'''
    # Bind both data and trainable parameters
    param_dict = {xp: xi for xp, xi in zip(x_params, x)}
    param_dict.update({tp: ti for tp, ti in zip(theta_params, theta)})

    bound_qc = build_vqc().assign_parameters(param_dict)
    sv = Statevector(bound_qc)

    # ⟨Z₀⟩ = P(measure 0 on qubit 0) - P(measure 1 on qubit 0)
    probs = sv.probabilities([0])   # marginal probability of qubit 0
    return probs[0] - probs[1]      # E[Z₀] = P(0) - P(1)

def predict_proba(theta: np.ndarray, X_data: np.ndarray) -> np.ndarray:
    '''Convert ⟨Z₀⟩ expectation to class probability.'''
    exp_vals = np.array([expectation_Z0(theta, x) for x in X_data])
    return (1 - exp_vals) / 2   # Map [-1,1] → [0,1]

def predict(theta: np.ndarray, X_data: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    return (predict_proba(theta, X_data) > threshold).astype(int)

def cross_entropy_loss(theta: np.ndarray, X_data: np.ndarray, y_data: np.ndarray) -> float:
    probs = predict_proba(theta, X_data)
    eps = 1e-8
    probs = np.clip(probs, eps, 1 - eps)
    return -np.mean(y_data * np.log(probs) + (1 - y_data) * np.log(1 - probs))

# Test with random initialization
theta_init = np.random.uniform(0, 2*np.pi, len(theta_params))
print(f"Random init ⟨Z₀⟩ for first sample: {expectation_Z0(theta_init, X_train[0]):.4f}")
print(f"Initial train accuracy: {accuracy_score(y_train, predict(theta_init, X_train)):.4f}")
print(f"Initial train loss:     {cross_entropy_loss(theta_init, X_train, y_train):.4f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Training with COBYLA"""))

cells.append(nbf.v4.new_code_cell(r"""# Training with COBYLA (gradient-free, robust for small parameter counts)
# This may take 2-5 minutes depending on dataset size and system

history = {"loss": [], "train_acc": [], "test_acc": []}
iteration_counter = [0]

def cost_fn(theta):
    loss = cross_entropy_loss(theta, X_train[:40], y_train[:40])  # mini-batch of 40
    history["loss"].append(loss)
    iteration_counter[0] += 1

    if iteration_counter[0] % 10 == 0:
        train_acc = accuracy_score(y_train[:40], predict(theta, X_train[:40]))
        test_acc  = accuracy_score(y_test[:20],  predict(theta, X_test[:20]))
        history["train_acc"].append(train_acc)
        history["test_acc"].append(test_acc)
        print(f"  Iter {iteration_counter[0]:4d} | Loss: {loss:.4f} | "
              f"Train: {train_acc:.4f} | Test: {test_acc:.4f}")

    return loss

print("Training VQC with COBYLA optimizer...")
print("(using mini-batch of 40 samples to keep runtime reasonable)\n")
print(f"{'Iter':>6s} {'Loss':>8s} {'Train':>8s} {'Test':>8s}")
print("-" * 36)

result = minimize(
    cost_fn,
    theta_init,
    method="COBYLA",
    options={"maxiter": 100, "rhobeg": 0.5}
)

theta_opt = result.x
print(f"\nOptimization: {result.message}")
print(f"Final loss: {result.fun:.4f}")

# Final evaluation on full dataset
final_train_acc = accuracy_score(y_train, predict(theta_opt, X_train))
final_test_acc  = accuracy_score(y_test,  predict(theta_opt, X_test))
print(f"\nFinal train accuracy: {final_train_acc:.4f}")
print(f"Final test accuracy:  {final_test_acc:.4f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Parameter Shift Rule (Quantum Gradient)"""))

cells.append(nbf.v4.new_code_cell(r"""def parameter_shift_gradient(theta: np.ndarray, x: np.ndarray, param_idx: int) -> float:
    '''
    Compute gradient of ⟨Z₀⟩ w.r.t. theta[param_idx] using parameter shift rule.
    Exact formula: ∂⟨O⟩/∂θ_i = (⟨O⟩|_{θᵢ+π/2} - ⟨O⟩|_{θᵢ-π/2}) / 2
    '''
    theta_plus  = theta.copy(); theta_plus[param_idx]  += np.pi / 2
    theta_minus = theta.copy(); theta_minus[param_idx] -= np.pi / 2

    exp_plus  = expectation_Z0(theta_plus,  x)
    exp_minus = expectation_Z0(theta_minus, x)

    return (exp_plus - exp_minus) / 2

# Compare parameter shift vs finite differences
x_sample = X_train[0]
param_test_idx = 0
eps = 1e-4

psr_grad = parameter_shift_gradient(theta_opt, x_sample, param_test_idx)
fd_grad  = (expectation_Z0(theta_opt + eps * np.eye(len(theta_opt))[param_test_idx], x_sample)
           - expectation_Z0(theta_opt - eps * np.eye(len(theta_opt))[param_test_idx], x_sample)) / (2*eps)

print("Gradient Comparison:")
print(f"  Parameter shift rule:  {psr_grad:.6f}")
print(f"  Finite difference:     {fd_grad:.6f}")
print(f"  Difference:            {abs(psr_grad - fd_grad):.2e}")
print("\nParameter shift is EXACT (no approximation error), while FD has O(ε²) error.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Training Results Visualization"""))

cells.append(nbf.v4.new_code_cell(r"""fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Loss curve
ax = axes[0][0]
ax.plot(history["loss"], lw=2, color="#2196F3")
ax.set_xlabel("Iteration"); ax.set_ylabel("Cross-Entropy Loss")
ax.set_title("VQC Training Loss", fontsize=12, fontweight="bold")
ax.grid(True, alpha=0.3)

# Accuracy curve
ax2 = axes[0][1]
iters_acc = np.arange(0, len(history["train_acc"])) * 10
ax2.plot(iters_acc, history["train_acc"], "g-o", lw=2, ms=5, label="Train")
ax2.plot(iters_acc, history["test_acc"],  "r-s", lw=2, ms=5, label="Test")
ax2.set_xlabel("Iteration"); ax2.set_ylabel("Accuracy")
ax2.set_title("Train vs Test Accuracy", fontsize=12, fontweight="bold")
ax2.legend(); ax2.grid(True, alpha=0.3); ax2.set_ylim(0, 1.1)

# Decision boundary
ax3 = axes[1][0]
xx, yy = np.meshgrid(np.linspace(0, np.pi, 60), np.linspace(0, np.pi, 60))
grid = np.c_[xx.ravel(), yy.ravel()]
Z_vqc = predict(theta_opt, grid).reshape(xx.shape)
ax3.contourf(xx, yy, Z_vqc, alpha=0.3, cmap="RdBu_r")
ax3.contour(xx, yy, Z_vqc, colors="black", linewidths=0.7)
for label, color in [(0, "#2196F3"), (1, "#FF5722")]:
    mask = y_test == label
    ax3.scatter(X_test[mask, 0], X_test[mask, 1], c=color, s=50, alpha=0.8,
                edgecolor="black", lw=0.5, label=f"Class {label}")
ax3.set_title(f"VQC Decision Boundary\nTest acc: {final_test_acc:.4f}", fontsize=12, fontweight="bold")
ax3.legend(); ax3.set_xlabel("x₁"); ax3.set_ylabel("x₂")

# Parameter values histogram
ax4 = axes[1][1]
ax4.hist(theta_init, bins=15, alpha=0.6, color="#90CAF9", edgecolor="black", label="Initial θ")
ax4.hist(theta_opt,  bins=15, alpha=0.6, color="#EF9A9A", edgecolor="black", label="Optimized θ")
ax4.set_xlabel("Parameter value"); ax4.set_ylabel("Count")
ax4.set_title("Parameter Distribution: Before vs After Training", fontsize=12, fontweight="bold")
ax4.legend()

plt.suptitle(f"VQC Training Results — {N_QUBITS} qubits, {N_LAYERS} layers, {len(theta_params)} parameters",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("vqc_training.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Optimizer Comparison

Compare COBYLA, L-BFGS-B (with parameter shift gradients), and SPSA on the same VQC. Plot convergence speed and final accuracy for each.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — optimizer comparison

from scipy.optimize import minimize
import time

def cost_with_grad(theta, use_psr=False):
    loss = cross_entropy_loss(theta, X_train[:30], y_train[:30])
    if not use_psr:
        return loss
    # Numerical gradient via parameter shift
    grad = np.array([
        parameter_shift_gradient(theta, X_train[0], i) for i in range(len(theta))
    ])
    return loss, grad

optimizers_to_compare = ["COBYLA", "Nelder-Mead"]
results_cmp = {}

for method in optimizers_to_compare:
    t0 = time.time()
    # YOUR CODE HERE: run each optimizer and record loss history
    print(f"{method}: not implemented yet")
    results_cmp[method] = {"time": time.time() - t0, "loss": []}

print("\nNote: L-BFGS-B requires gradients — use parameter_shift_gradient above.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Expressibility Analysis

For VQCs with 1, 2, 3, and 4 layers, measure how the **range of achievable outputs** changes.

Expressibility: sample 1000 random parameter vectors $\boldsymbol{\theta}$, compute $\langle Z_0\rangle$ for a fixed $\mathbf{x}$. A more expressive VQC will cover a wider range of values.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — expressibility sweep

x_fixed = np.array([1.0, 0.5])  # fixed data point
n_random_samples = 200

fig, ax = plt.subplots(figsize=(10, 4))

for n_layers_test in [1, 2, 3, 4]:
    # Temporarily adjust N_LAYERS
    theta_test_params = ParameterVector("θ", N_QUBITS * n_layers_test)
    exp_values = []
    for _ in range(n_random_samples):
        theta_random = np.random.uniform(0, 2*np.pi, len(theta_test_params))
        # YOUR CODE HERE: compute expectation value for this random theta
        # For now, use a placeholder
        exp_values.append(np.random.uniform(-1, 1))  # replace with actual

    ax.hist(exp_values, bins=30, alpha=0.5, label=f"{n_layers_test} layers",
            density=True, histtype="stepfilled")

ax.set_xlabel("⟨Z₀⟩ expectation value"); ax.set_ylabel("Density")
ax.set_title("VQC Expressibility: Distribution of ⟨Z₀⟩ for Random Parameters\n"
             "More uniform = more expressible", fontsize=11, fontweight="bold")
ax.legend(); ax.grid(True, alpha=0.3)
plt.show()
print("A perfectly expressible VQC produces a uniform distribution over [-1,1].")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Implement **gradient-based VQC training using only the parameter shift rule** (no scipy minimize):

1. Use the parameter shift rule to compute the full gradient $\nabla_\theta L$
2. Implement SGD: $\theta_{t+1} = \theta_t - \eta \nabla L(\theta_t)$
3. Train for 50 epochs using mini-batches of 10 samples
4. Compare convergence to COBYLA on the same task
5. Show the gradient magnitude over training (observe barren plateau effect)
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Parameter shift gradient descent from scratch

def full_gradient(theta, X_batch, y_batch):
    '''Compute full gradient using parameter shift rule for all parameters.'''
    grad = np.zeros_like(theta)
    for i in range(len(theta)):
        # YOUR CODE HERE: use parameter_shift_gradient for each parameter
        # Average over the batch
        pass
    return grad

def sgd_train_vqc(theta_init, X_tr, y_tr, n_epochs=50, lr=0.1, batch_size=10):
    '''SGD training loop using parameter shift gradients.'''
    theta = theta_init.copy()
    loss_history = []
    grad_norm_history = []

    for epoch in range(n_epochs):
        # Sample mini-batch
        idx = np.random.choice(len(X_tr), batch_size, replace=False)
        X_batch, y_batch = X_tr[idx], y_tr[idx]

        # YOUR CODE HERE: compute gradient and update theta
        grad = full_gradient(theta, X_batch, y_batch)
        theta = theta - lr * grad

        loss = cross_entropy_loss(theta, X_batch, y_batch)
        loss_history.append(loss)
        grad_norm_history.append(np.linalg.norm(grad))

    return theta, loss_history, grad_norm_history

print("Challenge: Implement full_gradient() and run sgd_train_vqc()")
print("Expected: loss decreases over epochs; gradient norm shows barren plateau")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Cerezo et al. (2021)** — "Variational quantum algorithms" — Nature Reviews Physics
2. **Mitarai et al. (2018)** — "Quantum circuit learning" — original parameter shift paper
3. **Schuld et al. (2019)** — "Evaluating analytic gradients on quantum hardware"
4. **Qiskit Machine Learning: VQC** — `qiskit_machine_learning.algorithms.VQC`
5. **SPSA optimizer** — "Simultaneous Perturbation Stochastic Approximation" — often preferred for QML
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DS3_variational_quantum_circuits.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
