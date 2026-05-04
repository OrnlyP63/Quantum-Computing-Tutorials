# Quantum Computing Tutorial Plan
## Using Qiskit | YouTube + Jupyter Notebook Series

---

## Vision & Mission

**Mission:** Make quantum computing approachable, practical, and hands-on for four distinct audiences using a single unified toolkit — IBM's Qiskit — delivered through YouTube videos and Jupyter Notebooks.

**Philosophy:** Every learner, regardless of background, deserves a clear on-ramp into quantum computing. We meet each audience where they are, speak their language, and give them something they can *do* — not just watch.

---

## The Four Audience Tracks

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│  🎓 Student  │ 💻 Developer │ 📊 Data Sci  │ ⚙️ Engineer  │
│              │              │              │              │
│ Intuition    │ Code-first   │ ML Bridge    │ Hardware     │
│ & Concepts   │ Workflows    │ & QML        │ & Systems    │
│              │              │              │              │
│ No math req. │ Python-ready │ sklearn/     │ Deep quantum │
│              │              │ numpy-ready  │ systems knowledge│
└──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## Shared Foundation Modules
> These 4 modules are watched/completed **by everyone** before entering their track.

| # | Module Title | YouTube Goal | Notebook Goal |
|---|---|---|---|
| F1 | **What is Quantum Computing?** | Superposition, entanglement, interference — zero jargon, pure analogy | Reflection worksheet: map quantum concepts to real-world ideas |
| F2 | **Why Qiskit?** | Tour of the Qiskit ecosystem: Terra, Aer, IBM Quantum | Install Qiskit, verify setup, run "Hello Qubit" |
| F3 | **Qubits, States & Measurement** | What a qubit is, how measurement collapses it, Bloch sphere intro | Visualize qubit states on Bloch sphere using Qiskit |
| F4 | **How to Use This Series** | How YouTube + notebooks work together, how to navigate your track | Run the environment check notebook end-to-end |

### Foundation Teaching Notes
- F1 uses **zero code** — pure storytelling and animation
- F2 is the **only setup video** — keep it short, link to a written guide
- F3 introduces the **Bloch sphere visually** before any math appears
- F4 sets **learning expectations** and prevents dropout from confusion

---

## 🎓 Track 1 — Students
**Target:** High school students, first-year undergraduates, curious beginners
**Prerequisites:** Basic algebra, curiosity
**Qiskit Features Used:** `QuantumCircuit`, `plot_bloch_vector`, `Statevector`, Qiskit Aer simulator

### Learning Outcomes
By the end of this track, students will be able to:
- Explain superposition, entanglement, and interference in plain language
- Describe what a quantum circuit is and how it differs from classical logic
- Read a simple Qiskit circuit diagram
- Run a basic quantum circuit on a simulator and interpret results

---

### Student Track Modules

#### Module S1 — Bits, Qubits & Superposition
| | Detail |
|---|---|
| **YouTube** | Classical bit vs qubit — use a coin flip analogy. Show a qubit spinning in superposition until measured. Animate the collapse. |
| **Notebook** | Students initialize qubits in `\|0⟩` and `\|1⟩`, apply an H gate, observe superposition, then measure. See probability histograms. |
| **Key Concept** | Superposition is not randomness — it is a structured state of simultaneous possibilities |
| **Analogy Used** | A coin mid-air (superposition) vs landed (measured) |
| **Duration** | ~12 min video / 20 min notebook |

#### Module S2 — Quantum Gates: The Building Blocks
| | Detail |
|---|---|
| **YouTube** | Gates as instructions that rotate qubits. Show X (flip), H (superpose), Z (phase). Compare to classical NOT gate. |
| **Notebook** | Apply X, H, Z gates one at a time. Visualize Bloch sphere before and after each gate. Fill-in-the-blank exercises. |
| **Key Concept** | Quantum gates are reversible rotations on the Bloch sphere |
| **Analogy Used** | Gates as turning a spinning top in different directions |
| **Duration** | ~15 min video / 25 min notebook |

#### Module S3 — Entanglement: Qubits That Share a Secret
| | Detail |
|---|---|
| **YouTube** | Tell the story of two entangled particles measured light-years apart. Animate the Bell state creation step by step. |
| **Notebook** | Build a Bell state using H + CNOT. Measure both qubits 1000 times. Show that results are always correlated. |
| **Key Concept** | Entanglement creates correlations that cannot be explained classically |
| **Analogy Used** | Magic dice — no matter how far apart, they always match |
| **Duration** | ~14 min video / 20 min notebook |

