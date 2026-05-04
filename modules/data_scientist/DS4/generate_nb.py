#!/usr/bin/env python3
"""generate_nb.py — Module DS4: Quantum Neural Networks with Qiskit"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# DS4 — Quantum Neural Networks with Qiskit
**Track:** Data Scientist | **Difficulty:** ⭐⭐⭐⭐☆ | **Est. Time:** 45 min

| | |
|---|---|
| **Prerequisites** | F1–F4, DS1–DS3; PyTorch basics helpful |
| **Qiskit Modules** | `qiskit_machine_learning`, `qiskit`, `qiskit_aer` |
| **Companion Video** | Data Scientist Module DS4 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Distinguish `SamplerQNN` and `EstimatorQNN` and select the right one for your task
2. Build a `SamplerQNN` for binary classification and compute its forward pass
3. Compute **parameter shift gradients** through a QNN
4. Connect a QNN to PyTorch via `TorchConnector` and train with standard PyTorch loop
5. Evaluate and compare to classical baselines from DS1
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Concept Summary

### SamplerQNN vs EstimatorQNN

| | `SamplerQNN` | `EstimatorQNN` |
|---|---|---|
| **Output** | Measurement probability distribution | Expectation value $\langle\hat{O}\rangle$ |
| **Based on** | `Sampler` primitive | `Estimator` primitive |
| **Use for** | Classification (discrete output) | Regression, VQE (continuous output) |
| **Output type** | Probabilities $p_i \in [0,1]$ | Real number $\in [-1,1]$ |
| **Gradient** | Parameter shift | Parameter shift |

### TorchConnector

`TorchConnector` wraps a Qiskit QNN as a PyTorch `Module`, enabling:
- **Autograd:** QNN gradients are computed via parameter shift and integrated into PyTorch's backward pass
- **Standard training loop:** use `optimizer.step()`, `loss.backward()`, etc.
- **Hybrid models:** combine quantum layers with classical pre/post-processing

```python
qnn_layer = TorchConnector(qnn)
model = nn.Sequential(classical_layer, qnn_layer, output_layer)
```

### Parameter Shift Rule (revisited)

$$\frac{\partial f}{\partial \theta_i} = \frac{f(\theta_i + \pi/2) - f(\theta_i - \pi/2)}{2}$$

Each gradient evaluation requires 2 circuit shots — scales as $O(P)$ for $P$ parameters.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 SamplerQNN Setup"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer import AerSimulator
from sklearn.datasets import make_moons
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings; warnings.filterwarnings("ignore")

np.random.seed(42)

# Dataset
X, y = make_moons(n_samples=100, noise=0.1, random_state=42)
X = MinMaxScaler(feature_range=(0, np.pi)).fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build VQC circuit
N_QUBITS = 2
N_LAYERS = 2
feature_dim = N_QUBITS
input_params  = ParameterVector("x", feature_dim)
weight_params = ParameterVector("θ", N_QUBITS * N_LAYERS)

def build_qnn_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(N_QUBITS)
    # Feature map: angle encode
    for i in range(N_QUBITS):
        qc.ry(input_params[i], i)
    qc.cx(0, 1)
    # Ansatz
    idx = 0
    for layer in range(N_LAYERS):
        for q in range(N_QUBITS):
            qc.ry(weight_params[idx], q); idx += 1
        if layer < N_LAYERS - 1:
            qc.cx(0, 1)
    return qc

qc_qnn = build_qnn_circuit()
print("QNN Circuit:")
print(qc_qnn.draw(output="text"))
print(f"\nInput parameters:  {list(input_params)}")
print(f"Weight parameters: {list(weight_params)}")

# Try to import qiskit_machine_learning
try:
    from qiskit_machine_learning.neural_networks import SamplerQNN, EstimatorQNN
    from qiskit_machine_learning.connectors import TorchConnector
    HAS_QML = True
    print("\n✓ qiskit_machine_learning available")
except ImportError:
    HAS_QML = False
    print("\n✗ qiskit_machine_learning not installed")
    print("  Install: pip install qiskit-machine-learning")
    print("  Falling back to manual implementation")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 SamplerQNN — Forward Pass"""))

