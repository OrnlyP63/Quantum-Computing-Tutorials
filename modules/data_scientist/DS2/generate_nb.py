#!/usr/bin/env python3
"""generate_nb.py — Module DS2: Encoding Classical Data into Quantum Circuits"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# DS2 — Encoding Classical Data into Quantum Circuits
**Track:** Data Scientist | **Difficulty:** ⭐⭐⭐☆☆ | **Est. Time:** 30 min

| | |
|---|---|
| **Prerequisites** | F1–F4, DS1; numpy, sklearn |
| **Qiskit Modules** | `qiskit`, `qiskit.circuit.library.ZZFeatureMap` |
| **Companion Video** | Data Scientist Module DS2 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Explain the **three main encoding strategies**: basis, angle, and amplitude encoding
2. Implement **angle encoding** manually and via `ZZFeatureMap`
3. Understand why `ZZFeatureMap` creates **non-trivial entanglement** between features
4. Visualize how different data points map to **distinct quantum states**
5. Analyze the **expressibility** tradeoff between encoding complexity and circuit depth
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Data Encoding Strategies

### The Fundamental Challenge

Quantum computers operate on quantum states. Classical data (vectors of real numbers) must be **embedded** into quantum states before any quantum advantage can be exploited.

### 1. Basis Encoding

Encode integer index $x$ as a computational basis state $|x\rangle$:

$$x = 5 = (101)_2 \to |101\rangle$$

- **Pro:** Simple, classical bitstring maps directly
- **Con:** Requires $O(N)$ circuit size to prepare arbitrary superposition; can't leverage quantum parallelism for continuous data

### 2. Angle Encoding (Rotation Encoding)

Encode feature vector $\mathbf{x} \in \mathbb{R}^n$ as rotation angles on $n$ qubits:

$$\mathbf{x} = (x_1, \ldots, x_n) \to \bigotimes_{i=1}^n R_y(x_i)|0\rangle$$

$$\text{State: } \prod_{i=1}^n \big(\cos(x_i/2)|0\rangle + \sin(x_i/2)|1\rangle\big)$$

- **Pro:** $n$ features → $n$ qubits; compact, hardware-efficient
- **Con:** No feature interaction without entangling layers

### 3. Amplitude Encoding

Encode $2^n$-dimensional normalized vector $\mathbf{x}$ directly into amplitudes:

$$\mathbf{x} = (x_0, \ldots, x_{2^n-1}) \to \sum_i x_i |i\rangle$$

- **Pro:** Exponentially compact — $2^n$ features in $n$ qubits
- **Con:** State preparation is expensive ($O(2^n)$ gates in general)

### 4. ZZFeatureMap (Product Feature Map)

Creates **non-linear, entangled** feature representations:

$$U_{\phi}(\mathbf{x}) = \exp\!\left(i\sum_{S \subseteq [n]} \phi_S(\mathbf{x}) \prod_{k \in S} Z_k\right) H^{\otimes n}$$

The $ZZ$ interactions create correlations like the kernel trick: $\phi_{\{j,k\}}(\mathbf{x}) = (\pi - x_j)(\pi - x_k)$.

> **DS Bridge:** Feature maps in quantum ML = feature engineering pipelines. ZZFeatureMap ≈ polynomial feature expansion applied at the quantum level.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Encoding Strategy 1 — Basis Encoding"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def basis_encode(x: int, n_bits: int) -> QuantumCircuit:
    '''Encode integer x into |x⟩ basis state using X gates.'''
    qc = QuantumCircuit(n_bits, name=f"|{x:0{n_bits}b}⟩")
    binary = format(x, f"0{n_bits}b")
    for i, bit in enumerate(reversed(binary)):  # little-endian
        if bit == "1":
            qc.x(i)
    return qc

# Demonstrate for 3 qubits (8 possible states)
n_bits = 3
print("Basis Encoding: integer → quantum basis state")
print(f"{'Integer':10s} {'Binary':8s} {'State':10s} {'P(0...0)':12s}")
print("-" * 45)
for x in range(8):
    qc = basis_encode(x, n_bits)
    sv = Statevector(qc)
    # Which state has amplitude 1?
    state_idx = np.argmax(np.abs(sv.data))
    print(f"{x:10d} {x:08b}   |{x:03b}⟩     {abs(sv.data[x])**2:.3f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Encoding Strategy 2 — Angle Encoding"""))