#### Module S4 — Your First Quantum Circuit
| | Detail |
|---|---|
| **YouTube** | Live Qiskit walkthrough from scratch. Show how to build, draw, and simulate a 2-qubit circuit with the host explaining every line. |
| **Notebook** | Guided build of a 3-step circuit. Students modify gates and observe how results change. Prediction-then-verify exercises. |
| **Key Concept** | Circuits are sequences of gates applied to qubits, read left to right |
| **Analogy Used** | A recipe — ingredients (qubits) + steps (gates) = dish (output state) |
| **Duration** | ~18 min video / 30 min notebook |

#### Module S5 — Quantum Computing in the Real World
| | Detail |
|---|---|
| **YouTube** | Three stories: (1) breaking encryption, (2) simulating molecules for medicine, (3) optimizing delivery routes. Keep each under 3 minutes. |
| **Notebook** | Conceptual exploration notebook: map application → quantum technique → real company using it today |
| **Key Concept** | Quantum advantage exists in specific problem domains — not everything |
| **Analogy Used** | A supercar on a track vs in city traffic — context determines advantage |
| **Duration** | ~15 min video / 15 min notebook |

---

## 💻 Track 2 — Developers
**Target:** Software engineers, Python developers, CS graduates
**Prerequisites:** Python proficiency, basic data structures, familiarity with APIs
**Qiskit Features Used:** `QuantumCircuit`, `transpile`, `Aer`, `IBMProvider`, `qiskit.circuit.library`, `QuantumRegister`, `ClassicalRegister`

### Learning Outcomes
By the end of this track, developers will be able to:
- Build multi-qubit quantum circuits using Qiskit's full API
- Implement foundational quantum algorithms from scratch
- Transpile and optimize circuits for real backends
- Submit jobs to IBM Quantum hardware and parse results

---

### Developer Track Modules

#### Module D1 — Quantum Computing for Python Developers
| | Detail |
|---|---|
| **YouTube** | Map classical programming concepts to quantum equivalents: variables → qubits, functions → gates, output → measurement. Live terminal setup. |
| **Notebook** | Install walkthrough, first circuit in 10 lines, draw + simulate + interpret histogram. Annotated line-by-line. |
| **Key Concept** | Quantum programming is a new paradigm, not just a library |
| **Dev Bridge** | `if/else` → measurement branching; `arrays` → quantum registers |
| **Duration** | ~16 min video / 25 min notebook |

#### Module D2 — Quantum Gates as Matrix Operations
| | Detail |
|---|---|
| **YouTube** | Show gates as 2×2 matrices. Demonstrate how H, X, CNOT work mathematically. Keep it visual with matrix-vector multiplication animations. |
| **Notebook** | Use `Operator` class in Qiskit to inspect gate matrices. Multiply gate matrices manually vs Qiskit's output. Verify results match. |
| **Key Concept** | Every gate is a unitary matrix; circuits are matrix multiplications |
| **Dev Bridge** | Unitary matrices are like pure functions — reversible, no side effects |
| **Duration** | ~18 min video / 30 min notebook |

#### Module D3 — Building Complex Circuits
| | Detail |
|---|---|
| **YouTube** | Registers, barriers, circuit composition, appending circuits. Show how to build circuits modularly like software components. |
| **Notebook** | Build a modular circuit using `QuantumRegister` and `ClassicalRegister`. Compose sub-circuits. Use barriers for readability. |
| **Key Concept** | Circuits can be composed, parameterized, and reused like functions |
| **Dev Bridge** | Sub-circuits = modules/functions; parameterized circuits = function arguments |
| **Duration** | ~20 min video / 35 min notebook |

#### Module D4 — Deutsch-Jozsa Algorithm
| | Detail |
|---|---|
| **YouTube** | Explain the oracle problem: is a function constant or balanced? Show classical worst case vs quantum 1-shot solution with animation. |
| **Notebook** | Build the Deutsch-Jozsa circuit. Implement constant and balanced oracles. Run both. Compare results and shot counts. |
| **Key Concept** | Quantum algorithms exploit interference to rule out wrong answers in bulk |
| **Dev Bridge** | Oracle = black-box function; the algorithm = a single API call that answers the question |
| **Duration** | ~20 min video / 35 min notebook |

