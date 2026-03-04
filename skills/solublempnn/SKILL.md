---
name: solublempnn
description: >
  Solubility-optimized protein sequence design using SolubleMPNN.
  Use this skill when: (1) Designing for E. coli expression,
  (2) Optimizing solubility of designed proteins,
  (3) Reducing aggregation propensity,
  (4) Need high-yield expression,
  (5) Avoiding inclusion body formation.

  For standard design, use proteinmpnn.
  For ligand-aware design, use ligandmpnn.
license: MIT
category: design-tools
tags: [sequence-design, inverse-folding, solubility]
source: https://github.com/adaptyvbio/protein-design-skills
---

# SolubleMPNN Solubility-Optimized Design

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.10 |
| GPU VRAM | 8GB | 16GB (T4) |

## How to run

```bash
cd biomodals
modal run modal_proteinmpnn.py \
  --pdb-path backbone.pdb \
  --num-seq-per-target 16 \
  --sampling-temp 0.1 \
  --model-name v_48_020
```

## Model Variants

| Model | Description | Use Case |
|-------|-------------|----------|
| v_48_002 | Standard | General design |
| v_48_020 | Soluble-trained | E. coli expression |
| v_48_030 | High solubility | Difficult targets |

## Decision tree

```
When to use SolubleMPNN?
├─ E. coli expression → SolubleMPNN ✓
├─ History of aggregation → SolubleMPNN ✓
├─ History of low yield → SolubleMPNN ✓
├─ Ligand in binding site → LigandMPNN
└─ No expression issues → ProteinMPNN is fine
```

**Expected improvement**: +15-30% solubility score vs standard ProteinMPNN.

**Next**: Structure prediction → `protein-qc` for filtering.
