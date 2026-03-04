---
name: cell-free-expression
description: >
  Guidance for cell-free protein synthesis (CFPS) optimization. Use when:
  (1) Planning CFPS experiments,
  (2) Troubleshooting low yield or aggregation,
  (3) Optimizing DNA template design for CFPS,
  (4) Expressing difficult proteins (disulfide-rich, toxic, membrane).
license: MIT
category: experimental
tags: [expression, cfps, validation]
source: https://github.com/adaptyvbio/protein-design-skills
---

# Cell-Free Protein Synthesis (CFPS)

## System Selection Guide

| System | Best For | Yield | Disulfides | Cost |
|--------|----------|-------|------------|------|
| E. coli extract | Rapid prototyping | 100-400 μg/mL | Poor | Low |
| E. coli PURE | Defined, unnatural AAs | 50-150 μg/mL | Controllable | High |
| Wheat germ | Eukaryotic proteins | 100-500 μg/mL | Moderate | Medium |
| Rabbit reticulocyte | Mammalian proteins | 10-50 μg/mL | Poor | High |
| HeLa/CHO | Native mammalian | 10-50 μg/mL | Good | Very High |

## Troubleshooting Matrix

| Problem | Design Fix | Reagent Fix |
|---------|------------|-------------|
| No expression | Codon optimize first 30 codons | Use BL21-CodonPlus extract |
| Low yield | Optimize 5' UTR (ΔG > -5 kcal/mol) | Increase Mg²⁺ (10-18 mM) |
| Aggregation | Add solubility tags (MBP, SUMO) | Add 0.1% Tween-20, chaperones |
| Inactive protein | Slow translation (use rare codons!) | Add GroEL/ES, DnaK/J |
| Truncation | Remove AGG/AGA/CUA clusters | Supplement rare tRNAs |

## Codon Optimization Rules

### Codons to avoid in E. coli CFPS

| Codon | AA | Issue |
|-------|----|----|
| AGG | Arg | Very rare, stalling |
| AGA | Arg | Very rare, stalling |
| CUA | Leu | Low abundance |

### Design Rules
1. First 30 codons: Use only high-frequency codons
2. Rare codon content: Keep <5% of coding sequence
3. GC content: Target 40-60%
4. No >6 consecutive G or C residues
5. **Strategic slow codons**: Place at domain boundaries for folding!

## Expression Prediction

| Feature | Good | Marginal | Bad |
|---------|------|----------|-----|
| Rare codon content | <3% | 3-8% | >10% |
| First 30 codons rare | 0 | 1-2 | >2 |
| GC content | 45-55% | 35-45% | <30% or >70% |
| 5' UTR ΔG | > -3 kcal/mol | -3 to -8 | < -10 kcal/mol |
| Cysteine count | Even | Mixed | Odd |

## Solubility Tags

| Tag | Size | Enhancement | Notes |
|-----|------|-------------|-------|
| MBP | 40 kDa | Excellent | Best overall |
| SUMO | 11 kDa | Very Good | Native N-terminus after cleavage |
| NusA | 55 kDa | Excellent | Large size |
| Trx | 12 kDa | Good | For disulfide proteins |

## Temperature Optimization

| Temperature | Use Case |
|-------------|----------|
| 37°C | Fast expression, stable proteins |
| 30°C | Balanced (default) |
| 25°C | Disulfide proteins, complex folds |
| 18-20°C | Aggregation-prone proteins |

## Disulfide Bond Formation (E. coli extract)

```
1. Deplete DTT (dialysis or IAM 5 mM)
2. Add 4 mM GSSG + 1 mM GSH (4:1 ratio)
3. Add 10 μM PDI
4. Optional: Add 5 μM DsbC
5. Express at 25°C for 4-6 hours
```

## References

- [User's Guide to CFPS - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6481089/)
- [Codon Influence on Expression - Nature](https://www.nature.com/articles/nature16509)