#### Module D5 — Grover's Search Algorithm
| | Detail |
|---|---|
| **YouTube** | Searching an unsorted list: classical O(N) vs Grover's O(√N). Show amplitude amplification step by step with bar chart animation. |
| **Notebook** | Build Grover's oracle and diffuser for a 3-qubit search. Visualize amplitude before and after each iteration. Find the marked state. |
| **Key Concept** | Grover's amplifies the probability of correct answers through constructive interference |
| **Dev Bridge** | Think of it as a probabilistic binary search with guaranteed amplification |
| **Duration** | ~22 min video / 40 min notebook |

#### Module D6 — Running on Real IBM Quantum Hardware
| | Detail |
|---|---|
| **YouTube** | Tour IBM Quantum platform. Explain queue, backends, shots, and noise. Show a real job submission and result interpretation. |
| **Notebook** | Connect via `IBMProvider`. Choose a least-busy backend. Transpile a circuit. Submit, wait, retrieve, and compare results to simulator. |
| **Key Concept** | Real hardware introduces noise — results are probabilistic distributions, not perfect answers |
| **Dev Bridge** | Backend = remote API endpoint; transpilation = build optimization/minification |
| **Duration** | ~20 min video / 30 min notebook |

---

## 📊 Track 3 — Data Scientists
**Target:** ML practitioners, data analysts, researchers with Python/numpy/sklearn experience
**Prerequisites:** numpy, pandas, sklearn basics, familiarity with optimization
**Qiskit Features Used:** `qiskit_machine_learning`, `QNNCircuit`, `SamplerQNN`, `EstimatorQNN`, `VQC`, `ZZFeatureMap`, `RealAmplitudes`, `FidelityQuantumKernel`

### Learning Outcomes
By the end of this track, data scientists will be able to:
- Encode classical data into quantum circuits
- Build and train Variational Quantum Circuits (VQC)
- Use quantum kernels for classical ML tasks
- Understand where quantum ML may provide advantage

---

### Data Scientist Track Modules

#### Module DS1 — Quantum vs Classical ML: The Big Picture
| | Detail |
|---|---|
| **YouTube** | Side-by-side: classical neural net vs variational quantum circuit. Explain parameterized circuits as the quantum analog of neural nets. |
| **Notebook** | Conceptual comparison table. Load a classical dataset. Establish a classical sklearn baseline that quantum results will later be compared to. |
| **Key Concept** | Quantum ML is not replacing classical ML — it is exploring new hypothesis spaces |
| **DS Bridge** | VQC ≈ shallow neural net with quantum feature transformation |
| **Duration** | ~16 min video / 20 min notebook |

#### Module DS2 — Encoding Classical Data into Quantum Circuits
| | Detail |
|---|---|
| **YouTube** | The fundamental challenge: quantum computers need quantum input. Explain angle encoding, amplitude encoding, and basis encoding with visuals. |
| **Notebook** | Encode a small classical dataset three ways using Qiskit's `ZZFeatureMap` and custom circuits. Visualize how data maps to qubit states. |
| **Key Concept** | Data encoding is the most critical and least solved part of quantum ML |
| **DS Bridge** | Feature maps in quantum ML = feature engineering / preprocessing pipelines |
| **Duration** | ~18 min video / 30 min notebook |

#### Module DS3 — Variational Quantum Circuits (VQC)
| | Detail |
|---|---|
| **YouTube** | What makes a circuit variational? Show ansatz, parameters, and the training loop. Animate gradient descent updating gate angles. |
| **Notebook** | Build a VQC using `RealAmplitudes` ansatz. Define a cost function. Train using a classical optimizer. Plot loss curve. |
| **Key Concept** | VQCs are trained by optimizing gate rotation angles using classical optimizers |
| **DS Bridge** | Ansatz = model architecture; rotation angles = model weights; optimizer = Adam/SGD |
| **Duration** | ~20 min video / 40 min notebook |

#### Module DS4 — Quantum Neural Networks with Qiskit
| | Detail |
|---|---|
| **YouTube** | Deep dive into `SamplerQNN` and `EstimatorQNN`. How they compute gradients (parameter shift rule). When to use each. |
| **Notebook** | Build a `SamplerQNN` for binary classification. Connect to a PyTorch training loop using `TorchConnector`. Train and evaluate. |
| **Key Concept** | The parameter shift rule is the quantum analog of backpropagation |
| **DS Bridge** | `TorchConnector` lets you drop a QNN into any PyTorch model like a custom layer |
| **Duration** | ~22 min video / 45 min notebook |