cells.append(nbf.v4.new_code_cell(r"""def angle_encode(x: np.ndarray) -> QuantumCircuit:
    '''Angle encoding: feature x[i] → Ry(x[i]) on qubit i.'''
    n = len(x)
    qc = QuantumCircuit(n, name="AngleEnc")
    for i, xi in enumerate(x):
        qc.ry(xi, i)
    return qc

# Compare two different data points
x1 = np.array([0.3, 1.2])
x2 = np.array([2.1, 0.8])

qc1 = angle_encode(x1)
qc2 = angle_encode(x2)
sv1 = Statevector(qc1)
sv2 = Statevector(qc2)

print("Angle Encoding:")
print(f"\nData point x₁ = {x1}:")
print(f"  State: {np.round(sv1.data, 4)}")
print(f"  Interpretation: each qubit i in state cos(xᵢ/2)|0⟩ + sin(xᵢ/2)|1⟩")

print(f"\nData point x₂ = {x2}:")
print(f"  State: {np.round(sv2.data, 4)}")

# Inner product (quantum similarity)
inner = abs(sv1.data.conj() @ sv2.data)**2
print(f"\n|⟨x₁|x₂⟩|² (quantum similarity) = {inner:.4f}")
print(f"Classical cosine similarity = {np.dot(x1/np.linalg.norm(x1), x2/np.linalg.norm(x2)):.4f}")

# Visualize angle encoding geometry
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Dataset of 30 points, show their angle-encoded states
from sklearn.datasets import make_moons
from sklearn.preprocessing import MinMaxScaler

X_demo, y_demo = make_moons(n_samples=60, noise=0.1, random_state=42)
X_demo_scaled = MinMaxScaler(feature_range=(0, np.pi)).fit_transform(X_demo)

# For qubit 0 and 1 separately, show angle encoding
for ax_idx, (ax, qubit) in enumerate(zip(axes, [0, 1])):
    for label, color in [(0, "#2196F3"), (1, "#FF5722")]:
        mask = y_demo == label
        angles = X_demo_scaled[mask, qubit]
        ax.scatter(np.cos(angles), np.sin(angles), c=color, s=50, alpha=0.7,
                   label=f"Class {label}", edgecolor="black", lw=0.5)

    theta_range = np.linspace(0, np.pi, 100)
    ax.plot(np.cos(theta_range), np.sin(theta_range), "gray", ls="--", alpha=0.5, lw=1.5)
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-0.1, 1.5)
    ax.axhline(0, color="black", lw=0.8); ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("cos(x)"); ax.set_ylabel("sin(x)")
    ax.set_title(f"Qubit {qubit}: Angle Encoding of x_{qubit+1}\n"
                 "Each data point maps to a point on the unit circle", fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)

plt.suptitle("Angle Encoding: Data Points → Qubit States on the Bloch Sphere Equator",
             fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("angle_encoding.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Encoding Strategy 3 — ZZFeatureMap"""))

