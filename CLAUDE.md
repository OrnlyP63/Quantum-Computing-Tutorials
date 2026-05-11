# CLAUDE.md — Quantum Computing Tutorial Series

## Project Overview

YouTube tutorial series + Jupyter Notebook course on quantum computing using Qiskit.
Brand: **วิศวกร สอน AI** (Engineer Teaches AI).
27 modules across 5 tracks: Foundation, Student, Developer, Data Scientist, Engineer.

---

## Completed Tasks

### 1. Generate Notebooks — 27 `generate_nb.py` scripts + `.ipynb` outputs

Each module in `modules/<track>/<id>/` has:
- `generate_nb.py` — builds the notebook programmatically via `nbformat`
- `<id>_<title>.ipynb` — generated output (do not edit by hand)

**Tracks and modules written:**

| Track | Modules |
|-------|---------|
| Foundation | F1, F2, F3, F4 |
| Student | S1, S2, S3, S4, S5 |
| Developer | D1, D2, D3, D4, D5, D6 |
| Data Scientist | DS1, DS2, DS3, DS4, DS5, DS6 |
| Engineer | E1, E2, E3, E4, E5, E6 |

**Regenerate all notebooks:**
```bash
find modules -name "generate_nb.py" | sort | while read f; do
  (cd "$(dirname "$f")" && python generate_nb.py)
done
```

**Regenerate single module:**
```bash
cd modules/engineer/E6 && python generate_nb.py
```

**Known issues fixed during generation:**
- Inner `"""` inside `r"""..."""` code cells closed string prematurely → replaced inner `"""` with `'''`
- E2–E6 output path was absolute-relative (`modules/engineer/E2/...`) → stripped to filename only (scripts run from their own directory)
- DS6 used `×` (U+00D7) in Python code → replaced with `times`
- D1 had `"""` in markdown cell code fence → replaced with `'''`

---

### 2. README.md

Written at project root. Covers:
- Project overview and philosophy
- Repo structure
- Getting started (pip install, generate commands, launch Jupyter)
- Four-track module tables with titles and key concepts
- 7-section notebook structure
- Technical stack table (Qiskit 1.x, AerSimulator, qiskit-machine-learning, etc.)
- ASCII curriculum map
- Regeneration instructions
- MIT license

---

### 3. YouTube Cover Thumbnails — `generate_covers.py`

Generates 27 PNG thumbnails (1280×720) to `covers/`.

**Run:**
```bash
python3 generate_covers.py
```

**Design system:**
- Dark navy gradient background (`#080C1C` → `#12193A`)
- Circuit-board decoration on right half (seeded per module for variety)
- Per-track color coding:
  - Foundation: gold `(245, 166, 35)`
  - Student: green `(39, 174, 96)`
  - Developer: blue `(41, 128, 185)`
  - Data Scientist: orange `(230, 126, 34)`
  - Engineer: red `(192, 57, 43)`
- `logo.png` composited top-left (white pixels made transparent)
- Module badge top-right (bold, track color)
- Track pill (rounded rect) below logo
- English title: bold white, 80pt HelveticaNeue
- Thai hook: track color, 42pt Ayuthaya
- Accent bar at bottom (6px, track color)

**Fonts used:**
- `/System/Library/Fonts/HelveticaNeue.ttc` index=1 (bold)
- `/System/Library/Fonts/Supplemental/Ayuthaya.ttf` (Thai)

**Output:** `covers/F1_cover.png` … `covers/E6_cover.png`

---

## Tech Stack

| Component | Choice |
|-----------|--------|
| Quantum SDK | Qiskit 1.x |
| Simulator | `qiskit-aer` (AerSimulator) |
| QML | `qiskit-machine-learning` |
| Hardware access | `qiskit-ibm-runtime` |
| Notebook generation | `nbformat` v4 |
| Thumbnail generation | `Pillow` (PIL) |
| Python | 3.12+ |

## Key API Patterns (Qiskit 1.x)

```python
from qiskit_aer import AerSimulator
from qiskit import transpile

sim = AerSimulator()
tqc = transpile(qc, sim)
job = sim.run(tqc, shots=1024)
counts = job.result().get_counts()
```

Always `transpile()` before `sim.run()` — Qiskit 1.x removed direct `execute()`.