#### Module DS5 — Quantum Kernels for Classification
| | Detail |
|---|---|
| **YouTube** | Explain kernel methods (SVM recap). Show how a quantum feature map creates a kernel matrix in exponentially large Hilbert space. |
| **Notebook** | Use `FidelityQuantumKernel` + `ZZFeatureMap`. Plug into sklearn's `SVC`. Compare accuracy vs classical RBF kernel on same dataset. |
| **Key Concept** | Quantum kernels compute inner products in spaces classical computers cannot efficiently access |
| **DS Bridge** | Drop-in replacement for RBF/polynomial kernels in sklearn's SVM pipeline |
| **Duration** | ~20 min video / 35 min notebook |

#### Module DS6 — Quantum Advantage: Benchmarking & Reality Check
| | Detail |
|---|---|
| **YouTube** | Honest conversation: where quantum ML helps today, where it doesn't. Discuss barren plateaus, noise, and the scaling problem. |
| **Notebook** | Benchmark VQC vs classical model on dataset size vs accuracy vs training time. Visualize trade-offs. Identify break-even points. |
| **Key Concept** | Current quantum ML advantage is theoretical — practical advantage requires fault-tolerant hardware |
| **DS Bridge** | Like comparing GPU vs CPU — hardware maturity determines real-world usefulness |
| **Duration** | ~18 min video / 30 min notebook |

---

## ⚙️ Track 4 — Engineers
**Target:** Electrical engineers, systems engineers, quantum hardware researchers
**Prerequisites:** Linear algebra, signals, Python, some physics background
**Qiskit Features Used:** `qiskit.pulse`, `transpile`, `InstructionScheduleMap`, noise models in `qiskit_aer.noise`, `FakeManhattan`, error mitigation via `qiskit_ibm_runtime`

### Learning Outcomes
By the end of this track, engineers will be able to:
- Understand quantum hardware architectures and their trade-offs
- Characterize noise using Qiskit tools
- Program at the pulse level using Qiskit Pulse
- Apply error mitigation and understand error correction concepts

---

### Engineer Track Modules

#### Module E1 — Quantum Hardware Architectures
| | Detail |
|---|---|
| **YouTube** | Survey superconducting qubits (IBM), trapped ions, and photonic systems. Deep dive into IBM's superconducting transmon architecture. |
| **Notebook** | Use Qiskit to query real backend properties: coupling map, qubit connectivity, native gate set, T1/T2 times. Visualize the coupling map. |
| **Key Concept** | Hardware architecture determines what gates are native, what errors dominate, and how circuits must be mapped |
| **Eng Bridge** | Coupling map = PCB trace routing; native gates = instruction set architecture (ISA) |
| **Duration** | ~22 min video / 30 min notebook |

#### Module E2 — Noise, Decoherence & Error Characterization
| | Detail |
|---|---|
| **YouTube** | T1 (energy relaxation) and T2 (dephasing) explained with signal decay analogies. Gate error rates, readout error. Noise channel taxonomy. |
| **Notebook** | Build a noise model using `qiskit_aer.noise`. Simulate a circuit with depolarizing noise, bit-flip, and phase-flip channels. Compare noisy vs ideal results. |
| **Key Concept** | Decoherence is the primary engineering challenge — circuits must complete before information decays |
| **Eng Bridge** | T1/T2 = RC time constants; decoherence = signal attenuation in analog circuits |
| **Duration** | ~24 min video / 40 min notebook |

#### Module E3 — Transpilation & Circuit Optimization
| | Detail |
|---|---|
| **YouTube** | What is transpilation? Routing, decomposition, optimization passes. Show how the same circuit looks different on different backends. |
| **Notebook** | Transpile a circuit at optimization levels 0–3. Compare gate count, circuit depth, and CNOT count at each level. Visualize coupling map routing. |
| **Key Concept** | Transpilation maps abstract circuits to hardware-executable form while minimizing depth and error |
| **Eng Bridge** | Transpilation = compiler optimization pipeline; routing = register allocation |
| **Duration** | ~22 min video / 35 min notebook |

