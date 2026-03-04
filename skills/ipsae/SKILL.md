---
name: ipsae
description: >
  Binder design ranking using ipSAE (interprotein Score from Aligned Errors).
  Use this skill when: (1) Ranking binder designs for experimental testing,
  (2) Filtering BindCraft or BoltzGen outputs,
  (3) Comparing AF2/AF3/Boltz predictions,
  (4) Predicting binding success rates,
  (5) Need better ranking than ipTM or iPAE.

  For structure prediction, use chai or alphafold.
  For QC thresholds, use protein-qc.
license: MIT
category: evaluation
tags: [ranking, scoring, binding]
source: https://github.com/adaptyvbio/protein-design-skills
---

# ipSAE Binder Ranking

## Overview

ipSAE outperforms ipTM and iPAE for binder design ranking with **1.4x higher precision**.

**Paper**: [What's wrong with AlphaFold's ipTM score](https://www.biorxiv.org/content/10.1101/2025.02.10.637595v2)

## Installation
```bash
git clone https://github.com/DunbrackLab/IPSAE.git
cd IPSAE && pip install numpy
```

## How to run

### AlphaFold2
```bash
python ipsae.py scores_rank_001.json unrelaxed_rank_001.pdb 15 15
```

### AlphaFold3
```bash
python ipsae.py fold_model_full_data_0.json fold_model_0.cif 10 10
```

### Boltz1
```bash
python ipsae.py pae_model_0.npz model_0.cif 10 10
```

## Key parameters

| Parameter | Recommended | Description |
|-----------|-------------|-------------|
| PAE cutoff | 10-15 | Threshold for contacts |
| Distance cutoff | 10-15 | Max CA-CA distance (Å) |

## Output format

**Chain-pair scores** (`_chains.csv`):
```
chain_A,chain_B,ipSAE_min,pDockQ,LIS,n_contacts
A,B,0.72,0.65,0.45,42
```

## Recommended thresholds

| Metric | Standard | Stringent |
|--------|----------|-----------|
| ipSAE_min | > 0.61 | > 0.70 |
| LIS | > 0.35 | > 0.45 |
| pDockQ | > 0.5 | > 0.6 |

## Decision tree

```
Should I use ipSAE?
├─ Designed binders → ipSAE ✓ (1.4x better than ipTM)
├─ Natural complexes → ipTM is fine
├─ Different length constructs → ipSAE ✓
└─ Single proteins → Not applicable
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `KeyError: 'pae'` | Wrong PAE format | Check if AF2/AF3/Boltz format |
| `ValueError: no contacts` | No interface | Check chain IDs, reduce cutoffs |

**Next**: Select top designs (ipSAE_min > 0.61) → experimental validation.