cells.append(nbf.v4.new_code_cell(r"""if HAS_QML:
    from qiskit.primitives import StatevectorSampler

    # Build SamplerQNN
    sampler_qnn = SamplerQNN(
        circuit=qc_qnn,
        input_params=list(input_params),
        weight_params=list(weight_params),
        input_gradients=False,   # don't compute input gradients
        interpret=lambda x: x % 2,  # parity interpretation
        output_shape=2,          # 2 output classes
    )

    # Test forward pass
    x_sample = X_train[0]
    w_init = np.random.uniform(0, 2*np.pi, len(weight_params))

    result_fwd = sampler_qnn.forward(input_data=x_sample, weights=w_init)
    print("SamplerQNN forward pass:")
    print(f"  Input x: {np.round(x_sample, 4)}")
    print(f"  Output (class probs): {np.round(result_fwd, 4)}")
    print(f"  Predicted class: {np.argmax(result_fwd)}")
    print(f"  True label: {y_train[0]}")

else:
    # Manual implementation of SamplerQNN forward pass
    from qiskit_aer import AerSimulator
    from qiskit import transpile

    sim = AerSimulator()

    def sampler_qnn_forward(x: np.ndarray, weights: np.ndarray, n_shots: int = 1024) -> np.ndarray:
        '''Manual SamplerQNN: returns measurement probability distribution.'''
        qc = qc_qnn.copy()
        param_dict = {ip: xi for ip, xi in zip(input_params, x)}
        param_dict.update({wp: wi for wp, wi in zip(weight_params, weights)})
        qc_bound = qc.assign_parameters(param_dict)
        qc_bound.measure_all()

        job = sim.run(transpile(qc_bound, sim), shots=n_shots)
        counts = job.result().get_counts()
        total = sum(counts.values())

        probs = np.zeros(2**N_QUBITS)
        for bitstring, count in counts.items():
            idx = int(bitstring, 2)
            probs[idx] = count / total

        # Parity interpretation: class 0 = even parity, class 1 = odd parity
        class_0 = sum(probs[i] for i in range(len(probs)) if bin(i).count("1") % 2 == 0)
        class_1 = sum(probs[i] for i in range(len(probs)) if bin(i).count("1") % 2 == 1)
        return np.array([class_0, class_1])

    x_sample = X_train[0]
    w_init   = np.random.uniform(0, 2*np.pi, len(weight_params))
    result_fwd = sampler_qnn_forward(x_sample, w_init)
    print(f"Manual QNN forward: {np.round(result_fwd, 4)}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 PyTorch Training Loop with TorchConnector"""))

cells.append(nbf.v4.new_code_cell(r"""if HAS_QML:
    import torch
    import torch.nn as nn
    from torch.optim import Adam

    # Wrap QNN as PyTorch module
    initial_weights = torch.tensor(np.random.uniform(0, 2*np.pi, len(weight_params)))

    qnn_torch_layer = TorchConnector(sampler_qnn, initial_weights=initial_weights)

    # Build hybrid model: classical pre-processing + quantum layer
    model = nn.Sequential(qnn_torch_layer)

    optimizer = Adam(model.parameters(), lr=0.02)
    loss_fn   = nn.CrossEntropyLoss()

    # Training loop
    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.long)
    X_test_t  = torch.tensor(X_test, dtype=torch.float32)

    loss_history = []; acc_history = []
    n_epochs = 30

    print("Training QNN with PyTorch Adam optimizer...")
    print(f"{'Epoch':>7s} {'Loss':>10s} {'Train Acc':>12s}")
    print("-" * 32)

    for epoch in range(n_epochs):
        model.train()
        optimizer.zero_grad()

        out = model(X_train_t)
        loss = loss_fn(out, y_train_t)
        loss.backward()
        optimizer.step()

        with torch.no_grad():
            preds = torch.argmax(model(X_train_t), dim=1).numpy()
            acc   = accuracy_score(y_train, preds)

        loss_history.append(loss.item())
        acc_history.append(acc)

        if epoch % 5 == 0:
            print(f"{epoch+1:>7d} {loss.item():>10.4f} {acc:>12.4f}")

    print(f"\nFinal test accuracy: {accuracy_score(y_test, torch.argmax(model(X_test_t), dim=1).numpy()):.4f}")

else:
    # Manual gradient descent
    print("Manual QNN training (without qiskit_machine_learning):")
    print("See DS3 for manual parameter shift gradient descent implementation.")

    # Simplified manual training
    w = w_init.copy()
    lr = 0.05
    loss_history = []

    def manual_loss(w, X_b, y_b):
        probs = np.array([sampler_qnn_forward(xi, w) for xi in X_b])
        eps = 1e-8
        probs = np.clip(probs, eps, 1-eps)
        return -np.mean(np.log(probs[np.arange(len(y_b)), y_b]))

    for epoch in range(20):
        loss = manual_loss(w, X_train[:20], y_train[:20])
        loss_history.append(loss)
        # Gradient-free update (random perturbation)
        perturbation = np.random.normal(0, 0.1, len(w))
        w_new = w + lr * perturbation
        if manual_loss(w_new, X_train[:20], y_train[:20]) < loss:
            w = w_new
        print(f"  Epoch {epoch+1:3d}: loss = {loss:.4f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Visualize Training and Decision Boundary"""))