#### Module E4 — Pulse-Level Programming with Qiskit Pulse
| | Detail |
|---|---|
| **YouTube** | Go below the gate level. Explain microwave pulses that drive superconducting qubits. Show a gate as a shaped microwave pulse. |
| **Notebook** | Use `qiskit.pulse` to schedule a custom drive pulse. Compare to default gate implementation. Build a simple pulse schedule for an X gate. |
| **Key Concept** | Gates are hardware abstractions — underneath are precisely timed analog microwave pulses |
| **Eng Bridge** | Pulse programming = bare-metal / assembly level vs gate level = high-level language |
| **Duration** | ~25 min video / 45 min notebook |

#### Module E5 — Error Mitigation Techniques
| | Detail |
|---|---|
| **YouTube** | Difference between error mitigation (software) and error correction (hardware). Explain Zero Noise Extrapolation (ZNE) and measurement error mitigation. |
| **Notebook** | Apply `qiskit_ibm_runtime` error mitigation options. Compare raw results, measurement-mitigated, and ZNE-mitigated results for the same circuit. |
| **Key Concept** | Error mitigation improves results statistically without requiring logical qubits |
| **Eng Bridge** | ZNE = extrapolation-based calibration; similar to noise floor subtraction in signal processing |
| **Duration** | ~22 min video / 40 min notebook |

#### Module E6 — Quantum Error Correction Concepts
| | Detail |
|---|---|
| **YouTube** | Why we need logical qubits. Explain the 3-qubit bit-flip code and surface code concept. Show the overhead cost honestly. |
| **Notebook** | Simulate the 3-qubit repetition code in Qiskit. Introduce an error manually. Run syndrome measurement. Demonstrate correction. |
| **Key Concept** | Fault-tolerant quantum computing requires encoding 1 logical qubit in many physical qubits |
| **Eng Bridge** | Repetition code = RAID parity; surface code = 2D parity check matrix |
| **Duration** | ~25 min video / 45 min notebook |

---

## YouTube Episode Blueprint

Every episode across all tracks follows this consistent structure:

```
╔══════════════════════════════════════════════════════════╗
║  0:00 │ HOOK (45 sec)                                    ║
║       │ Provocative question or surprising demo          ║
╠══════════════════════════════════════════════════════════╣
║  0:45 │ RECAP (1 min)                                    ║
║       │ 3 bullets from last episode                      ║
╠══════════════════════════════════════════════════════════╣
║  1:45 │ CONCEPT EXPLANATION (6–8 min)                    ║
║       │ Analogy → Intuition → Formal Definition          ║
║       │ Animated visuals, Bloch sphere, circuit diagrams ║
╠══════════════════════════════════════════════════════════╣
║  9:00 │ QISKIT LIVE DEMO (6–8 min)                       ║
║       │ Screen-recorded, narrated, mirrors the notebook  ║
╠══════════════════════════════════════════════════════════╣
║ 16:00 │ RESULTS INTERPRETATION (2 min)                   ║
║       │ What do the outputs mean? What surprises you?    ║
╠══════════════════════════════════════════════════════════╣
║ 18:00 │ KEY TAKEAWAYS (1 min)                            ║
║       │ Exactly 3 bullet points, shown on screen         ║
╠══════════════════════════════════════════════════════════╣
║ 19:00 │ NOTEBOOK CHALLENGE PREVIEW (1 min)               ║
║       │ Show the exercise — don't solve it               ║
╚══════════════════════════════════════════════════════════╝
```

---

## Jupyter Notebook Blueprint

Every notebook follows this consistent 7-section layout:

```
╔══════════════════════════════════════════════════════════╗
║  📌 HEADER CELL (Markdown)                               ║
║  Track | Module | Title | Difficulty ⭐⭐⭐              ║
║  Prerequisites | Estimated Time | Qiskit Modules Used    ║
╠══════════════════════════════════════════════════════════╣
║  🎯 LEARNING OBJECTIVES (Markdown)                       ║
║  3–5 measurable "you will be able to..." statements      ║
╠══════════════════════════════════════════════════════════╣
║  📖 CONCEPT SUMMARY (Markdown)                           ║
║  3–5 paragraphs max. Not a repeat of the video.          ║
║  Focuses on what you need to know to run the code.       ║
╠══════════════════════════════════════════════════════════╣
║  💻 GUIDED CODE CELLS (Code + Markdown interleaved)      ║
║  Every cell has a purpose comment.                       ║
║  Outputs are described before they appear.               ║
╠══════════════════════════════════════════════════════════╣
║  🧪 EXERCISES (Code cells with blanks)                   ║
║  # YOUR CODE HERE                                        ║
║  Expected output shown so students can self-check.       ║
╠══════════════════════════════════════════════════════════╣
║  🏆 CHALLENGE (Optional)                                 ║
║  One open-ended harder problem. No solution provided.    ║
╠══════════════════════════════════════════════════════════╣
║  📚 FURTHER READING (Markdown)                           ║
║  3–5 links: Qiskit docs, IBM research papers, textbooks  ║
╚══════════════════════════════════════════════════════════╝
```