cells.append(nbf.v4.new_code_cell(r"""try:
    from qiskit.circuit.library import ZZFeatureMap, ZFeatureMap, PauliFeatureMap
    HAS_ZZ = True
except ImportError:
    HAS_ZZ = False
    print("ZZFeatureMap not available — implementing manually")

if HAS_ZZ:
    # ZZFeatureMap: creates non-linear entangled feature representations
    n_features = 2

    for reps in [1, 2, 3]:
        fm = ZZFeatureMap(feature_dimension=n_features, reps=reps)
        print(f"\nZZFeatureMap (reps={reps}):")
        print(f"  Parameters: {fm.parameters}")
        print(f"  Circuit depth: {fm.decompose().depth()}")
        print(f"  Gate count: {dict(fm.decompose().count_ops())}")

    # Visualize one repetition
    fm1 = ZZFeatureMap(feature_dimension=n_features, reps=1)
    print("\nZZFeatureMap (reps=1) circuit:")
    print(fm1.decompose().draw(output="text"))
else:
    # Manual ZZ-like feature map
    from qiskit.circuit import ParameterVector

    def manual_zzfm(x: np.ndarray) -> QuantumCircuit:
        '''Manual ZZ feature map with Hadamard + Rz + ZZ coupling.'''
        n = len(x)
        qc = QuantumCircuit(n, name="ZZ-FM")
        qc.h(range(n))
        for i in range(n):
            qc.rz(2 * x[i], i)
        for i in range(n - 1):
            phi_ij = 2 * (np.pi - x[i]) * (np.pi - x[i+1])
            qc.cx(i, i+1)
            qc.rz(phi_ij, i+1)
            qc.cx(i, i+1)
        return qc

    print("Manual ZZ Feature Map:")
    print(manual_zzfm(np.array([1.0, 2.0])).draw(output="text"))
"""))

cells.append(nbf.v4.new_code_cell(r"""# Visualize how ZZFeatureMap separates classes better than angle encoding

if HAS_ZZ:
    from qiskit.circuit import ParameterVector

    n_feat = 2
    X_demo2, y_demo2 = make_moons(n_samples=80, noise=0.1, random_state=42)
    X_demo2_s = MinMaxScaler(feature_range=(0, 2*np.pi)).fit_transform(X_demo2)

    fm = ZZFeatureMap(feature_dimension=n_feat, reps=2)
    params = list(fm.parameters)

    # Extract quantum features (statevector after feature map)
    feat_0, feat_1 = [], []
    for xi, yi in zip(X_demo2_s[:40], y_demo2[:40]):
        bound = fm.assign_parameters(dict(zip(params, xi)))
        sv    = Statevector(bound)
        # Use first two amplitude squares as "quantum features"
        q_feats = np.abs(sv.data)**2
        if yi == 0: feat_0.append(q_feats[:4])
        else:       feat_1.append(q_feats[:4])

    feat_0 = np.array(feat_0); feat_1 = np.array(feat_1)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # Original space
    for label, color, data in [(0,"#2196F3",X_demo2_s[:40][y_demo2[:40]==0]),
                               (1,"#FF5722",X_demo2_s[:40][y_demo2[:40]==1])]:
        axes[0].scatter(data[:,0], data[:,1], c=color, s=40, alpha=0.8,
                        label=f"Class {label}", edgecolor="black", lw=0.5)
    axes[0].set_title("Original Feature Space\n(scaled to [0,2π])", fontsize=11, fontweight="bold")
    axes[0].legend()

    # ZZFeatureMap projected features (first 2 quantum features)
    for feat_arr, color, label in [(feat_0,"#2196F3","Class 0"),(feat_1,"#FF5722","Class 1")]:
        axes[1].scatter(feat_arr[:,0], feat_arr[:,1], c=color, s=40, alpha=0.8,
                        label=label, edgecolor="black", lw=0.5)
    axes[1].set_title("ZZFeatureMap Space\n(quantum amplitudes |α₀|², |α₁|²)", fontsize=11, fontweight="bold")
    axes[1].legend()

    # Kernel matrix heatmap (approximate)
    n_show = min(20, len(X_demo2_s))
    K = np.zeros((n_show, n_show))
    for i in range(n_show):
        for j in range(n_show):
            sv_i = Statevector(fm.assign_parameters(dict(zip(params, X_demo2_s[i]))))
            sv_j = Statevector(fm.assign_parameters(dict(zip(params, X_demo2_s[j]))))
            K[i,j] = abs(sv_i.data.conj() @ sv_j.data)**2

    im = axes[2].imshow(K, cmap="Blues", vmin=0, vmax=1)
    axes[2].set_title(f"ZZFeatureMap Kernel Matrix K[i,j]=|⟨φᵢ|φⱼ⟩|²\n(first {n_show} samples)", fontsize=10, fontweight="bold")
    plt.colorbar(im, ax=axes[2], fraction=0.046)

    plt.suptitle("ZZFeatureMap: Non-Linear Feature Transformation into Quantum Hilbert Space",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig("zzfeaturemap.png", dpi=120, bbox_inches="tight")
    plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Amplitude Encoding"""))

