---
name: protein-qc
description: >
  Quality control metrics and filtering thresholds for protein design.
  Use this skill when: (1) Evaluating design quality for binding, expression, or structure,
  (2) Setting filtering thresholds for pLDDT, ipTM, PAE,
  (3) Checking sequence liabilities (cysteines, deamidation, polybasic clusters),
  (4) Creating multi-stage filtering pipelines,
  (5) Computing PyRosetta interface metrics (dG, SC, dSASA),
  (6) Checking biophysical properties (instability, GRAVY, pI),
  (7) Ranking designs with composite scoring.
license: MIT
category: evaluation
tags: [qc, filtering, metrics, thresholds]
source: https://github.com/adaptyvbio/protein-design-skills
---

# Protein Design Quality Control

## Critical Limitation

**Individual metrics have weak predictive power for binding**:
- Individual metric ROC AUC: 0.64-0.66 (slightly better than random)
- Metrics are **pre-screening filters**, not affinity predictors
- **Composite scoring is essential** for meaningful ranking

## Quick Reference: All Thresholds

| Category | Metric | Standard | Stringent |
|----------|--------|----------|-----------|
| **Structural** | pLDDT | > 0.85 | > 0.90 |
| | pTM | > 0.70 | > 0.80 |
| | scRMSD | < 2.0 Å | < 1.5 Å |
| **Binding** | ipTM | > 0.50 | > 0.60 |
| | PAE_interaction | < 12 Å | < 10 Å |
| | interface_dG | < -10 | < -15 |
| **Expression** | Instability | < 40 | < 30 |
| | GRAVY | < 0.4 | < 0.2 |
| | ESM2 PLL | > 0.0 | > 0.2 |

## Design-Level Checks

| Pattern | Risk | Action |
|---------|------|--------|
| Odd cysteine count | Unpaired disulfides | Redesign |
| NG/NS/NT motifs | Deamidation | Flag/avoid |
| K/R ≥ 3 consecutive | Proteolysis | Flag |
| ≥ 6 hydrophobic run | Aggregation | Redesign |

## Sequential Filtering Pipeline

```python
import pandas as pd

designs = pd.read_csv('designs.csv')

# Stage 1: Structural confidence
designs = designs[designs['pLDDT'] > 0.85]

# Stage 2: Self-consistency
designs = designs[designs['scRMSD'] < 2.0]

# Stage 3: Binding quality
designs = designs[(designs['ipTM'] > 0.5) & (designs['PAE_interaction'] < 10)]

# Stage 4: Sequence plausibility
designs = designs[designs['esm2_pll_normalized'] > 0.0]

# Stage 5: Expression checks
designs = designs[designs['cysteine_count'] % 2 == 0]
designs = designs[designs['instability_index'] < 40]
```

## Composite Scoring

```python
def composite_score(row):
    return (
        0.30 * row['pLDDT'] +
        0.20 * row['ipTM'] +
        0.20 * (1 - row['PAE_interaction'] / 20) +
        0.15 * row['shape_complementarity'] +
        0.15 * row['esm2_pll_normalized']
    )

designs['score'] = designs.apply(composite_score, axis=1)
top_designs = designs.nlargest(100, 'score')
```

## Metric AUC Comparison

| Metric | AUC |
|--------|-----|
| ipTM | ~0.64 |
| PAE | ~0.65 |
| ESM2 PLL | ~0.72 |
| **Composite** | **~0.75+** |

## Campaign Health

| Pass Rate | Status |
|-----------|--------|
| > 15% | Excellent |
| 10-15% | Good |
| 5-10% | Marginal |
| < 5% | Poor — diagnose |

## Failure Recovery

**Low pLDDT (< 5% passing)**:
- Regenerate backbones with `noise_scale=0.5-0.8`
- Use SolubleMPNN instead of ProteinMPNN
- Try BindCraft (integrated design)

**Low ipTM (< 5% passing)**:
- Review hotspot selection (surface-exposed, conserved)
- Increase binder length (more contact area)
- Try BoltzGen for all-atom precision

**High scRMSD (> 50%)**:
- Lower ProteinMPNN temperature to 0.1
- Increase sequences per backbone to 32
- Regenerate backbones with lower noise_scale
