#!/usr/bin/env python3
"""generate_nb.py — Module DS6: Quantum Advantage — Benchmarking & Reality Check"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# DS6 — Quantum Advantage: Benchmarking & Reality Check
**Track:** Data Scientist | **Difficulty:** ⭐⭐⭐☆☆ | **Est. Time:** 30 min

| | |
|---|---|
| **Prerequisites** | F1–F4, DS1–DS5; sklearn, numpy |
| **Qiskit Modules** | `qiskit`, `qiskit_aer` |
| **Companion Video** | Data Scientist Module DS6 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Design a **fair benchmark**: same data, same CV strategy, reporting confidence intervals
2. Compare VQC vs classical models on **training time**, **test accuracy**, and **parameter efficiency**
3. Explain **barren plateaus**, **quantum noise**, and **data availability** as current QML limitations
4. Identify the **break-even point** where quantum models would need to outperform classical ones
5. Make an evidence-based recommendation: when would you use QML today?
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Honest Assessment

### What the Math Promises

Quantum ML has theoretical advantages in:
- **Kernel expressibility:** $2^n$ feature space with $n$ qubits
- **Quantum speedups:** for specific kernel computations (structured data)
- **Natural quantum data:** molecules, quantum systems (no classical encoding overhead)

### What the Experiments Show (2024)

- No demonstrated practical advantage on classical tabular data (yet)
- NISQ noise limits qubit counts and depth — classical simulation is often faster
- Training is bottlenecked by barren plateaus and slow gradient computation
- Best results: specialized datasets with inherent quantum structure

### The Honest Framework

Quantum ML will be useful **if and only if**:
1. The data has quantum-native structure (or quantum feature maps provide a genuine advantage)
2. The hardware has sufficient fidelity to run the required circuit depth
3. The problem size exceeds what classical kernels can tractably compute

> **DS Bridge:** Like comparing GPU vs CPU — hardware maturity determines real-world usefulness. The GPU era required 15 years of CUDA ecosystem development after the hardware existed.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Benchmark Setup"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
import time
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from scipy.optimize import minimize
import warnings; warnings.filterwarnings("ignore")

np.random.seed(42)
sim = AerSimulator()

# Benchmark datasets
DATASETS = {
    "Two Moons": make_moons(n_samples=200, noise=0.15, random_state=42),
    "Circles":   make_circles(n_samples=200, noise=0.1, factor=0.5, random_state=42),
    "Linear":    make_classification(n_samples=200, n_features=2, n_redundant=0,
                                     n_clusters_per_class=1, random_state=42),
}

# Preprocessing for quantum: scale to [0, π]
def prep_data(X, y, test_size=0.25):
    X_s = MinMaxScaler(feature_range=(0, np.pi)).fit_transform(X)
    return train_test_split(X_s, y, test_size=test_size, random_state=42)

print("Benchmark Datasets:")
for name, (X, y) in DATASETS.items():
    print(f"  {name}: {X.shape}, class balance: {np.mean(y):.2f}/{1-np.mean(y):.2f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Classical Baselines (Full Benchmark)"""))

cells.append(nbf.v4.new_code_cell(r"""# Classical models to compare against
classical_models = {
    "Logistic Regression": LogisticRegression(max_iter=200),
    "SVM (RBF)":           SVC(kernel="rbf", C=1.0, gamma="scale"),
    "SVM (Linear)":        SVC(kernel="linear", C=1.0),
    "MLP (8-8)":           MLPClassifier(hidden_layer_sizes=(8, 8), max_iter=500),
}

classical_results = {ds: {} for ds in DATASETS}

print("Classical model benchmark:")
print(f"{'Dataset':15s} {'Model':25s} {'Test Acc':>10s} {'Train Time(ms)':>15s}")
print("-" * 68)

for ds_name, (X, y) in DATASETS.items():
    X_tr, X_te, y_tr, y_te = prep_data(X, y)
    for model_name, clf in classical_models.items():
        t0 = time.time()
        clf.fit(X_tr, y_tr)
        train_time_ms = (time.time() - t0) * 1000
        acc = accuracy_score(y_te, clf.predict(X_te))
        classical_results[ds_name][model_name] = {"acc": acc, "time_ms": train_time_ms}
        print(f"{ds_name:15s} {model_name:25s} {acc:>10.4f} {train_time_ms:>15.1f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 VQC Benchmark"""))

