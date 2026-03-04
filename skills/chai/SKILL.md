---
name: chai
description: >
  Structure prediction using Chai-1, a foundation model for molecular structure.
  Use this skill when: (1) Predicting protein-protein complex structures,
  (2) Validating designed binders,
  (3) Predicting protein-ligand complexes,
  (4) Using the Chai API for high-throughput prediction,
  (5) Need an alternative to AlphaFold2.

  For QC thresholds, use protein-qc.
  For AlphaFold2 prediction, use alphafold.
  For ESM-based analysis, use esm.
license: MIT
category: design-tools
tags: [structure-prediction, validation, foundation-model]
source: https://github.com/adaptyvbio/protein-design-skills
---

# Chai-1 Structure Prediction

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.10+ | 3.11 |
| CUDA | 12.0+ | 12.1+ |
| GPU VRAM | 24GB | 40GB (A100) |
| RAM | 32GB | 64GB |

## How to run

### Option 1: Modal
```bash
cd biomodals
modal run modal_chai1.py \
  --input-faa complex.fasta \
  --out-dir predictions/
```

### Option 2: Chai API (recommended)
```bash
pip install chai_lab
python -c "
from chai_lab.chai1 import run_inference
run_inference(fasta_file='complex.fasta', output_dir='predictions/', num_trunk_recycles=3)
"
```

## FASTA Format

```
>binder
MKTAYIAKQRQISFVKSHFSRQLE...
>target
MVLSPADKTNVKAAWGKVGAHAGE...
```

### Protein + ligand
```
>protein
MKTAYIAKQRQISFVKSHFSRQLE...
>ligand|smiles
CCO
```

## Key parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `num_trunk_recycles` | 3 | Recycles (more = better) |
| `num_diffn_timesteps` | 200 | Diffusion steps |

## Output format

```
predictions/
├── pred.model_idx_0.cif    # Best model
├── scores.json             # pTM, ipTM, ranking_score
├── pae.npy                 # PAE matrix
└── plddt.npy               # pLDDT values
```

## Chai vs AF2

| Aspect | Chai-1 | AlphaFold2 |
|--------|--------|------------|
| MSA required | No | Yes |
| Small molecules | Yes | No |
| Speed | Faster | Slower |
| Accuracy | Comparable | Reference |

## Typical performance

| Campaign | Time (A100) | Cost (Modal) |
|----------|-------------|--------------|
| 100 complexes | 30-60 min | ~$10 |
| 500 complexes | 2-4h | ~$45 |

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `CUDA out of memory` | Complex too large | Use A100-80GB |
| `KeyError: 'iptm'` | Single chain | Ensure FASTA has 2+ chains |
| `ValueError: invalid SMILES` | Malformed ligand | Validate SMILES with RDKit |

**Next**: `protein-qc` for filtering and ranking.