cells.append(nbf.v4.new_code_cell(r"""# Amplitude encoding: N-dimensional normalized vector → n = log2(N) qubits
# Requires state initialization

def amplitude_encode(x: np.ndarray) -> QuantumCircuit:
    '''
    Amplitude encoding: normalized x ∈ R^N → quantum state with N amplitudes.
    Uses Qiskit's initialize instruction.
    '''
    N = len(x)
    n = int(np.ceil(np.log2(N)))
    # Pad to power of 2 and normalize
    x_padded = np.zeros(2**n)
    x_padded[:N] = x
    norm = np.linalg.norm(x_padded)
    if norm > 0: x_padded = x_padded / norm

    qc = QuantumCircuit(n, name="AmpEnc")
    qc.initialize(x_padded)
    return qc

# Encode a 4-dimensional data vector
x_amp = np.array([0.5, 1.2, 0.8, 2.1])
x_amp_norm = x_amp / np.linalg.norm(x_amp)

qc_amp = amplitude_encode(x_amp)
sv_amp = Statevector(qc_amp)

print("Amplitude Encoding:")
print(f"Input: {x_amp}")
print(f"Normalized: {np.round(x_amp_norm, 4)}")
print(f"\nEncoded in {qc_amp.num_qubits} qubits:")
for i, (target, actual) in enumerate(zip(x_amp_norm, sv_amp.data)):
    print(f"  Amplitude {i}: target={target:.4f}, actual={actual.real:.4f}  match={np.isclose(target, actual.real)}")

# Compare encoding strategies
print("\n\nEncoding Strategy Comparison:")
print(f"{'Strategy':20s} {'Qubits for N feats':20s} {'Circuit depth':15s} {'Entanglement':15s}")
print("-" * 72)
print(f"{'Basis encoding':20s} {'log₂(N)':20s} {'O(log N)':15s} {'None':15s}")
print(f"{'Angle encoding':20s} {'N qubits':20s} {'O(1)':15s} {'None':15s}")
print(f"{'Amplitude encoding':20s} {'log₂(N)':20s} {'O(N)':15s} {'Full':15s}")
print(f"{'ZZFeatureMap':20s} {'N qubits':20s} {'O(N²·reps)':15s} {'Entangled':15s}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Custom Feature Map

Implement a custom feature map that encodes 2D data using:
- $R_x(x_1)$ on qubit 0
- $R_y(x_2)$ on qubit 1
- A CNOT then $R_z(x_1 \cdot x_2)$ to create a product feature

Verify that it distinguishes the two moon classes better than simple angle encoding.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — custom product feature map

from qiskit.circuit import ParameterVector

def product_feature_map(x: np.ndarray) -> QuantumCircuit:
    '''Custom feature map with product features.'''
    qc = QuantumCircuit(2, name="ProductFM")
    # YOUR CODE HERE
    # qc.rx(x[0], 0)
    # qc.ry(x[1], 1)
    # qc.cx(0, 1)
    # qc.rz(x[0] * x[1], 1)
    return qc

# Test: do points from different classes map to more distinguishable states?
from sklearn.datasets import make_moons
from sklearn.preprocessing import MinMaxScaler

X_ex, y_ex = make_moons(n_samples=20, noise=0.05, random_state=42)
X_ex_s = MinMaxScaler(feature_range=(0, np.pi)).fit_transform(X_ex)

inner_products_same  = []
inner_products_diff  = []

for i in range(len(X_ex_s)):
    for j in range(i+1, len(X_ex_s)):
        # YOUR CODE HERE: compute quantum inner product for each pair
        pass

# YOUR CODE HERE: plot histogram of inner products for same vs different class pairs
print("Challenge: implement and show inner products separate classes better with product features")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Encoding Fidelity

For amplitude encoding of a $2^n$-dimensional vector, verify that:
1. The encoded state has unit norm
2. The measurement probabilities match $|x_i|^2 / \|\mathbf{x}\|^2$
3. The state can be recovered (approximately) from repeated measurement
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — amplitude encoding verification
from qiskit_aer import AerSimulator
from qiskit import transpile

sim = AerSimulator()

x_test = np.array([1.0, 2.0, 3.0, 4.0])
x_test_norm = x_test / np.linalg.norm(x_test)
expected_probs = x_test_norm**2

qc_ae = amplitude_encode(x_test)
sv_ae = Statevector(qc_ae)

print("Amplitude Encoding Verification:")
print(f"{'State':6s} {'Target amplitude':18s} {'Actual amplitude':18s} {'Expected P':12s} {'Actual P':10s}")
print("-" * 68)
for i in range(len(x_test)):
    print(f"|{i:02b}⟩   {x_test_norm[i]:>12.4f}       {sv_ae.data[i].real:>12.4f}       "
          f"{expected_probs[i]:>10.4f}   {abs(sv_ae.data[i])**2:>10.4f}")

# Verify normalization
print(f"\nNorm: {np.linalg.norm(sv_ae.data):.6f}  (should be 1.0)")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Implement **data re-uploading** — a technique where the same data is encoded multiple times through the circuit, interleaved with trainable layers:

$$U(\mathbf{x}, \boldsymbol{\theta}) = W_L U(\mathbf{x}) W_{L-1} U(\mathbf{x}) \cdots W_1 U(\mathbf{x})$$

This is proven to make VQCs universal function approximators.

1. Build a 2-qubit, 3-layer re-uploading circuit
2. For a fixed data point $\mathbf{x}$, sweep the trainable parameters $\theta$ and show how the output varies
3. Compare the expressibility (range of achievable outputs) to a circuit without re-uploading
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Data Re-uploading
from qiskit.circuit import ParameterVector

def data_reuploading(n: int, n_layers: int, x: np.ndarray, theta: ParameterVector) -> QuantumCircuit:
    '''
    Data re-uploading: encode x multiple times interleaved with trainable W layers.
    '''
    qc = QuantumCircuit(n, name="DataReupload")
    x_fixed = {f"x{i}": x[i] for i in range(n)}
    theta_idx = 0

    for layer in range(n_layers):
        # Data encoding layer
        for q in range(n):
            qc.ry(x[q % len(x)], q)  # YOUR CODE: use actual Parameter binding

        # Trainable layer
        for q in range(n):
            qc.ry(theta[theta_idx], q)
            theta_idx += 1
        for q in range(n - 1):
            qc.cx(q, q + 1)

    return qc

n = 2; n_layers = 3
theta_params = ParameterVector("θ", n * n_layers)
x_point = np.array([1.2, 0.8])

qc_reupload = data_reuploading(n, n_layers, x_point, theta_params)
print("Data Re-uploading Circuit:")
print(qc_reupload.draw(output="text"))
print(f"\nNumber of trainable parameters: {len(theta_params)}")
print("Challenge: sweep theta values and measure output expressibility")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Pérez-Salinas et al. (2020)** — "Data re-uploading for a universal quantum classifier" — arXiv:1907.02085
2. **Schuld et al. (2021)** — "Effect of data encoding on the expressive power of variational quantum ML models"
3. **Qiskit circuit.library.ZZFeatureMap** — Official API documentation
4. **Havlíček et al. (2019)** — "Supervised learning with quantum-enhanced feature spaces" — Nature 567
5. **LaRose & Coyle (2020)** — "Robust data encodings for quantum classifiers" — arXiv:2003.01695
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DS2_data_encoding.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