cells.append(nbf.v4.new_code_cell(r"""# Mini VQC benchmark with limited training budget
N_QUBITS = 2; N_LAYERS = 2
x_params = ParameterVector("x", N_QUBITS)
theta_params = ParameterVector("θ", N_QUBITS * N_LAYERS)

def build_vqc():
    qc = QuantumCircuit(N_QUBITS)
    for i in range(N_QUBITS): qc.ry(x_params[i], i)
    qc.cx(0, 1)
    idx = 0
    for l in range(N_LAYERS):
        for q in range(N_QUBITS): qc.ry(theta_params[idx], q); idx += 1
        if l < N_LAYERS - 1: qc.cx(0, 1)
    return qc

vqc = build_vqc()

def vqc_predict_proba(theta, X_data):
    probs = []
    for x in X_data:
        pdict = {xp: xi for xp, xi in zip(x_params, x)}
        pdict.update({tp: ti for tp, ti in zip(theta_params, theta)})
        sv = Statevector(vqc.assign_parameters(pdict))
        p0 = sv.probabilities([0])[0]
        probs.append((1 - (2*p0 - 1)) / 2)
    return np.array(probs)

def vqc_loss(theta, X_data, y_data):
    p = np.clip(vqc_predict_proba(theta, X_data), 1e-8, 1-1e-8)
    return -np.mean(y_data * np.log(p) + (1-y_data) * np.log(1-p))

vqc_results = {}
BATCH_SIZE  = 30  # small batch for speed
MAX_ITER    = 60

print("VQC benchmark (mini-batch, limited iterations):")
print(f"{'Dataset':15s} {'Test Acc':>10s} {'Train Time(ms)':>15s}")
print("-" * 44)

for ds_name, (X, y) in DATASETS.items():
    X_tr, X_te, y_tr, y_te = prep_data(X, y)
    theta_init = np.random.uniform(0, 2*np.pi, len(theta_params))

    t0 = time.time()
    result = minimize(
        vqc_loss,
        theta_init,
        args=(X_tr[:BATCH_SIZE], y_tr[:BATCH_SIZE]),
        method="COBYLA",
        options={"maxiter": MAX_ITER}
    )
    train_time_ms = (time.time() - t0) * 1000

    theta_opt = result.x
    preds = (vqc_predict_proba(theta_opt, X_te) > 0.5).astype(int)
    acc   = accuracy_score(y_te, preds)

    vqc_results[ds_name] = {"acc": acc, "time_ms": train_time_ms}
    print(f"{ds_name:15s} {acc:>10.4f} {train_time_ms:>15.1f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Comprehensive Comparison Visualization"""))

