---
name: boltz
description: >
  Structure prediction using Boltz-1/Boltz-2, an open biomolecular structure predictor.
  Use this skill when: (1) Predicting protein complex structures,
  (2) Validating designed binders,
  (3) Need open-source alternative to AF2,
  (4) Predicting protein-ligand complexes,
  (5) Using local GPU resources.

  For QC thresholds, use protein-qc.
  For AlphaFold2 prediction, use alphafold.
  For Chai prediction, use chai.
license: MIT
category: design-tools
tags: [structure-prediction, validation, open-source]
source: https://github.com/adaptyvbio/protein-design-skills
---

# Boltz Structure Prediction

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.10+ | 3.11 |
| CUDA | 12.0+ | 12.1+ |
| GPU VRAM | 24GB | 48GB (L40S) |
| RAM | 32GB | 64GB |

## How to run

### Option 1: Modal
```bash
cd biomodals
modal run modal_boltz.py \
  --input-faa complex.fasta \
  --out-dir predictions/
```

### Option 2: Local
```bash
pip install boltz
boltz predict --fasta complex.fasta --output predictions/
```

## Output format

```
predictions/
├── model_0.cif       # Best model (CIF format)
├── confidence.json   # pLDDT, pTM, ipTM
└── pae.npy
```

## Comparison

| Feature | Boltz-1 | Boltz-2 | AF2-Multimer |
|---------|---------|---------|--------------|
| MSA-free | Yes | Yes | No |
| Open source | Yes | Yes | Yes |
| Speed | Fast | 2x faster | Slower |

## Typical performance

| Campaign | Time (L40S) | Cost (Modal) |
|----------|-------------|--------------|
| 100 complexes | 30-45 min | ~$8 |
| 500 complexes | 2-3h | ~$35 |

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `CUDA out of memory` | Complex too large | Use `--use_msa_server false` |
| `KeyError: 'iptm'` | Single chain | Ensure 2+ chains in FASTA |
| `FileNotFoundError: weights` | Missing model | Run `boltz download` first |

**Next**: `protein-qc` for filtering and ranking.