---

## Full Content Map

```
FOUNDATION (Everyone)
│
├── F1: What is Quantum Computing?
├── F2: Why Qiskit?
├── F3: Qubits, States & Measurement
└── F4: How to Use This Series
         │
         ├──────────────────────────────────────────────────┐
         │                    │                │            │
   🎓 STUDENT          💻 DEVELOPER     📊 DATA SCI   ⚙️ ENGINEER
   │                    │                │            │
   S1 Superposition     D1 Dev Intro     DS1 QML Intro    E1 Hardware
   S2 Gates             D2 Gate Matrices DS2 Encoding     E2 Noise
   S3 Entanglement      D3 Complex       DS3 VQC          E3 Transpile
   S4 First Circuit        Circuits      DS4 QNN          E4 Pulse
   S5 Applications      D4 Deutsch-Jozsa DS5 Kernels      E5 Mitigation
                        D5 Grover's      DS6 Benchmarking E6 Error Correction
                        D6 Real Hardware
```

---

## Rollout Timeline (16 Weeks)

| Week | Milestone |
|---|---|
| **1** | Finalize scripts for F1–F4. Record Foundation modules. |
| **2** | Edit and publish F1–F4 on YouTube. Release notebooks. |
| **3–4** | Record, edit, publish Student Track S1–S5 + notebooks |
| **5–6** | Record, edit, publish Developer Track D1–D3 + notebooks |
| **7–8** | Record, edit, publish Developer Track D4–D6 + notebooks |
| **9–10** | Record, edit, publish Data Scientist Track DS1–DS3 + notebooks |
| **11–12** | Record, edit, publish Data Scientist Track DS4–DS6 + notebooks |
| **13–14** | Record, edit, publish Engineer Track E1–E3 + notebooks |
| **15–16** | Record, edit, publish Engineer Track E4–E6 + notebooks |
| **Bonus** | Capstone projects per track + community Q&A livestream |

---

## Qiskit Module Reference by Track

| Qiskit Module | Student | Developer | Data Sci | Engineer |
|---|:---:|:---:|:---:|:---:|
| `qiskit.circuit` | ✅ | ✅ | ✅ | ✅ |
| `qiskit_aer` (Simulator) | ✅ | ✅ | ✅ | ✅ |
| `qiskit.visualization` | ✅ | ✅ | ✅ | ✅ |
| `qiskit.quantum_info` | | ✅ | ✅ | ✅ |
| `qiskit.circuit.library` | | ✅ | ✅ | ✅ |
| `qiskit_ibm_runtime` | | ✅ | | ✅ |
| `qiskit_machine_learning` | | | ✅ | |
| `qiskit.pulse` | | | | ✅ |
| `qiskit_aer.noise` | | | | ✅ |

---

## Pedagogical Principles

| Principle | How It's Applied |
|---|---|
| **Analogy First** | Every concept begins with a physical or everyday analogy before any code or math |
| **One Concept Per Video** | No episode covers more than one major idea — depth over breadth |
| **Predict → Run → Explain** | Students predict output before running code, then explain the difference |
| **Consistent Vocabulary** | A shared glossary PDF is released with the series and linked in every notebook |
| **Track Independence** | Each track is self-contained — no track requires watching another |
| **Honest Limitations** | Every track includes at least one "what quantum can't do yet" moment |

---

## Success Metrics

| Metric | Target |
|---|---|
| YouTube watch-through past 5 min | > 65% |
| Notebook exercise completion (via form) | > 50% of viewers |
| Student track: can explain Bell state | 80% of respondents in survey |
| Developer track: can submit a real job | 70% of respondents |
| Data scientist track: VQC trains without error | 75% of respondents |
| Engineer track: can read a noise model output | 70% of respondents |