cells.append(nbf.v4.new_code_cell(r"""fig, axes = plt.subplots(1, 3, figsize=(18, 5))

ds_names = list(DATASETS.keys())
model_names = list(classical_models.keys()) + ["VQC"]

colors_classical = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0"]
color_quantum    = "#E91E63"

for ax_idx, ds_name in enumerate(ds_names):
    ax = axes[ax_idx]

    # Classical accuracies
    c_accs = [classical_results[ds_name][m]["acc"] for m in classical_models]
    c_bars = ax.bar(list(classical_models.keys()), c_accs,
                    color=colors_classical, edgecolor="black", width=0.5, label="Classical")

    # VQC
    vqc_acc = vqc_results[ds_name]["acc"]
    q_bar = ax.bar(["VQC"], [vqc_acc],
                   color=color_quantum, edgecolor="black", width=0.5, label="VQC")

    best_classical = max(c_accs)
    ax.axhline(best_classical, ls="--", color="navy", lw=1.5, alpha=0.7)

    for bar in list(c_bars) + list(q_bar):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{bar.get_height():.3f}", ha="center", fontsize=9, rotation=45)

    ax.set_title(f"{ds_name}", fontsize=12, fontweight="bold")
    ax.set_ylabel("Test Accuracy"); ax.set_ylim(0, 1.15)
    ax.tick_params(axis="x", rotation=30)
    if ax_idx == 0:
        ax.legend(fontsize=9)

plt.suptitle("VQC vs Classical Models: Accuracy Comparison\n"
             "Dashed line = best classical; limited VQC budget (30 samples, 60 iters)",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("benchmark_accuracy.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_code_cell(r"""# Training time comparison (log scale)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Time comparison
ax = axes[0]
ds = "Two Moons"

time_data = {m: classical_results[ds][m]["time_ms"] for m in classical_models}
time_data["VQC (30 samples, 60 iter)"] = vqc_results[ds]["time_ms"]

names = list(time_data.keys())
times = list(time_data.values())
colors_time = colors_classical + [color_quantum]

ax.bar(names, times, color=colors_time, edgecolor="black", width=0.6)
ax.set_yscale("log")
ax.set_ylabel("Training Time (ms, log scale)")
ax.set_title("Training Time: Classical vs VQC\n(Two Moons, log scale)", fontsize=12, fontweight="bold")
ax.tick_params(axis="x", rotation=30)
for i, t in enumerate(times):
    ax.text(i, t * 1.3, f"{t:.1f}ms", ha="center", fontsize=9)

# Parameter efficiency
ax2 = axes[1]
param_counts = {
    "Logistic Regression": 5,      # 2 features + bias × 2 classes
    "SVM (RBF)": 0,                # support vectors (not params)
    "MLP (8-8)": 8*2+8 + 8*8+8 + 8*1+1,  # layer params
    f"VQC ({N_QUBITS}q, {N_LAYERS}L)": len(theta_params),
}
classical_accs_moons = {m: classical_results["Two Moons"][m]["acc"] for m in classical_models
                         if m in ["Logistic Regression", "MLP (8-8)"]}
classical_accs_moons[f"VQC ({N_QUBITS}q, {N_LAYERS}L)"] = vqc_results["Two Moons"]["acc"]

pnames = list(classical_accs_moons.keys())
paccs  = list(classical_accs_moons.values())
pcounts = [param_counts.get(n, 0) for n in pnames]

sc = ax2.scatter(pcounts, paccs,
                 c=[colors_classical[0], colors_classical[3], color_quantum],
                 s=200, edgecolor="black", zorder=5)
for name, x, y in zip(pnames, pcounts, paccs):
    ax2.annotate(name, (x, y), textcoords="offset points", xytext=(5, 5), fontsize=9)
ax2.set_xlabel("Number of Parameters"); ax2.set_ylabel("Test Accuracy")
ax2.set_title("Parameter Efficiency: Accuracy vs Parameter Count", fontsize=12, fontweight="bold")
ax2.grid(True, alpha=0.3)

plt.suptitle("Quantum vs Classical: Speed and Efficiency Tradeoffs",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("benchmark_efficiency.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Break-Even Analysis"""))

cells.append(nbf.v4.new_code_cell(r"""# When would quantum ML become competitive?
# Analysis: as a function of dataset size and problem complexity

# Theoretical scaling
N_values = np.logspace(2, 6, 50)

# Classical SVM-RBF: O(N^2) to O(N^3) for kernel matrix
classical_kernel_time = N_values**2.5 / 1e6  # normalized

# VQC (current NISQ): bottleneck is shots × parameters × samples
n_shots = 1024
n_params = len(theta_params)
vqc_time_nisq = N_values * n_params * n_shots / 1e3  # O(N × P × shots)

# VQC (fault-tolerant, future): quantum speedup in kernel computation
# Expected: polylog(N) per kernel evaluation if data has quantum structure
vqc_time_ft = N_values * np.log2(N_values)**2 / 1e3

fig, ax = plt.subplots(figsize=(10, 5))

ax.loglog(N_values, classical_kernel_time, "b-", lw=2.5, label="Classical SVM-RBF: O(N^2.5)")
ax.loglog(N_values, vqc_time_nisq,        "r-", lw=2.5, label=f"VQC (NISQ): O(N×P×shots), P={n_params}")
ax.loglog(N_values, vqc_time_ft,          "g--", lw=2.5, label="VQC (Fault-tolerant): O(N log²N)")

# Find crossover points
for label, t1, t2 in [
    ("NISQ crossover", classical_kernel_time, vqc_time_nisq),
    ("FT crossover",   classical_kernel_time, vqc_time_ft),
]:
    diff = np.abs(t1 - t2)
    cross_idx = np.argmin(diff)
    ax.axvline(N_values[cross_idx], ls=":", color="gray", alpha=0.7)
    ax.text(N_values[cross_idx] * 1.2, 1e-2, f"N≈{int(N_values[cross_idx]):,}", fontsize=9)

ax.set_xlabel("Dataset size N"); ax.set_ylabel("Relative training time (log scale)")
ax.set_title("Break-Even Analysis: When Does Quantum Become Competitive?\n"
             "Assumes quantum speedup only for fault-tolerant hardware", fontsize=12, fontweight="bold")
ax.legend(fontsize=10); ax.grid(True, which="both", alpha=0.3)

# Highlight "Quantum Winter" zone
ax.axhspan(ax.get_ylim()[0], ax.get_ylim()[1], xmin=0, xmax=0.4,
           alpha=0.05, color="red", label="Classical dominates")
ax.axhspan(ax.get_ylim()[0], ax.get_ylim()[1], xmin=0.8, xmax=1.0,
           alpha=0.05, color="green", label="Quantum may help")

plt.tight_layout()
plt.savefig("breakeven_analysis.png", dpi=120, bbox_inches="tight")
plt.show()

print("Key insight: NISQ advantage requires the quantum kernel computation to be")
print("faster than O(N × P × shots) — not yet achieved on classical datasets.")
print("Fault-tolerant advantage: possible for specific problem structures at N > 10^4.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Fair Cross-Validation

Implement 5-fold cross-validation for the VQC and compare with sklearn's `cross_val_score` for classical models. Report mean ± std accuracy.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — cross-validation comparison

from sklearn.model_selection import KFold

cv = KFold(n_splits=5, shuffle=True, random_state=42)
X_full_scaled, y_full = DATASETS["Two Moons"]
X_full_scaled = MinMaxScaler(feature_range=(0, np.pi)).fit_transform(X_full_scaled)

# Classical 5-fold CV
print("5-Fold Cross-Validation Comparison:")
print(f"{'Model':25s} {'CV Acc (mean±std)':20s}")
print("-" * 47)

for model_name, clf in classical_models.items():
    scores = cross_val_score(clf, X_full_scaled, y_full, cv=cv)
    print(f"{model_name:25s} {scores.mean():.4f} ± {scores.std():.4f}")

# VQC 5-fold CV (simplified — use same optimization)
# YOUR CODE HERE: implement VQC cross-validation
print(f"{'VQC (YOUR CODE)':25s} ???  ± ???")
print("\nNote: VQC CV is expensive — use small datasets and limited iterations.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Noise Impact on VQC

Simulate the VQC with increasing noise levels (depolarizing error) and plot how accuracy degrades:
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — noise impact analysis
try:
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    noise_levels = [0, 0.001, 0.005, 0.01, 0.05, 0.1]
    noisy_accs   = []

    X_tr, X_te, y_tr, y_te = prep_data(*DATASETS["Two Moons"])
    # Use the optimized theta from earlier (vqc results)
    # For this exercise, use a fixed pre-trained theta
    theta_fixed = np.random.uniform(0, 2*np.pi, len(theta_params))

    for noise_p in noise_levels:
        if noise_p == 0:
            noisy_sim = AerSimulator()
        else:
            nm = NoiseModel()
            nm.add_all_qubit_quantum_error(depolarizing_error(noise_p, 1), ["ry", "h"])
            nm.add_all_qubit_quantum_error(depolarizing_error(noise_p*5, 2), ["cx"])
            noisy_sim = AerSimulator(noise_model=nm)

        # YOUR CODE HERE: run VQC with noisy_sim and compute accuracy
        noisy_accs.append(0.5)  # placeholder

    plt.figure(figsize=(8, 4))
    plt.semilogx(noise_levels[1:], noisy_accs[1:], "r-o", lw=2.5, ms=8, label="VQC accuracy")
    plt.axhline(noisy_accs[0], ls="--", color="blue", label="Ideal (no noise)")
    plt.axhline(0.5, ls=":", color="gray", label="Random baseline")
    plt.xlabel("Depolarizing noise rate p"); plt.ylabel("Test Accuracy")
    plt.title("VQC Accuracy vs Noise Level"); plt.legend(); plt.grid(True, alpha=0.3)
    plt.show()

except ImportError:
    print("qiskit_aer.noise not available — install qiskit-aer for this exercise.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Write a **2-page evidence-based report** (as a Markdown cell) evaluating whether quantum ML should be adopted for a specific use case of your choice:

1. **Problem definition**: What classification/regression task?
2. **Dataset characteristics**: Size, dimensionality, any quantum-native structure?
3. **Benchmark results**: VQC vs classical (from this notebook or literature)
4. **Practical constraints**: Training time, hardware access, noise levels
5. **Recommendation**: Use quantum ML now, in 5 years, or never? Why?

Support every claim with a number from this notebook or a paper citation.
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Compile final benchmark summary

print("=== QUANTUM ML BENCHMARK SUMMARY ===\n")

print("Dataset: Two Moons (n=200, 2 features)")
print(f"{'Model':30s} {'Test Acc':>10s} {'Train Time':>12s} {'Params':>8s}")
print("-" * 65)

for m_name, clf in classical_models.items():
    r = classical_results["Two Moons"][m_name]
    print(f"{m_name:30s} {r['acc']:>10.4f} {r['time_ms']:>10.1f}ms {'—':>8s}")

r = vqc_results["Two Moons"]
print(f"{'VQC (2q, 2L, batch=30)':30s} {r['acc']:>10.4f} {r['time_ms']:>10.1f}ms {len(theta_params):>8d}")

print("\n\nYOUR RECOMMENDATION (fill this in):")
print("=" * 50)
recommendation = '''
Problem: [YOUR CHOSEN PROBLEM]
Dataset size: [N]
Classical best: [X%]
Quantum best:  [Y%]
Training time ratio: [Z] times

Recommendation: [Use/Don't use QML] because:
1. [Evidence-based reason 1]
2. [Evidence-based reason 2]
3. [Evidence-based reason 3]

Timeline: Quantum ML may become practical for this problem by [YEAR] when [CONDITION].
'''
print(recommendation)
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Schuld et al. (2022)** — "Is quantum advantage achievable with NISQ classifiers?" — arXiv:2101.07985
2. **Kübler et al. (2021)** — "Inductive supervised quantum learning" — arXiv:2104.05822
3. **Cerezo et al. (2022)** — "Challenges and Opportunities of Near-Term Quantum Computing Systems" — PNAS
4. **Bowles et al. (2024)** — "Better than classical? The case must be made more carefully" — arXiv:2403.02141
5. **Preskill (2022)** — "Quantum computing 40 years later" — arXiv:2106.10522
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DS6_benchmarking_reality_check.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