cells.append(nbf.v4.new_code_cell(r"""fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Loss curve
ax = axes[0]
ax.plot(loss_history, lw=2.5, color="#9C27B0")
ax.set_xlabel("Epoch"); ax.set_ylabel("Cross-Entropy Loss")
ax.set_title("QNN Training Loss (PyTorch + TorchConnector)", fontsize=11, fontweight="bold")
ax.grid(True, alpha=0.3)

# Accuracy curve
if 'acc_history' in dir() and len(acc_history) > 0:
    ax2 = axes[1]
    ax2.plot(acc_history, lw=2.5, color="#4CAF50", label="Train accuracy")
    ax2.set_xlabel("Epoch"); ax2.set_ylabel("Accuracy")
    ax2.set_title("Training Accuracy", fontsize=11, fontweight="bold")
    ax2.legend(); ax2.grid(True, alpha=0.3); ax2.set_ylim(0, 1.1)

# Decision boundary
ax3 = axes[2]
xx, yy = np.meshgrid(np.linspace(0, np.pi, 50), np.linspace(0, np.pi, 50))
grid = np.c_[xx.ravel(), yy.ravel()]

if HAS_QML:
    with torch.no_grad():
        grid_t = torch.tensor(grid, dtype=torch.float32)
        Z_qnn = torch.argmax(model(grid_t), dim=1).numpy().reshape(xx.shape)
else:
    Z_qnn = np.array([np.argmax(sampler_qnn_forward(xi, w)) for xi in grid]).reshape(xx.shape)

ax3.contourf(xx, yy, Z_qnn, alpha=0.3, cmap="RdBu_r")
ax3.contour(xx, yy, Z_qnn, colors="black", linewidths=0.7)
for label, color in [(0, "#2196F3"), (1, "#FF5722")]:
    mask = y_test == label
    ax3.scatter(X_test[mask, 0], X_test[mask, 1], c=color, s=50, alpha=0.8,
                label=f"Class {label}", edgecolor="black", lw=0.5)
ax3.set_title("QNN Decision Boundary", fontsize=11, fontweight="bold")
ax3.legend(); ax3.set_xlabel("x₁"); ax3.set_ylabel("x₂")

plt.suptitle("Quantum Neural Network (SamplerQNN + TorchConnector) — Full Training Pipeline",
             fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("qnn_training.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — EstimatorQNN

Build an `EstimatorQNN` using the same circuit but measuring $\langle Z_0 \otimes Z_1 \rangle$ instead of probabilities. Compare the decision boundary shape.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — EstimatorQNN

if HAS_QML:
    from qiskit_machine_learning.neural_networks import EstimatorQNN

    # Observable: Z₀ ⊗ Z₁
    observable = SparsePauliOp.from_list([("ZZ", 1.0)])

    est_qnn = EstimatorQNN(
        circuit=qc_qnn,
        observables=observable,
        input_params=list(input_params),
        weight_params=list(weight_params),
    )

    # Forward pass: returns single real number in [-1, 1]
    est_result = est_qnn.forward(input_data=X_train[0],
                                  weights=np.random.uniform(0, 2*np.pi, len(weight_params)))
    print(f"EstimatorQNN forward: ⟨ZZ⟩ = {est_result:.4f}")
    print("This is a regression output — threshold at 0 for binary classification")

    # YOUR CODE HERE: wrap with TorchConnector and train for binary classification
    # Threshold: ⟨ZZ⟩ > 0 → class 1, else class 0
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Hybrid Classical-Quantum Model

Add a classical preprocessing layer before the quantum layer:

```
Classical Dense(2→4, ReLU) → Quantum QNN(4→2) → Softmax
```

This is a **hybrid model** — classical layers extract features, quantum layer classifies.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — hybrid model
if HAS_QML:
    import torch.nn as nn

    class HybridModel(nn.Module):
        def __init__(self, qnn_layer):
            super().__init__()
            self.classical = nn.Linear(2, 2)  # classical pre-processing
            self.quantum   = qnn_layer
            self.softmax   = nn.Softmax(dim=1)

        def forward(self, x):
            x = torch.relu(self.classical(x))  # classical feature extraction
            x = self.quantum(x)                 # quantum classification
            return self.softmax(x)

    hybrid_model = HybridModel(TorchConnector(sampler_qnn))
    print("Hybrid Model:")
    print(hybrid_model)
    print(f"\nClassical parameters: {sum(p.numel() for p in hybrid_model.classical.parameters())}")
    print(f"Quantum parameters:   {sum(p.numel() for p in hybrid_model.quantum.parameters())}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Implement **quantum transfer learning**: use a pre-trained classical CNN as a feature extractor, and replace only the final classification layer with a quantum QNN.

1. Use a pre-trained 4-class classical model on sklearn's iris dataset
2. Extract penultimate layer features (4D output of the classical portion)
3. Feed these 4 features into a 4-qubit QNN (angle encoding)
4. Compare accuracy to a classical linear layer replacement
5. Analyze: does quantum transfer learning help or hurt?
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Quantum Transfer Learning
from sklearn.datasets import load_iris
from sklearn.preprocessing import MinMaxScaler

iris = load_iris()
X_iris = MinMaxScaler(feature_range=(0, np.pi)).fit_transform(iris.data)
y_iris = (iris.target == 0).astype(int)  # Binary: setosa vs not

print("Iris dataset (binary: setosa vs rest):")
print(f"  Shape: {X_iris.shape}")
print(f"  Classes: {np.unique(y_iris)}")

if HAS_QML:
    # 4-qubit QNN for 4 iris features
    n_q = 4
    in_p  = ParameterVector("x", n_q)
    wt_p  = ParameterVector("θ", n_q * 2)

    qc_iris = QuantumCircuit(n_q)
    for i in range(n_q): qc_iris.ry(in_p[i], i)
    for i in range(n_q-1): qc_iris.cx(i, i+1)
    idx = 0
    for layer in range(2):
        for q in range(n_q): qc_iris.ry(wt_p[idx], q); idx += 1
        if layer < 1:
            for q in range(n_q-1): qc_iris.cx(q, q+1)

    qnn_iris = SamplerQNN(circuit=qc_iris, input_params=list(in_p),
                          weight_params=list(wt_p), output_shape=2)
    print("\nChallenge: Train this 4-qubit QNN on iris and compare to classical baseline.")
else:
    print("Challenge requires qiskit_machine_learning — install it and retry.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Qiskit Machine Learning Docs** — SamplerQNN and EstimatorQNN API reference
2. **Mari et al. (2020)** — "Transfer learning in hybrid classical-quantum neural networks" — arXiv:1912.08278
3. **Havlíček et al. (2019)** — "Supervised learning with quantum-enhanced feature spaces" — Nature 567
4. **TorchConnector tutorial** — Qiskit Machine Learning GitHub examples
5. **Benedetti et al. (2019)** — "Parameterized quantum circuits as machine learning models" — arXiv:1906.07682
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DS4_quantum_neural_networks.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
