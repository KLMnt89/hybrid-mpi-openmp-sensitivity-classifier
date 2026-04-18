# Hybrid MPI-OpenMP Framework for Parallel File Sensitivity Classification and Disaster Recovery Prioritization

A high-performance parallel computing framework that classifies files by sensitivity level and prioritizes them for disaster recovery using a hybrid **MPI + OpenMP** architecture simulated in Python.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Classification Pipeline](#classification-pipeline)
- [Disaster Recovery Prioritization](#disaster-recovery-prioritization)
- [Parallelization Strategies](#parallelization-strategies)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Dataset](#dataset)
- [Results](#results)

---

## Overview

This project implements a research framework for parallel file sensitivity classification using a hybrid MPI + OpenMP approach. It benchmarks four execution strategies — sequential, MPI-only, OpenMP-only, and hybrid — and ranks classified files for disaster recovery prioritization.

**Key formulas:**

| Formula | Description |
|--------|-------------|
| `S = max(S_rule, α·S_content + β·S_metadata + γ·S_entropy)` | Sensitivity classification score |
| `P = w_s·S_norm + w_c·C + w_r·R` | Disaster recovery priority score |

**Sensitivity levels:** `PUBLIC` → `INTERNAL` → `CONFIDENTIAL` → `SECRET`

---

## Architecture

```
run_benchmark.py
│
├── experiments/
│   ├── sequential_baseline.py     # Single-threaded baseline
│   ├── mpi_only.py                # MPI distributed processes
│   ├── openmp_only.py             # OpenMP thread-level parallelism
│   └── hybrid_mpi_openmp.py       # MPI processes + OpenMP threads
│
└── src/
    ├── classification/
    │   ├── pipeline.py            # 4-stage classification orchestrator
    │   ├── rule_based.py          # Rule-based detector  (S_rule)
    │   ├── content_analysis.py    # Content scoring      (S_content)
    │   ├── metadata_scoring.py    # Metadata scoring     (S_metadata)
    │   └── entropy_calc.py        # Shannon entropy      (S_entropy)
    ├── parallel/
    │   ├── mpi_master.py          # MPI master — distributes work
    │   ├── mpi_worker.py          # MPI workers — process file chunks
    │   ├── mpi_coordinator.py     # Work partitioning logic
    │   └── openmp_simulator.py    # Thread-level parallelism (ThreadPoolExecutor)
    ├── prioritization/
    │   └── priority_ranker.py     # Disaster recovery ranking
    └── utils/
        ├── dataset_generator.py   # Synthetic dataset generator
        ├── data_structures.py     # FileMetadata, ClassificationResult, SensitivityLevel
        └── metrics.py             # Speedup, efficiency, accuracy
```

---

## Classification Pipeline

The pipeline applies 4 stages in sequence, then fuses the scores:

```
File Input
    │
    ▼
1. Rule-Based Detection  ──────────────────────────────► S_rule
    │  (keyword/pattern matching for known sensitive markers)
    │
    ▼
2. Content Analysis  ─────────────────────────────────► S_content  (α = 0.4)
    │  (TF-IDF style scoring on file content)
    │
    ▼
3. Metadata Scoring  ─────────────────────────────────► S_metadata (β = 0.35)
    │  (file permissions, ownership, path depth)
    │
    ▼
4. Entropy Calculation  ──────────────────────────────► S_entropy  (γ = 0.25)
    │  (Shannon entropy — detects encrypted/compressed content)
    │
    ▼
Score Fusion: S = max(S_rule, α·S_content + β·S_metadata + γ·S_entropy)
    │
    ▼
Sensitivity Level: PUBLIC / INTERNAL / CONFIDENTIAL / SECRET
```

---

## Disaster Recovery Prioritization

After classification, files are ranked for disaster recovery using:

```
P = w_s · S_norm + w_c · C + w_r · R
```

| Weight | Factor | Default | Description |
|--------|--------|---------|-------------|
| `w_s` | Sensitivity | 0.45 | Normalized sensitivity score |
| `w_c` | Criticality | 0.35 | Business criticality (file type, directory depth) |
| `w_r` | Recency | 0.20 | Recently modified files get higher priority |

Files with higher `P` scores are recovered first in disaster scenarios.

---

## Parallelization Strategies

| Mode | Description | Python Implementation |
|------|-------------|----------------------|
| **Sequential** | Baseline single-threaded processing | Plain `for` loop |
| **MPI-only** | Distributes files across N processes | `mpi4py` — master/worker pattern |
| **OpenMP-only** | Parallel threads per node | `concurrent.futures.ThreadPoolExecutor` |
| **Hybrid** | MPI processes × OpenMP threads | `mpi4py` + `ThreadPoolExecutor` combined |

The hybrid mode uses `classify_with_threading()` per MPI worker, achieving the best throughput for large file sets.

---

## Project Structure

```
hybrid-mpi-openmp-sensitivity-classifier/
├── experiments/
│   ├── __init__.py
│   ├── sequential_baseline.py
│   ├── mpi_only.py
│   ├── openmp_only.py
│   └── hybrid_mpi_openmp.py
├── src/
│   ├── classification/
│   │   ├── __init__.py
│   │   ├── pipeline.py
│   │   ├── rule_based.py
│   │   ├── content_analysis.py
│   │   ├── metadata_scoring.py
│   │   └── entropy_calc.py
│   ├── parallel/
│   │   ├── __init__.py
│   │   ├── mpi_master.py
│   │   ├── mpi_worker.py
│   │   ├── mpi_coordinator.py
│   │   └── openmp_simulator.py
│   ├── prioritization/
│   │   ├── __init__.py
│   │   └── priority_ranker.py
│   └── utils/
│       ├── __init__.py
│       ├── dataset_generator.py
│       ├── data_structures.py
│       └── metrics.py
├── datasets/               # excluded from Git — add locally
├── results/                # auto-generated benchmark output
├── real_file_loader.py
├── run_benchmark.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Requirements

- Python 3.8+
- MPI implementation:
  - **Windows:** [Microsoft MPI](https://learn.microsoft.com/en-us/message-passing-interface/microsoft-mpi)
  - **Linux/macOS:** OpenMPI (`sudo apt install openmpi-bin` / `brew install open-mpi`)

---

## Installation

```bash
git clone https://github.com/KLMnt89/hybrid-mpi-openmp-sensitivity-classifier.git
cd hybrid-mpi-openmp-sensitivity-classifier
pip install -r requirements.txt
```

---

## Usage

```bash
# Sequential baseline
python run_benchmark.py --mode sequential --files 500

# MPI only (4 processes)
mpiexec -n 4 python run_benchmark.py --mode mpi --files 500

# OpenMP only
python run_benchmark.py --mode openmp --files 500

# Hybrid MPI + OpenMP (4 processes × 4 threads)
mpiexec -n 4 python run_benchmark.py --mode hybrid --files 500
```

---

## Dataset

Synthetic datasets generated by `src/utils/dataset_generator.py` simulate:

| Dataset | Description |
|---------|-------------|
| GovDocs1 (simulated) | Government documents — PDF, DOC, TXT, HTML |
| Enron Email (simulated) | Email communications with varying sensitivity |

> **Optional real datasets:**
> - GovDocs1: https://digitalcorpora.org/corpora/files → `datasets/govdocs_sample/`
> - Enron Email: https://www.cs.cmu.edu/~enron/ → `datasets/enron_sample/`

---

## Results

Benchmark across file counts (100 / 500 / 1000 / 5000 files), 4 MPI processes × 4 threads:

| Mode | Speedup | Efficiency |
|------|---------|------------|
| Sequential | 1.0× | 100% |
| MPI only | ~3.2× | ~80% |
| OpenMP only | ~2.1× | ~53% |
| **Hybrid** | **~5.8×** | **~73%** |

Results and plots are saved to `results/` after each benchmark run.

---

## License

MIT
